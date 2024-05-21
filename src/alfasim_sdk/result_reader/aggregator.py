import functools
import json
import os
from collections import namedtuple
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from typing import Callable
from typing import DefaultDict
from typing import Dict
from typing import Iterator
from typing import List
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import Union

import attr
import h5py
import numpy
import numpy as np
from typing_extensions import Self

from alfasim_sdk.result_reader.aggregator_constants import (
    GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME,
)
from alfasim_sdk.result_reader.aggregator_constants import (
    HISTORY_MATCHING_DETERMINISTIC_DSET_NAME,
)
from alfasim_sdk.result_reader.aggregator_constants import HISTORY_MATCHING_GROUP_NAME
from alfasim_sdk.result_reader.aggregator_constants import (
    HISTORY_MATCHING_PROBABILISTIC_DSET_NAME,
)
from alfasim_sdk.result_reader.aggregator_constants import META_GROUP_NAME
from alfasim_sdk.result_reader.aggregator_constants import PROFILES_GROUP_NAME
from alfasim_sdk.result_reader.aggregator_constants import (
    PROFILES_STATISTICS_DSET_NAME_SUFFIX,
)
from alfasim_sdk.result_reader.aggregator_constants import RESULT_FILE_LOCKING_MODE
from alfasim_sdk.result_reader.aggregator_constants import RESULT_FILE_PREFIX
from alfasim_sdk.result_reader.aggregator_constants import TIME_SET_DSET_NAME
from alfasim_sdk.result_reader.aggregator_constants import TRENDS_GROUP_NAME

OutputKeyType = str
"""\
A output key is a tuple with the output id and the property id.
"""

TimeSetKeyType = Tuple[int, ...]
"""\
A time set key is a tuple of the base time steps relevant for a time set (in ascending order).

The "base time step"s are the time steps for which are global metadata folders.
"""

SourceTimeSetKeyType = Tuple[str, TimeSetKeyType]
"""\
A source time set key is a tuple containing:
    - a source identifier, the output's type that caused this time set to emerge (trend/profile);
    - a list of "base time step"s of relevance;
"""

TimeSetType = List[float]
"""\
A time set is just a list o floats (the time steps in this time set).
"""

DeltaTsType = List[float]
"""\
A list of floats representing Δt's.
"""


BaseTimeStepIndexToMetaList = Dict[int, Dict]
"""\
A map of base time steps to the metadata contained in the respective result file.

All the metadata will represents the same kind of output (profiles/trends).
"""

HistoryMatchingResultKeyType = str
"""\
A HM result key is simply the id of the parametric var associated with that particular result.
"""

TimeSetInfoItem = namedtuple("TimeSetInfoItem", "global_start size uuid")
TimeSetInfo = Dict[int, TimeSetInfoItem]


_PROFILE_ID_ATTR = "profile_id"
_TREND_ID_ATTR = "trend_id"
_SOURCE_ID_TO_GROUP_NAME = {
    _PROFILE_ID_ATTR: PROFILES_GROUP_NAME,
    _TREND_ID_ATTR: TRENDS_GROUP_NAME,
}


class ResultsNeedFullReloadError(RuntimeError):
    """
    This error is raised by ``read_metadata`` when using
    ``previous_time_set_info`` parameter and a result truncation is detected.

    The result is truncated when the simulation has been started using a
    "restart file" and the option "keep old results" is selected.
    """


@attr.s(slots=True, hash=False)
class GlobalSensitivityAnalysisMetadata:
    """
    A class that hold the global sensitivity analysis metadata.
    """

    @attr.s(slots=True, hash=False)
    class GSAItem:
        """
        A class that hold each global sensitivity analysis
        metadata information.
        :ivar property_id:
            The property name (holdup, total mass flow rate).
        :ivar trend_id:
            The id associated a specific trend.
        :ivar category:
            The property category. For global sensitivity analysis
            this always be dimensionless.
        :ivar parametric_var_id:
            The id associated a parametric variable.
        :ivar parametric_var_name:
            The name associated a parametric variable.
        :ivar network_element_name:
            The name of network where this data is associated.
        :ivar position:
            The element position in a pipe.
        :ivar position_unit:
            The position unit (m, Km, cm).
        :ivar unit:
            The unit of a dimensionless property (-, %)
        :ivar qoi_index:
            The index of a quantity of interest in the results file.
        :ivar qoi_data_index:
            The data index of a quantity of interest.
        """

        property_id: str = attr.ib(validator=attr.validators.instance_of(str))
        trend_id: str = attr.ib(validator=attr.validators.instance_of(str))
        category: str = attr.ib(validator=attr.validators.instance_of(str))
        parametric_var_id: str = attr.ib(validator=attr.validators.instance_of(str))
        parametric_var_name: str = attr.ib(validator=attr.validators.instance_of(str))
        network_element_name: Optional[str] = attr.ib(
            validator=attr.validators.optional(attr.validators.instance_of(str))
        )
        position: Optional[float] = attr.ib(
            validator=attr.validators.optional(attr.validators.instance_of(float))
        )
        position_unit: Optional[str] = attr.ib(
            validator=attr.validators.optional(attr.validators.instance_of(str))
        )
        unit: str = attr.ib(validator=attr.validators.instance_of(str))
        qoi_index: Optional[int] = attr.ib(
            validator=attr.validators.optional(attr.validators.instance_of(int))
        )
        qoi_data_index: Optional[int] = attr.ib(
            validator=attr.validators.optional(attr.validators.instance_of(int))
        )

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> Self:
            return cls(
                property_id=data["property_id"],
                trend_id=data["trend_id"],
                category=data["category"],
                parametric_var_id=data["parametric_var_id"],
                parametric_var_name=data["parametric_var_name"],
                network_element_name=data["network_element_name"],
                position=data["position"],
                position_unit=data["position_unit"],
                unit=data["unit"],
                qoi_index=data["qoi_index"],
                qoi_data_index=data["qoi_data_index"],
            )

    gsa_items: Dict[str, GSAItem] = attr.ib(validator=attr.validators.instance_of(Dict))
    result_directory: Path = attr.ib(validator=attr.validators.instance_of(Path))

    @classmethod
    def empty(cls, result_directory: Path) -> Self:
        return GlobalSensitivityAnalysisMetadata(
            gsa_items={}, result_directory=result_directory
        )

    @classmethod
    def get_metadata_from_dir(cls, result_directory: Path) -> Self:
        """
        Return the metadata info from result directory.
        If the directory does not exist/is invalid, return an empty metadata.
        :param result_directory:
            The directory result.
        """

        def map_data(
            gsa_metadata: Dict,
        ) -> Dict[str, GlobalSensitivityAnalysisMetadata.GSAItem]:
            return {
                key: GlobalSensitivityAnalysisMetadata.GSAItem.from_dict(data)
                for key, data in gsa_metadata.items()
            }

        with open_result_file(
            result_directory, result_filename="result"
        ) as result_file:
            if not result_file:
                return cls.empty(result_directory=result_directory)

            loaded_metadata = json.loads(
                result_file[META_GROUP_NAME].attrs["global_sensitivity_analysis"]
            )
            return cls(
                gsa_items=map_data(loaded_metadata), result_directory=result_directory
            )


@attr.s(slots=True, hash=False)
class HistoryMatchingMetadata:
    """
    Holder for the History Matching results metadata.

    :ivar hm_items:
        Map of the data id and its associated metadata.
    :ivar objective_functions:
        Map of observed curve id to a dict of Quantity of Interest data, populated with keys
        'trend_id' and 'property_id'. This represents the setup for this HM analysis.
    :ivar parametric_vars:
        Map of parametric vars to the values that represents the analysis, with all existent vars.
        Values are either the optimal values (deterministic) or the base values (probabilistic).
    :ivar result_directory:
        The directory in which the result is saved.
    """

    @attr.s(slots=True, hash=False)
    class HMItem:
        """
        Metadata associated with each item of the HM results.

        :ivar parametric_var_id:
            The id of the associated parametric var.
        :ivar parametric_var_name:
            The name of the associated parametric var.
        :ivar min_value:
            Lower limit of the specified range for the parametric var.
        :ivar max_value:
            Upper limit of the specified range for the parametric var.
        :ivar data_index:
            The index of the data in the result datasets.
        """

        parametric_var_id: str = attr.ib(validator=attr.validators.instance_of(str))
        parametric_var_name: str = attr.ib(validator=attr.validators.instance_of(str))
        min_value: float = attr.ib(validator=attr.validators.instance_of(float))
        max_value: float = attr.ib(validator=attr.validators.instance_of(float))
        data_index: int = attr.ib(validator=attr.validators.instance_of(int))

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> Self:
            """
            Parse a dict into a HM item.

            :raises: KeyError if some expected key is not present in the given data dict.
            """
            return cls(
                parametric_var_name=data["parametric_var_name"],
                parametric_var_id=data["parametric_var_id"],
                min_value=data["min_value"],
                max_value=data["max_value"],
                data_index=data["data_index"],
            )

    hm_items: Dict[str, HMItem] = attr.ib(validator=attr.validators.instance_of(Dict))
    objective_functions: Dict[str, Dict[str, str]] = attr.ib(
        validator=attr.validators.instance_of(Dict)
    )
    parametric_vars: Dict[str, float] = attr.ib(
        validator=attr.validators.instance_of(Dict)
    )
    result_directory: Path = attr.ib(validator=attr.validators.instance_of(Path))

    @classmethod
    def empty(cls, result_directory: Path) -> Self:
        return cls(
            hm_items={},
            objective_functions={},
            parametric_vars={},
            result_directory=result_directory,
        )

    @classmethod
    def from_result_directory(cls, result_directory: Path) -> Self:
        """
        Read History Matching results metadata from result directory/file.

        If result file is not ready or doesn't exist, return an empty metadata.
        """

        def map_data(hm_metadata: Dict) -> Dict[str, HistoryMatchingMetadata.HMItem]:
            return {
                key: HistoryMatchingMetadata.HMItem.from_dict(data)
                for key, data in hm_metadata.items()
            }

        with open_result_file(result_directory) as result_file:
            if not result_file:
                return cls.empty(result_directory=result_directory)

            loaded_metadata = json.loads(
                result_file[META_GROUP_NAME].attrs[HISTORY_MATCHING_GROUP_NAME]
            )

            if len(loaded_metadata) == 0:
                return cls.empty(result_directory=result_directory)

            some_item_metadata = list(loaded_metadata.values())[0]

            objective_functions = some_item_metadata["objective_functions"]
            parametric_vars = some_item_metadata["parametric_vars"]

            return cls(
                hm_items=map_data(loaded_metadata),
                objective_functions=objective_functions,
                parametric_vars=parametric_vars,
                result_directory=result_directory,
            )


@attr.s(slots=True, hash=False)
class ALFASimResultMetadata:
    """
    :ivar profiles:
        Map output keys (profile id and property id) to metadata entries.

    :ivar trends:
        Map output keys (trend id and property id) to metadata entries.

    :ivar time_sets:
        Map sourced time set keys (tuples of relevant base time sets) to a list
        of list of the time step values.

    :ivar time_sets_unit:
        The unit used by all time sets.

    :ivar time_steps_boundaries:
        The time step boundaries index where this metadata object is relevant.
        The first item is the starting time step index (including) and the second
        is the ending time step index (excluding).

    :ivar time_set_info:
        Map output type to maps of base time steps to `TimeSetInfoItem`.

    :ivar result_directory:
        The path where this data has been read.

    :ivar app_version_info:
        Map "base time steps" to the application version used in the simulation.
    """

    profiles = attr.ib(validator=attr.validators.instance_of(dict))
    trends = attr.ib(validator=attr.validators.instance_of(dict))
    time_sets = attr.ib(validator=attr.validators.instance_of(list))
    time_sets_unit = attr.ib(validator=attr.validators.instance_of(str))
    time_steps_boundaries = attr.ib(validator=attr.validators.instance_of(tuple))
    time_set_info = attr.ib(validator=attr.validators.instance_of(dict))
    result_directory = attr.ib(validator=attr.validators.instance_of(Path))
    app_version_info = attr.ib(validator=attr.validators.instance_of(dict))

    @property
    def trends_time_steps_boundaries(self) -> Tuple[int, int]:
        """
        Return a tuple with the initial and final time step boundaries for trends.
        """
        trends_index = 1
        time_steps_boundaries = self.time_steps_boundaries
        return (
            time_steps_boundaries[0][trends_index],
            time_steps_boundaries[1][trends_index],
        )

    @property
    def profile_time_steps_boundaries(self) -> Tuple[int, int]:
        """
        Return a tuple with the initial and final time step boundaries for profiles.
        """
        profiles_index = 0
        time_steps_boundaries = self.time_steps_boundaries
        return (
            time_steps_boundaries[0][profiles_index],
            time_steps_boundaries[1][profiles_index],
        )


@attr.s(slots=True, hash=False)
class _MergedMetadataWithStatistics:
    """
    :ivar app_version_info:
        Map "base time steps" to the application version used in the simulation.

    :ivar profile_key_to_metadata:
        Map output keys (profile id and property id) to metadata entries.

    :ivar trend_key_to_metadata:
        Map output keys (trend id and property id) to metadata entries.

    :ivar time_set_keys:
        List of sourced time set keys (tuples of relevant base time sets).
    """

    app_version_info = attr.ib(validator=attr.validators.instance_of(dict))
    profile_key_to_metadata = attr.ib(validator=attr.validators.instance_of(dict))
    trend_key_to_metadata = attr.ib(validator=attr.validators.instance_of(dict))
    time_set_keys = attr.ib(validator=attr.validators.instance_of(list))


@contextmanager
def open_result_files(result_directory: Path) -> Dict[int, h5py.File]:
    """
    Return a dict with the result files.

    Note that once the container dict is collected the files originally returned are closed.
    """
    # When a new result file is created its metadata contents are not complete, and the file
    # has not been put into SWMR mode yet (SWMR mode does not allow new groups, attributes,
    # and/or data sets to be created).
    # Since it is not possible to open files in SWMR mode for reading if a writer is not
    # present fall back to open files from former runs in normal read mode.
    # Since a new file (with incomplete metadata) is open by the writer in normal mode we
    # need avoid reading that incomplete file.
    # To avoid race conditions a file `<result_file_name>.creating` is create in the same
    # folder before the actual result file is created. After the metadata is writen and the
    # writer enters SWMR mode the `<result_file_name>.creating` is removed to signal readers
    # that is safe to read that file.
    files = set(result_directory.glob(RESULT_FILE_PREFIX + "*"))
    result_files = set()
    files_under_creation = set()
    for f in files:
        ext = f.suffix
        if ext == ".creating":
            # Take note of any file to ignore.
            name, _ = os.path.splitext(f)
            files_under_creation.add(Path(name))
        elif ext == "":
            result_files.add(f)
        else:
            raise ValueError(f"Unknown ext: {ext}")

    prefix_len = len(RESULT_FILE_PREFIX)
    result_files.difference_update(files_under_creation)  # Ignore incomplete files.
    result_files_sorted = (
        (int(filename.name[prefix_len:]), _open_result_file(filename))
        for filename in result_files
    )
    result_files_sorted_dict = dict(sorted(result_files_sorted, key=lambda x: x[0]))

    try:
        yield result_files_sorted_dict
    finally:
        for f in result_files_sorted_dict.values():
            f.close()


def _open_result_file(filename: Path) -> h5py.File:
    h5py_file = h5py.File
    if h5py.version.version_tuple[:2] >= (3, 5):
        h5py_file = functools.partial(h5py.File, locking=RESULT_FILE_LOCKING_MODE)

    # The lib h5py will fail to open the file for some exotic paths,
    # but will work if the cwd are such paths.
    directory = filename.parent
    old_directory = os.getcwd()
    try:
        os.chdir(directory)
        try:
            return h5py_file(filename.name, "r", libver="latest", swmr=True)
        except OSError as os_error:
            swmr_message = (
                "Unable to open file (file is not already open for SWMR writing)"
            )
            if str(os_error) == swmr_message:
                return h5py_file(filename.name, "r", libver="latest", swmr=False)
            raise

    except PermissionError:
        raise PermissionError(
            f"Could not access folder {filename}.\n"
            f'If you are using your local "Downloads" directory, consider changing the project file\n'
            f"to somewhere else as some services try to synchronize that directory and interfere with\n"
            f"the simulation.\n"
            "\n"
            f'1 - Click in "Save as".\n'
            f"2 - Select a different path, outside Download folder.\n"
            f"3 - Run simulation again.\n"
        )
    finally:
        os.chdir(old_directory)


def _get_number_of_base_time_steps_from_time_set_info(
    time_set_info_source_dict: Dict,
) -> int:
    from itertools import chain

    expected_number_of_base_ts = chain.from_iterable(
        time_set_info.keys() for time_set_info in time_set_info_source_dict.values()
    )
    return len(set(expected_number_of_base_ts))


def _get_empty_result(
    profile_index: int = 0,
    trend_index: int = 0,
    *,
    result_directory: Path,
    previous_time_set_info: Optional[Dict] = None,
) -> ALFASimResultMetadata:
    """
    Create an empty `ALFASimResultMetadata` object with the expected time step boundaries.
    """
    return ALFASimResultMetadata(
        profiles={},
        trends={},
        time_sets=[],
        time_sets_unit="",
        time_steps_boundaries=(
            (profile_index, trend_index),
            (profile_index, trend_index),
        ),
        time_set_info=previous_time_set_info,
        result_directory=result_directory,
        app_version_info={},
    )


def read_metadata(
    result_directory: Path,
    *,
    initial_profiles_time_step_index: Optional[int] = None,
    final_profiles_time_step_index: Optional[int] = None,
    initial_trends_time_step_index: Optional[int] = None,
    final_trends_time_step_index: Optional[int] = None,
    previous_time_set_info: Optional[Dict] = None,
) -> ALFASimResultMetadata:
    """
    Read all meta data for the given range.
    The range boundaries defaults are the begin and end of the simulation.

    :param initial_profiles_time_step_index:
        The profile global time step index where to start collecting metadata.
        If not supplied on `None` then `0` is used.

    :param final_profiles_time_step_index:
        The profile global time step index after the last to have its metadata
        collected. If not supplied or `None` all the available time steps after
        `initial_profiles_time_step_index`  are collected.

    :param initial_trends_time_step_index:
        The trend global time step index where to start collecting metadata.
        If not supplied on `None` then `0` is used.

    :param final_trends_time_step_index:
        The trend global time step index after the last to have its metadata
        collected. If not supplied or `None` all the available time steps after
        `initial_trends_time_step_index` are collected.

    :param previous_time_set_info:
        The `time_set_info` from the previous metadata (when progressively reading).
        If omitted a time set truncation is not detected. This is only relevant
        when progressive reading is used (..see: `ConcatenateMetadata`).
    """
    if previous_time_set_info is None:
        previous_time_set_info = {}

    if not result_directory.is_dir():
        return _get_empty_result(
            result_directory=result_directory,
            previous_time_set_info=previous_time_set_info,
        )

    with open_result_files(result_directory) as result_files:
        if len(result_files) == 0:
            return _get_empty_result(
                result_directory=result_directory,
                previous_time_set_info=previous_time_set_info,
            )
        else:
            return _read_metadata(
                result_directory,
                initial_profiles_time_step_index=initial_profiles_time_step_index,
                final_profiles_time_step_index=final_profiles_time_step_index,
                initial_trends_time_step_index=initial_trends_time_step_index,
                final_trends_time_step_index=final_trends_time_step_index,
                previous_time_set_info=previous_time_set_info,
                result_files=result_files,
            )


def _read_metadata(
    result_directory: Path,
    *,
    initial_profiles_time_step_index: Optional[int] = None,
    final_profiles_time_step_index: Optional[int] = None,
    initial_trends_time_step_index: Optional[int] = None,
    final_trends_time_step_index: Optional[int] = None,
    previous_time_set_info: Optional[Dict] = None,
    result_files: Dict[int, h5py.File],
) -> ALFASimResultMetadata:
    """
    See `read_metadata`.
    """
    expected_number_of_base_ts = _get_number_of_base_time_steps_from_time_set_info(
        previous_time_set_info
    )
    if (expected_number_of_base_ts > 0) and (
        len(result_files) != expected_number_of_base_ts
    ):
        raise ResultsNeedFullReloadError(
            f"Different number of result files: {len(result_files)} but expecting {expected_number_of_base_ts}"
        )

    global_profiles_metadata, global_trends_metadata = _read_global_metadata(
        result_files
    )

    def normalize_time_step_index(n: int, total_size: int, *, default: int):
        if n is None:
            return default
        if n < 0:
            return total_size + n
        return n

    profiles_time_set_info = read_time_set_info(result_files, PROFILES_GROUP_NAME)
    time_set_info_item = list(profiles_time_set_info.values())[-1]
    total_profiles_time_set_size = (
        time_set_info_item.global_start + time_set_info_item.size
    )
    initial_profiles_time_step_index = normalize_time_step_index(
        initial_profiles_time_step_index, total_profiles_time_set_size, default=0
    )
    assert initial_profiles_time_step_index is not None
    final_profiles_time_step_index = normalize_time_step_index(
        final_profiles_time_step_index,
        total_profiles_time_set_size,
        default=total_profiles_time_set_size,
    )
    assert final_profiles_time_step_index is not None

    trends_time_set_info = read_time_set_info(result_files, TRENDS_GROUP_NAME)
    time_set_info_item = list(trends_time_set_info.values())[-1]
    total_trends_time_set_size = (
        time_set_info_item.global_start + time_set_info_item.size
    )
    initial_trends_time_step_index = normalize_time_step_index(
        initial_trends_time_step_index, total_trends_time_set_size, default=0
    )
    assert initial_trends_time_step_index is not None
    final_trends_time_step_index = normalize_time_step_index(
        final_trends_time_step_index,
        total_trends_time_set_size,
        default=total_trends_time_set_size,
    )
    assert final_trends_time_step_index is not None

    def check_time_set_info_for_truncation(old: TimeSetInfo, new: TimeSetInfo) -> None:
        if set(old) - set(new):
            raise ResultsNeedFullReloadError("Time set truncated")
        for base_ts, new_value in new.items():
            old_value = old.get(base_ts)
            if old_value and (old_value.uuid != new_value.uuid):
                raise ResultsNeedFullReloadError("Time set truncated")

    check_time_set_info_for_truncation(
        previous_time_set_info.get(PROFILES_GROUP_NAME, {}), profiles_time_set_info
    )
    check_time_set_info_for_truncation(
        previous_time_set_info.get(TRENDS_GROUP_NAME, {}), trends_time_set_info
    )

    if (final_profiles_time_step_index == initial_profiles_time_step_index) and (
        final_trends_time_step_index == initial_trends_time_step_index
    ):
        return _get_empty_result(
            initial_profiles_time_step_index,
            initial_trends_time_step_index,
            result_directory=result_directory,
            previous_time_set_info=previous_time_set_info,
        )

    if initial_profiles_time_step_index != final_profiles_time_step_index:
        if not (0 <= initial_profiles_time_step_index < total_profiles_time_set_size):
            raise IndexError(
                f"`initial_profiles_time_step_index` ({initial_profiles_time_step_index}) outside of valid range: [0, {total_profiles_time_set_size - 1}]"
            )
        if not (0 <= final_profiles_time_step_index <= total_profiles_time_set_size):
            raise IndexError(
                f"`final_profiles_time_step_index` ({final_profiles_time_step_index}) outside of valid range: [0, {total_profiles_time_set_size}]"
            )

    if initial_trends_time_step_index != final_trends_time_step_index:
        if not (0 <= initial_trends_time_step_index < total_trends_time_set_size):
            raise IndexError(
                f"`initial_trends_time_step_index` ({initial_trends_time_step_index}) outside of valid range: [0, {total_trends_time_set_size - 1}]"
            )
        if not (0 <= final_trends_time_step_index <= total_trends_time_set_size):
            raise IndexError(
                f"`final_trends_time_step_index` ({final_trends_time_step_index}) outside of valid range: [0, {total_trends_time_set_size}]"
            )

    merged_metadata = _merge_metadata_and_read_global_statistics(
        result_files,
        global_profiles_metadata,
        profiles_time_set_info,
        global_trends_metadata,
        trends_time_set_info,
        initial_profiles_time_step_index,
        final_profiles_time_step_index,
        initial_trends_time_step_index,
        final_trends_time_step_index,
    )

    result_metadata = ALFASimResultMetadata(
        profiles=merged_metadata.profile_key_to_metadata,
        trends=merged_metadata.trend_key_to_metadata,
        time_sets=merged_metadata.time_set_keys,
        time_sets_unit="s",
        time_steps_boundaries=(
            (initial_profiles_time_step_index, initial_trends_time_step_index),
            (final_profiles_time_step_index, final_trends_time_step_index),
        ),
        time_set_info={
            PROFILES_GROUP_NAME: profiles_time_set_info,
            TRENDS_GROUP_NAME: trends_time_set_info,
        },
        result_directory=result_directory,
        app_version_info=merged_metadata.app_version_info,
    )
    return result_metadata


def read_time_set_info(
    result_files: Dict[int, h5py.File], container_group_name: str
) -> TimeSetInfo:
    """
    :return:
        A dict mapping a result file to the index of the first time step and number of time
        steps stored.
    """
    from bisect import bisect_left

    from boltons.iterutils import pairwise_iter

    time_set_info = {}
    start = 0
    TimeSetLimits = namedtuple("TimeSetLimits", ("first", "last", "values"))
    limits = {}

    for key, file in result_files.items():
        dataset = file[container_group_name][TIME_SET_DSET_NAME]
        time_set_uuid = file[META_GROUP_NAME].attrs.get(
            "time_set_uuid", default="<NO UUID>"
        )
        size = dataset.size
        if size > 0:
            limits[key] = TimeSetLimits(dataset[0], dataset[-1], dataset)
        time_set_info[key] = TimeSetInfoItem(
            global_start=start, size=size, uuid=time_set_uuid
        )
        start += size

    # Restart with former results may need to adjust the time set infos for correct reading
    for (previous_key, previous_data), (next_key, next_data) in pairwise_iter(
        limits.items()
    ):
        if next_data.first <= previous_data.last:
            index = bisect_left(previous_data.values, next_data.first)

            previous_old_info = time_set_info[previous_key]
            previous_new_uuid = f"{previous_old_info.uuid}-trunc-at-{index}"
            time_set_info[previous_key] = TimeSetInfoItem(
                global_start=previous_old_info.global_start,
                size=index,
                uuid=previous_new_uuid,
            )

            next_old_info = time_set_info[next_key]
            new_start = previous_old_info.global_start + index
            next_new_uuid = f"{next_old_info.uuid}-trunc-prev-at-{index}"
            time_set_info[next_key] = TimeSetInfoItem(
                global_start=new_start,
                size=next_old_info.size,
                uuid=next_new_uuid,
            )

    return time_set_info


def _global_index_to_file_based_index(
    index: int, time_set_start: int, time_set_size: int
) -> int:
    """
    Converts a global index into an index suitable to extract the data from a result file.

    :param index:
        The Global index.

    :param time_set_start:
        The starting global index of the time set stored in the file.

    :param time_set_size:
        The number of time steps stored in the file.

    :return:
        The equivalent index to use when indexing the data stored in the file.
    """
    if index <= time_set_start:
        return 0
    elif index >= (time_set_start + time_set_size):
        return time_set_size
    else:
        return index - time_set_start


def _merge_metadata_and_read_global_statistics(
    result_files: Dict[int, h5py.File],
    global_profiles_metadata: Dict[int, Dict],
    profiles_time_set_info: Dict[int, Tuple[int, int]],
    global_trends_metadata: Dict[int, Dict],
    trends_time_set_info: Dict[int, Tuple[int, int]],
    initial_profiles_time_step_index: int,
    final_profiles_time_step_index: int,
    initial_trends_time_step_index: int,
    final_trends_time_step_index: int,
) -> _MergedMetadataWithStatistics:
    """
    Read the per time step statistics for the given range.
    """
    from collections import defaultdict

    skip_sentinel = object()

    # Setup "helpers".
    @attr.s
    class Helper:
        meta = attr.ib(default=attr.Factory(dict), init=False)  # type: Dict
        output_type_name = attr.ib(validator=attr.validators.instance_of(str))

    profiles_helper = Helper(output_type_name="profile_id")
    trends_helper = Helper(output_type_name="trend_id")

    profiles_to_time_set_key = map_output_key_to_time_set_key(global_profiles_metadata)
    profiles_base_ts_to_time_set_keys = map_base_time_set_to_time_set_keys(
        profiles_to_time_set_key
    )

    trends_to_time_set_key = map_output_key_to_time_set_key(global_trends_metadata)
    trends_base_ts_to_time_set_keys = map_base_time_set_to_time_set_keys(
        trends_to_time_set_key
    )

    time_set_info = {
        PROFILES_GROUP_NAME: profiles_time_set_info,
        TRENDS_GROUP_NAME: trends_time_set_info,
    }
    time_step_index_range_to_read = {
        PROFILES_GROUP_NAME: (
            initial_profiles_time_step_index,
            final_profiles_time_step_index,
        ),
        TRENDS_GROUP_NAME: (
            initial_trends_time_step_index,
            final_trends_time_step_index,
        ),
    }

    time_set_ranges: Dict[SourceTimeSetKeyType, List[Tuple[int, int]]] = {}
    global_profiles_statistics: DefaultDict[int, Dict[str, float]] = defaultdict(
        lambda: {"global_max": numpy.nan, "global_min": numpy.nan}
    )
    trends_statistics: DefaultDict[int, Dict[str, float]] = defaultdict(
        lambda: {"max": numpy.nan, "min": numpy.nan}
    )

    def read_profiles_statistics(ts_index: int) -> None:
        f = result_files[ts_index]
        profile_group = f[PROFILES_GROUP_NAME]

        for output_id, meta in global_profiles_metadata[ts_index].items():
            source_time_set_key = "profile_id", profiles_to_time_set_key[output_id]
            partial_indices = time_set_ranges[source_time_set_key]
            start_index, stop_index = partial_indices[-1]  # The most recent.

            if start_index == stop_index:
                continue  # pragma: no cover

            statistics_id = meta["data_id"] + PROFILES_STATISTICS_DSET_NAME_SUFFIX
            statistics = global_profiles_statistics[output_id]
            profile_statistics_dset = profile_group[statistics_id]
            if "global_min" in profile_statistics_dset.attrs:
                statistics["global_min"] = numpy.nanmin(  # type:ignore[call-overload]
                    (
                        statistics["global_min"],
                        profile_statistics_dset.attrs["global_min"],
                    )
                )
                statistics["global_max"] = numpy.nanmax(  # type:ignore[call-overload]
                    (
                        statistics["global_max"],
                        profile_statistics_dset.attrs["global_max"],
                    )
                )

    def read_trends_statistics(ts_index: int) -> None:
        f = result_files[ts_index]
        trends_group = f[TRENDS_GROUP_NAME]
        if "trends_statistic" not in trends_group:
            return  # pragma: no cover

        trends_statistic = trends_group["trends_statistic"][:, :]
        for output_id, meta in global_trends_metadata[ts_index].items():
            source_time_set_key = "trend_id", trends_to_time_set_key[output_id]
            partial_indices = time_set_ranges[source_time_set_key]
            start_index, stop_index = partial_indices[-1]  # The most recent.

            if start_index < stop_index:
                statistics = trends_statistics[
                    output_id
                ]  # type: Dict[str, numpy.ndarray]
                data_index = meta["index"]
                min_value, max_value = trends_statistic[:, data_index]
                statistics["min"] = numpy.nanmin((min_value, statistics["min"]))
                statistics["max"] = numpy.nanmax((max_value, statistics["max"]))

    def update_helper(
        helper: Helper,
        ts_index: int,
        global_metadata_dict: Dict[int, Dict],
        base_ts_to_time_set_keys_dict: Dict[int, List[TimeSetKeyType]],
    ) -> Optional[object]:
        """
        Updates the helper. Use/update `global_time_set_indices` from outer scope.
        Merges the index/data_id_domain_id from the various base time set indices into a
        single dict. Also update the time set helper indices returned by the outer function.

        :param helper:
            One of `profiles_helper` or `trends_helper` to be updated.

        :param ts_index:
            The time steps index used. This should be a base time step index.

        :param global_metadata_dict:
            Maps base time step index to a list of metadata items in effect
            (`global_profiles_metadata or `global_trends_metadata`).

        :param base_ts_to_time_set_keys_dict:
            Maps base time step index to a list of affected time step keys
            (this should be a per output type map).

        :return:
            A value indicating if the statistics collection should be skipped
            (skip when return `True`).
        """
        if ts_index not in base_ts_to_time_set_keys_dict:
            return skip_sentinel  # pragma: no cover

        output_type_name = helper.output_type_name
        is_profile = output_type_name == "profile_id"
        output_group_name = PROFILES_GROUP_NAME if is_profile else TRENDS_GROUP_NAME

        time_set_key_list = base_ts_to_time_set_keys_dict[ts_index]
        time_set_info_item = time_set_info[output_group_name][ts_index]
        time_set_start = time_set_info_item.global_start
        time_set_size = time_set_info_item.size
        start_index, stop_index = time_step_index_range_to_read[output_group_name]

        start_index = _global_index_to_file_based_index(
            start_index, time_set_start, time_set_size
        )
        stop_index = _global_index_to_file_based_index(
            stop_index, time_set_start, time_set_size
        )
        if start_index == stop_index:
            return skip_sentinel  # pragma: no cover

        for time_set_key in time_set_key_list:
            source_time_set_key = output_type_name, time_set_key
            if source_time_set_key not in time_set_ranges:
                time_set_ranges[source_time_set_key] = []

            time_set_ranges[source_time_set_key].append((start_index, stop_index))

        output_key_meta_dict = helper.meta
        for output_id, output_meta in global_metadata_dict[ts_index].items():
            if output_id in output_key_meta_dict:
                item_meta = output_key_meta_dict[output_id]
            else:
                item_meta = output_key_meta_dict[output_id] = output_meta.copy()
                if is_profile:
                    item_meta["data_id"] = {}
                    item_meta["domain_id"] = {}
                else:
                    item_meta["index"] = {}
            # Update.
            if is_profile:
                item_meta["data_id"][ts_index] = output_meta["data_id"]
                item_meta["domain_id"][ts_index] = output_meta["domain_id"]
            else:
                item_meta["index"][ts_index] = output_meta["index"]

    app_version_info = {}
    for index, raw_result_file in result_files.items():
        app_version_info[index] = raw_result_file[META_GROUP_NAME].attrs.get(
            "application_version"
        )

        skip = update_helper(
            profiles_helper,
            index,
            global_profiles_metadata,
            profiles_base_ts_to_time_set_keys,
        )
        if skip is not skip_sentinel:
            read_profiles_statistics(index)

        skip = update_helper(
            trends_helper,
            index,
            global_trends_metadata,
            trends_base_ts_to_time_set_keys,
        )
        if skip is not skip_sentinel:
            read_trends_statistics(index)

    # Put collected statistics into metadata.
    for output_key, metadata_item in profiles_helper.meta.items():
        profile_statistics = global_profiles_statistics[output_key]
        metadata_item["time_set_key"] = profiles_to_time_set_key[output_key]
        metadata_item["global_max"] = profile_statistics["global_max"]
        metadata_item["global_min"] = profile_statistics["global_min"]

    for output_key, metadata_item in trends_helper.meta.items():
        trend_statistics = trends_statistics[output_key]
        metadata_item["time_set_key"] = trends_to_time_set_key[output_key]
        metadata_item["max"] = float(trend_statistics["max"])
        metadata_item["min"] = float(trend_statistics["min"])

    return _MergedMetadataWithStatistics(
        app_version_info=app_version_info,
        profile_key_to_metadata=profiles_helper.meta,
        trend_key_to_metadata=trends_helper.meta,
        time_set_keys=list(time_set_ranges.keys()),
    )


def _read_global_metadata(
    result_files: Dict[int, h5py.File],
) -> Tuple[BaseTimeStepIndexToMetaList, BaseTimeStepIndexToMetaList]:
    """
    :return:
        - a dict mapping base time steps to a list of profile metadata items;
        - a dict mapping base time steps to a list of trend metadata items;
    """
    import json

    def update_global_metadata(
        result_file: h5py.File,
        metadata_collection: BaseTimeStepIndexToMetaList,
        base_ts: int,
        output_type: str,
    ) -> None:
        """
        Read a metadata file and add it to a metadata collection.

        :param metadata_collection:
            This collection is changed. The keys are the "base time step index"
            and the values are the metadata from the file (the duplicates have
            been removed and the original index recorded).
        """
        meta = json.loads(result_file[META_GROUP_NAME].attrs[output_type])
        metadata_collection[base_ts] = meta

    all_profiles_meta: BaseTimeStepIndexToMetaList = {}
    all_trends_meta: BaseTimeStepIndexToMetaList = {}
    for base_ts, result_file in result_files.items():
        update_global_metadata(result_file, all_profiles_meta, base_ts, "profiles")
        update_global_metadata(result_file, all_trends_meta, base_ts, "trends")
    return all_profiles_meta, all_trends_meta


def _remap_profile_time_step_index(
    profile_time_set_info: Dict[int, TimeSetInfoItem],
    time_set_key: Tuple[int, ...],
    time_step_index: int,
) -> Tuple[int, int]:
    """
    :return:
        - the result file key;
        - the mapped time step index (the index inside the file);
    """
    if time_step_index >= 0:
        index_counter = 0
        for base_ts in time_set_key:
            time_set_info_item = profile_time_set_info[base_ts]
            know_time_set_size = index_counter + time_set_info_item.size
            if time_step_index < know_time_set_size:
                return base_ts, (time_step_index - index_counter)
            else:
                index_counter = know_time_set_size
    else:
        index_counter = 0
        for base_ts in reversed(time_set_key):
            time_set_info_item = profile_time_set_info[base_ts]
            know_time_set_size = index_counter - time_set_info_item.size
            if time_step_index >= know_time_set_size:
                return base_ts, (time_step_index - know_time_set_size)
            else:
                index_counter = know_time_set_size

    effective_time_set_info = {
        base_ts: profile_time_set_info[base_ts] for base_ts in time_set_key
    }
    raise IndexError(
        "\n- ".join(
            [
                f"Can not locate the profile for time step index {time_step_index}. Time set info {len(effective_time_set_info)}:"
            ]
            + [str(item) for item in effective_time_set_info.items()]
        )
    )


def _read_profile_arrays(
    result_metadata,
    output_keys,
    time_step_index,
    *,
    group_name: str,
    data_attr: str,
    data_id_suffix: str = "",
    slicer: Callable[[int], Any],
) -> Dict[OutputKeyType, Optional[numpy.array]]:
    """
    This is the core implementation of `read_profiles_data`/`read_profiles_domain_data`.
    """
    profiles_metadata = result_metadata.profiles
    profiles_time_set_info = result_metadata.time_set_info[PROFILES_GROUP_NAME]

    with open_result_files(result_metadata.result_directory) as result_files:
        profiles = {}
        for profile_key in output_keys:
            meta = profiles_metadata[profile_key]
            result_key, mapped_time_step_index = _remap_profile_time_step_index(
                profiles_time_set_info, meta["time_set_key"], time_step_index
            )
            f = result_files[result_key]
            profiles_group = f[group_name]
            data_id = meta[data_attr].get(result_key)

            if data_id is None:  # pragma: no cover
                # No data for this property in this file,
                # restart/continue with different output options.
                profiles[profile_key] = None
                continue

            data_id += data_id_suffix
            index = slicer(mapped_time_step_index)
            profiles[profile_key] = profiles_group[data_id].__getitem__(index)

        return profiles


def read_profiles_data(
    result_metadata: ALFASimResultMetadata,
    output_keys: List[OutputKeyType],
    time_step_index: int,
) -> Dict[OutputKeyType, Optional[numpy.array]]:
    """
    :return:
        The data for the profiles listed in `output_keys` for the given
        `time_step_index`, if a profile is not found `None` instead
        a `numpy.array` is mapped.
    """
    return _read_profile_arrays(
        result_metadata,
        output_keys,
        time_step_index,
        group_name=PROFILES_GROUP_NAME,
        data_attr="data_id",
        slicer=lambda index: (index, slice(None)),
    )


def read_profiles_domain_data(
    result_metadata: ALFASimResultMetadata,
    output_keys: List[OutputKeyType],
    time_step_index: int,
) -> Dict[OutputKeyType, Optional[numpy.array]]:
    """
    :return:
        The data for the profiles listed in `output_keys` for the given
        `time_step_index`, if a profile is not found `None` instead
        a `numpy.array` is mapped.
    """
    return _read_profile_arrays(
        result_metadata,
        output_keys,
        time_step_index,
        group_name=META_GROUP_NAME,
        data_attr="domain_id",
        slicer=lambda index: slice(None),
    )


def read_profiles_local_statistics(
    result_metadata: ALFASimResultMetadata,
    output_keys: List[OutputKeyType],
    time_step_index: int,
) -> Dict[OutputKeyType, Optional[numpy.array]]:
    """
    :return:
        The statistics for the profiles listed in `output_keys` for the given
        `time_step_index`, if the profile is not found `None` instead
        a `numpy.array` is mapped.
    """
    return _read_profile_arrays(
        result_metadata,
        output_keys,
        time_step_index,
        group_name=PROFILES_GROUP_NAME,
        data_attr="data_id",
        data_id_suffix=PROFILES_STATISTICS_DSET_NAME_SUFFIX,
        slicer=lambda index: (index, slice(None)),
    )


def read_trends_data(
    result_metadata: ALFASimResultMetadata,
    output_keys: Optional[List[OutputKeyType]] = None,
    initial_trends_time_step_index: Optional[int] = None,
    final_trends_time_step_index: Optional[int] = None,
) -> Dict[OutputKeyType, numpy.array]:
    """
    :param result_metadata:
        The metadata for the results.

    :param output_keys:
        Must be trends output ids. Default to ALL trends found in `result_metadata`.

    :param initial_trends_time_step_index:
        If `None` the initial boundary of the result metadata is used.

    :param final_trends_time_step_index:
        If `None` the final boundary of the result metadata is used.

    :return:
        The data for the trends listed in `output_keys`.
    """
    with open_result_files(result_metadata.result_directory) as result_files:
        return _read_trends_data(
            result_metadata,
            output_keys,
            initial_trends_time_step_index,
            final_trends_time_step_index,
            result_files=result_files,
        )


def _read_trends_data(
    result_metadata: ALFASimResultMetadata,
    output_keys: Optional[List[OutputKeyType]] = None,
    initial_trends_time_step_index: Optional[int] = None,
    final_trends_time_step_index: Optional[int] = None,
    *,
    result_files: Dict[int, h5py.File],
) -> Dict[OutputKeyType, numpy.array]:
    """
    See `read_trends_data`.
    """
    trends_metadata = result_metadata.trends
    trends_dsets = {
        base_ts: f[TRENDS_GROUP_NAME]["trends"] for base_ts, f in result_files.items()
    }

    if output_keys is None:
        output_keys = result_metadata.trends.keys()
    else:
        output_keys = output_keys

    if initial_trends_time_step_index is None:
        initial_trends_time_step_index = result_metadata.time_steps_boundaries[0][1]
    if not (
        result_metadata.time_steps_boundaries[0][1]
        <= initial_trends_time_step_index
        <= result_metadata.time_steps_boundaries[1][1]
    ):
        raise ValueError(
            f"Invalid initial_trends_time_step_index ({initial_trends_time_step_index})"
        )

    if final_trends_time_step_index is None:
        final_trends_time_step_index = result_metadata.time_steps_boundaries[1][1]
    if not (
        result_metadata.time_steps_boundaries[0][1]
        <= final_trends_time_step_index
        <= result_metadata.time_steps_boundaries[1][1]
    ):
        raise ValueError(
            f"Invalid final_trends_time_step_index ({final_trends_time_step_index})"
        )

    try:
        time_set_info = result_metadata.time_set_info[TRENDS_GROUP_NAME]
    except KeyError:
        return {
            trend_key: numpy.empty((0,), dtype=numpy.float64)
            for trend_key in output_keys
        }

    # Read data from files.
    trends = {}
    for trend_key in output_keys:
        trends_entry = trends[trend_key] = []
        meta = trends_metadata[trend_key]

        for base_ts, dset in trends_dsets.items():
            index = meta["index"].get(base_ts)
            if index is not None:
                time_set_info_item = time_set_info[base_ts]
                time_set_start = time_set_info_item.global_start
                time_set_size = time_set_info_item.size
                start_index = _global_index_to_file_based_index(
                    initial_trends_time_step_index, time_set_start, time_set_size
                )
                stop_index = _global_index_to_file_based_index(
                    final_trends_time_step_index, time_set_start, time_set_size
                )
                trend_data = dset[start_index:stop_index, index]
                trends_entry.append(trend_data)

    for trend_key, data_list in trends.items():
        if len(data_list) != 0:
            trends[trend_key] = numpy.concatenate(data_list)
        else:  # pragma: no cover (no data fragments)
            trends[trend_key] = numpy.empty((0,), dtype=numpy.float64)

    return trends


def read_time_sets(
    result_metadata: ALFASimResultMetadata,
    time_sets_key_list: Optional[List[SourceTimeSetKeyType]] = None,
    initial_profiles_time_step_index: Optional[int] = None,
    final_profiles_time_step_index: Optional[int] = None,
    initial_trends_time_step_index: Optional[int] = None,
    final_trends_time_step_index: Optional[int] = None,
) -> Dict[SourceTimeSetKeyType, numpy.array]:
    """
    :param result_metadata:
        The metadata for the results.

    :param time_sets_key_list:
        Default to ALL time sets found in `result_metadata`.

    :param initial_profiles_time_step_index:
        If `None` the initial boundary of the result metadata is used.

    :param final_profiles_time_step_index:
        If `None` the final boundary of the result metadata is used.

    :param initial_trends_time_step_index:
        If `None` the initial boundary of the result metadata is used.

    :param final_trends_time_step_index:
        If `None` the final boundary of the result metadata is used.

    :return:
        The data for the time sets listed in `time_sets_key_list`.
    """
    with open_result_files(result_metadata.result_directory) as result_files:
        return _read_time_sets(
            result_metadata,
            time_sets_key_list,
            initial_profiles_time_step_index,
            final_profiles_time_step_index,
            initial_trends_time_step_index,
            final_trends_time_step_index,
            result_files=result_files,
        )


def _read_time_sets(
    result_metadata: ALFASimResultMetadata,
    time_sets_key_list: Optional[List[SourceTimeSetKeyType]] = None,
    initial_profiles_time_step_index: Optional[int] = None,
    final_profiles_time_step_index: Optional[int] = None,
    initial_trends_time_step_index: Optional[int] = None,
    final_trends_time_step_index: Optional[int] = None,
    *,
    result_files: Dict[int, h5py.File],
) -> Dict[SourceTimeSetKeyType, numpy.array]:
    """
    See `read_time_sets`.
    """
    if time_sets_key_list is None:
        time_sets_key_list = result_metadata.time_sets

    dsets_by_source_id = {}

    time_step_index_range_to_read = {
        _PROFILE_ID_ATTR: [
            initial_profiles_time_step_index,
            final_profiles_time_step_index,
        ],
        _TREND_ID_ATTR: [initial_trends_time_step_index, final_trends_time_step_index],
    }
    if initial_profiles_time_step_index is None:
        time_step_index_range_to_read[_PROFILE_ID_ATTR][
            0
        ] = result_metadata.time_steps_boundaries[0][0]
    if final_profiles_time_step_index is None:
        time_step_index_range_to_read[_PROFILE_ID_ATTR][
            1
        ] = result_metadata.time_steps_boundaries[1][0]
    if initial_trends_time_step_index is None:
        time_step_index_range_to_read[_TREND_ID_ATTR][
            0
        ] = result_metadata.time_steps_boundaries[0][1]
    if final_trends_time_step_index is None:
        time_step_index_range_to_read[_TREND_ID_ATTR][
            1
        ] = result_metadata.time_steps_boundaries[1][1]

    cache = {}
    for time_set_key in time_sets_key_list:
        if time_set_key not in cache:
            source_id, base_ts_list = time_set_key
            source_group_name = _SOURCE_ID_TO_GROUP_NAME[source_id]
            global_start, global_stop = time_step_index_range_to_read[source_id]
            time_set_info = result_metadata.time_set_info[source_group_name]

            if source_id not in dsets_by_source_id:
                dsets_by_source_id[source_id] = {
                    base_ts: f[source_group_name][TIME_SET_DSET_NAME]
                    for base_ts, f in result_files.items()
                }
            dsets = dsets_by_source_id[source_id]

            cache[time_set_key] = _read_time_set(
                dsets,
                base_ts_list,
                time_set_info,
                global_start,
                global_stop,
            )

    return _concatenate_values(cache)


def _read_time_set(
    dsets: Dict[int, h5py.File],
    base_ts_list: Tuple[int, ...],
    time_set_info: Dict[int, TimeSetInfoItem],
    global_start: int,
    global_stop: int,
) -> List[numpy.ndarray]:
    """
    Read a single Time Set (used by `ReadTimeSets`).

    :param dsets:
        The time set data sets used to collect the data.

    :param base_ts_list:
        The base time steps relevant to this time set.

    :param time_set_info:
        The metadata associated with the time set.

    :param global_start:
        The global start of the read.

    :param global_stop:
        The global stop (exclusive) of the read.
    """
    result = []
    for base_ts in base_ts_list:
        time_set_dset = dsets.get(base_ts)
        if time_set_dset:
            time_set_info_item = time_set_info[base_ts]
            time_set_start = time_set_info_item.global_start
            time_set_size = time_set_info_item.size
            start_index = _global_index_to_file_based_index(
                global_start, time_set_start, time_set_size
            )
            stop_index = _global_index_to_file_based_index(
                global_stop, time_set_start, time_set_size
            )
            result.append(time_set_dset[start_index:stop_index])

    return result


def _concatenate_values(
    data_dict: Dict[Any, List[numpy.ndarray]]
) -> Dict[Any, numpy.ndarray]:
    """
    Concatenate the values in the given dict.
    """
    return {
        key: (
            numpy.empty((0,), dtype=numpy.float64)
            if len(data_list) == 0
            else numpy.concatenate(data_list)
        )
        for key, data_list in data_dict.items()
    }


def map_output_key_to_time_set_key(
    all_metadata: Dict[int, Dict]
) -> Dict[OutputKeyType, TimeSetKeyType]:
    """
    Operates on the complete metadata mapping "output key"s to they  respective "time set key".

    :param all_metadata:
        A dict mapping base time steps to output metadata.
    """
    from collections import defaultdict

    output_key_dict = defaultdict(set)
    for base_ts, metadata in all_metadata.items():
        for output_id, meta in metadata.items():
            time_set_key = output_key_dict[output_id]
            time_set_key.add(base_ts)
    return {k: tuple(sorted(v)) for k, v in output_key_dict.items()}


def map_base_time_set_to_time_set_keys(
    output_key_to_time_set_key_dict: Dict[OutputKeyType, TimeSetKeyType]
) -> Dict[int, Tuple[TimeSetKeyType, ...]]:
    """
    Maps base time steps to the "time set key"s where they are found.

    :param output_key_to_time_set_key_dict:
        See `MapOutputKeyToTimeSetKey` return value documentation.
    """
    from collections import defaultdict

    base_ts_index_dict = defaultdict(set)
    for time_set_key in output_key_to_time_set_key_dict.values():
        for base_ts in time_set_key:
            time_set_key_set = base_ts_index_dict[base_ts]
            time_set_key_set.add(time_set_key)
    return {k: tuple(sorted(v)) for k, v in base_ts_index_dict.items()}


def concatenate_metadata(
    r_a: ALFASimResultMetadata,
    r_b: ALFASimResultMetadata,
    *,
    yield_execution: Callable[[], None] = lambda: None,
) -> ALFASimResultMetadata:
    """
    Concatenate two result metadata objects.
    """

    if r_b.result_directory != r_a.result_directory:
        raise RuntimeError("Can not concatenate result from different sources.")

    a_initial_ts_index, a_final_ts_index = r_a.time_steps_boundaries
    if a_initial_ts_index == a_final_ts_index:
        return r_b

    b_initial_ts_index, b_final_ts_index = r_b.time_steps_boundaries
    if b_initial_ts_index == b_final_ts_index:
        return r_a

    a_number_of_files = _get_number_of_base_time_steps_from_time_set_info(
        r_a.time_set_info
    )
    b_number_of_files = _get_number_of_base_time_steps_from_time_set_info(
        r_b.time_set_info
    )
    if a_number_of_files != b_number_of_files:
        raise ResultsNeedFullReloadError(
            f"The two result need to have matching number_of_files: {a_number_of_files} != {b_number_of_files}"
        )

    if a_final_ts_index != b_initial_ts_index:
        raise RuntimeError(
            f"The concatenated results must be adjacent.\na_final_ts_index:{a_final_ts_index}\nb_initial_ts_index:{b_initial_ts_index}"
        )

    time_sets_as_dict = {}  # Using dict as ordered set.

    def update_time_set(source, a_time_set_key, b_time_set_key):
        new_time_set_key = set(a_time_set_key)
        new_time_set_key.update(b_time_set_key)
        new_time_set_key = tuple(sorted(new_time_set_key))
        new_source_time_set_key = (source, new_time_set_key)
        time_sets_as_dict[new_source_time_set_key] = None
        return new_source_time_set_key[1]

    def merge_metadata(a_metadata, b_metadata, *, source, update=(), min_=(), max_=()):
        updated_a_time_sets = set()
        # Merge.
        for output_id, b_meta_item in b_metadata.items():
            yield_execution()
            if output_id in a_metadata:
                # Merge "b" into "a".
                a_meta_item = a_metadata[output_id]

                for attr_name in update:
                    a_meta_item[attr_name].update(b_meta_item[attr_name])
                for attr_name in min_:
                    a_meta_item[attr_name] = numpy.nanmin(
                        (a_meta_item[attr_name], b_meta_item[attr_name]), axis=0
                    )
                for attr_name in max_:
                    a_meta_item[attr_name] = numpy.nanmax(
                        (a_meta_item[attr_name], b_meta_item[attr_name]), axis=0
                    )

                a_meta_item["time_set_key"] = update_time_set(
                    source, a_meta_item["time_set_key"], b_meta_item["time_set_key"]
                )
                updated_a_time_sets.add(output_id)
            else:
                # Not in "a", just assign "b" to "a".
                a_metadata[output_id] = b_meta_item

                only_b_source_time_set_key = (source, b_meta_item["time_set_key"])
                if only_b_source_time_set_key not in time_sets_as_dict:
                    time_sets_as_dict[only_b_source_time_set_key] = None
        # Copy time sets used only in "a" result.
        for output_id, a_meta_item in a_metadata.items():
            if output_id in updated_a_time_sets:
                continue
            yield_execution()
            only_a_source_time_set_key = (source, a_meta_item["time_set_key"])
            if only_a_source_time_set_key not in time_sets_as_dict:
                time_sets_as_dict[only_a_source_time_set_key] = None
        return a_metadata

    profiles = merge_metadata(
        r_a.profiles,
        r_b.profiles,
        source="profile_id",
        update=["domain_id", "data_id"],
        min_=["global_min"],
        max_=["global_max"],
    )

    trends = merge_metadata(
        r_a.trends,
        r_b.trends,
        source="trend_id",
        update=["index"],
        min_=["min"],
        max_=["max"],
    )

    app_version_info = r_a.app_version_info.copy()
    app_version_info.update(r_b.app_version_info)

    return ALFASimResultMetadata(
        profiles=profiles,
        trends=trends,
        time_sets=list(time_sets_as_dict.keys()),
        time_sets_unit=r_a.time_sets_unit,
        time_steps_boundaries=(
            r_a.time_steps_boundaries[0],
            r_b.time_steps_boundaries[1],
        ),
        time_set_info=r_b.time_set_info,
        result_directory=r_a.result_directory,
        app_version_info=app_version_info,
    )


def read_global_sensitivity_analysis_meta_data(
    result_directory: Path,
) -> Optional[GlobalSensitivityAnalysisMetadata]:
    """
    Read the global sensitivity analysis metadata persisted in a result file.
    """

    return GlobalSensitivityAnalysisMetadata.get_metadata_from_dir(
        result_directory=result_directory
    )


def read_global_sensitivity_analysis_time_set(
    result_directory: Path,
) -> Optional[numpy.array]:
    """
    Get the time set for sensitivity analysis results.
    """
    with open_result_file(result_directory, result_filename="result") as result_file:
        if not result_file:
            return
        return result_file[GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME]["time_set"][:]


def read_global_sensitivity_coefficients(
    coefficients_key: str,
    metadata: GlobalSensitivityAnalysisMetadata,
) -> Optional[np.ndarray]:
    """
    Read the global sensitivity analysis coefficients results.
    """
    # The metadata is empty.
    if not metadata.gsa_items:
        return None
    meta = metadata.gsa_items[coefficients_key]
    with open_result_file(
        metadata.result_directory, result_filename="result"
    ) as result_file:
        gsa_group = result_file[GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME]
        coefficients_dset = gsa_group["global_sensitivity_analysis"]
        return coefficients_dset[meta.qoi_index, meta.qoi_data_index]


def read_history_matching_metadata(result_directory: Path) -> HistoryMatchingMetadata:
    """
    :param result_directory:
        The directory to lookup for the History Matching result file.
    """
    return HistoryMatchingMetadata.from_result_directory(result_directory)


def read_history_matching_result(
    metadata: HistoryMatchingMetadata,
    hm_type: Literal["deterministic", "probabilistic"],
    hm_result_key: Optional[HistoryMatchingResultKeyType] = None,
) -> Dict[HistoryMatchingResultKeyType, Union[np.ndarray, float]]:
    """
    :param metadata:
        History Matching result metadata.
    :param hm_type:
        The type of HM analysis. Can be 'deterministic' or 'probabilistic'.
    :param hm_result_key:
        The id of the parametric vars to collect the result. Defaults to None, in which case the
        result of all keys found in the metadata will be returned.
    :return:
        A dict mapping the HM result key (the parametric var id) to its corresponding result, which
        could be an array with N values (N being the sampling size) for the probabilistic or a single
        float for the deterministic.
    """
    if hm_type not in ("deterministic", "probabilistic"):
        raise ValueError(f"history matching of type `{hm_type}` not supported")

    if hm_type == "deterministic":
        dataset_key = HISTORY_MATCHING_DETERMINISTIC_DSET_NAME
    else:
        assert hm_type == "probabilistic"
        dataset_key = HISTORY_MATCHING_PROBABILISTIC_DSET_NAME

    with open_result_file(metadata.result_directory) as result_file:
        if not result_file:
            return {}

        result = result_file[HISTORY_MATCHING_GROUP_NAME][dataset_key]

        result_map = {}
        if hm_result_key is None:
            for key, meta in metadata.hm_items.items():
                result_map[key] = result[meta.data_index]
        else:
            meta = metadata.hm_items.get(hm_result_key)
            if meta is not None:
                result_map[hm_result_key] = result[meta.data_index]

        return result_map


@contextmanager
def open_result_file(
    result_directory: Path, result_filename: str = "result"
) -> Iterator[Optional[h5py.File]]:
    """
    :param result_directory:
        The directory to lookup for the result file.
    :param result_filename:
        The filename.
    :return:
        The result HDF file, or None if it doesn't exist or is still being created.
    """
    filepath = result_directory / result_filename
    creating_file = result_directory / f"{result_filename}.creating"

    if not filepath.is_file():
        yield None
    # Do not open incomplete file.
    elif creating_file.is_file():
        yield None
    else:
        with _open_result_file(filepath) as file:
            yield file
