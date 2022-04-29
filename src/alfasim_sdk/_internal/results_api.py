import contextlib
import json
import os
from collections import namedtuple
from pathlib import Path
from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import attr
import h5py
import numpy
from barril.units import Array

from alfasim_sdk._internal.constants import META_GROUP_NAME
from alfasim_sdk._internal.constants import PROFILES_GROUP_NAME
from alfasim_sdk._internal.constants import PROFILES_STATISTICS_DSET_NAME_SUFFIX
from alfasim_sdk._internal.constants import RESULT_FILE_PREFIX
from alfasim_sdk._internal.constants import TIME_SET_DSET_NAME
from alfasim_sdk._internal.constants import TRENDS_GROUP_NAME


TimeSetInfoItem = namedtuple("TimeSetInfoItem", "global_start size uuid")
TimeSetKeyType = Tuple[int, ...]
SourceTimeSetKeyType = Tuple[str, TimeSetKeyType]
BaseTimeStepIndexToMetaList = Dict[int, Dict]

_PROFILE_ID_ATTR = "profile_id"
_TREND_ID_ATTR = "trend_id"
_SOURCE_ID_TO_GROUP_NAME = {
    _PROFILE_ID_ATTR: PROFILES_GROUP_NAME,
    _TREND_ID_ATTR: TRENDS_GROUP_NAME,
}


@attr.s(slots=True, hash=False)
class ALFASimResultMetadata:
    """
    :ivar profiles: Map output keys (profile id and property id) to metadata entries.
    :ivar trends:  Map output keys (trend id and property id) to metadata entries.
    :ivar time_sets: Map sourced time set keys (tuples of relevant base time sets) to a list of
        list of the time step values.
    :ivar time_sets_unit: The unit used by all time sets.
    :ivar time_steps_boundaries: The time step boundaries index where this metadata object is
        relevant. The first item is the starting time step index (including) and the second is
        the ending time step index (excluding).
    :ivar time_set_info: Map output type to maps of base time steps to `TimeSetInfoItem`;
    :ivar result_directory: The path where this data has been read.
    :ivar app_version_info: Map "base time steps" to the application version used in the simulation.
    """

    profiles = attr.ib(validator=attr.validators.instance_of(dict))
    trends = attr.ib(validator=attr.validators.instance_of(dict))
    time_sets = attr.ib(validator=attr.validators.instance_of(list))
    time_sets_unit = attr.ib(validator=attr.validators.instance_of(str))
    time_steps_boundaries = attr.ib(validator=attr.validators.instance_of(tuple))
    time_set_info = attr.ib(validator=attr.validators.instance_of(dict))
    result_directory = attr.ib(validator=attr.validators.instance_of(Path))
    app_version_info = attr.ib(validator=attr.validators.instance_of(dict))


@attr.s(slots=True, hash=False)
class _MergedMetadataWithStatistics:
    """
    :ivar app_version_info: Map "base time steps" to the application version used in the simulation.
    :ivar profile_key_to_metadata: Map output keys (profile id and property id) to metadata entries.
    :ivar trend_key_to_metadata:  Map output keys (trend id and property id) to metadata entries.
    :ivar time_set_keys: List of sourced time set keys (tuples of relevant base time sets).
    """

    app_version_info = attr.ib(validator=attr.validators.instance_of(dict))
    profile_key_to_metadata = attr.ib(validator=attr.validators.instance_of(dict))
    trend_key_to_metadata = attr.ib(validator=attr.validators.instance_of(dict))
    time_set_keys = attr.ib(validator=attr.validators.instance_of(list))


class ResultsNeedFullReloadError(RuntimeError):
    pass


# https://docs.python.org/3/library/weakref.html
# Several built-in types such as list and dict do not directly support weak references but can
# add support through subclassing:
class _Dict(dict):
    __slots__ = ["__weakref__"]


def get_number_of_base_time_steps_from(time_set_info_source_dict):
    from itertools import chain

    expected_number_of_base_ts = chain.from_iterable(
        time_set_info.keys() for time_set_info in time_set_info_source_dict.values()
    )
    return len(set(expected_number_of_base_ts))


def read_global_metadata(
    result_files: Dict[int, h5py.File],
) -> Tuple[BaseTimeStepIndexToMetaList, BaseTimeStepIndexToMetaList]:
    """
    :return:
        - a dict mapping base time steps to a list of profile metadata items;
        - a dict mapping base time steps to a list of trend metadata items;
    """

    def update_global_metadata(
        result_file: h5py.File,
        metadata_collection: BaseTimeStepIndexToMetaList,
        base_ts: int,
        output_type: str,
    ) -> None:
        """
        Read a metadata file and add it to a metadata collection.

        :param metadata_collection: This collection is changed.
            The keys are the "base time step index" and the values are the metadata from the
            file (the duplicates have been removed and the original index recorded).
        """
        meta = json.loads(result_file[META_GROUP_NAME].attrs[output_type])
        # TODO: arthur: Review commented code
        # # Remove duplicates from the result. Save the original index.
        # meta = []
        # for index, item in enumerate(meta_tmp):
        #     if index == meta_tmp.index(item):
        #         item = item.copy()  # The original item is used to eliminate copies.
        #         item['index'] = index
        #         meta.append(item)
        metadata_collection[base_ts] = meta

    all_profiles_meta: BaseTimeStepIndexToMetaList = {}
    all_trends_meta: BaseTimeStepIndexToMetaList = {}
    for base_ts, result_file in result_files.items():
        update_global_metadata(result_file, all_profiles_meta, base_ts, "profiles")
        update_global_metadata(result_file, all_trends_meta, base_ts, "trends")
    return all_profiles_meta, all_trends_meta


def read_time_set_info(result_files, container_group_name):
    """
    :type result_files: Dict[int, h5py.File]
    :type container_group_name: str

    :rtype: Dict[int, TimeSetInfoItem]
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


def map_output_key_to_time_set_key(all_metadata):
    """
    Operates on the complete metadata mapping "output key"s to they  respective "time set key".

    :type all_metadata: Dict[int, Dict]
    :param all_metadata:
        A dict mapping base time steps to output metadata.

    :rtype: Dict[OutputKeyType, TimeSetKeyType]
    """
    from collections import defaultdict

    output_key_dict = defaultdict(set)
    for base_ts, metadata in all_metadata.items():
        for output_id in metadata.keys():
            time_set_key = output_key_dict[output_id]
            time_set_key.add(base_ts)
    return {k: tuple(sorted(v)) for k, v in output_key_dict.items()}


def map_base_time_set_to_time_set_keys(output_key_to_time_set_key_dict):
    """
    Maps base time steps to the "time set key"s where they are found.

    :type output_key_to_time_set_key_dict: Dict[OutputKeyType, TimeSetKeyType]
    :param output_key_to_time_set_key_dict:
        See `map_output_key_to_time_set_key` return value documentation.

    :rtype: Dict[int, Tuple[TimeSetKeyType, ...]]
    """
    from collections import defaultdict

    base_ts_index_dict = defaultdict(set)
    for time_set_key in output_key_to_time_set_key_dict.values():
        for base_ts in time_set_key:
            time_set_key_set = base_ts_index_dict[base_ts]
            time_set_key_set.add(time_set_key)
    return {k: tuple(sorted(v)) for k, v in base_ts_index_dict.items()}


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

    SKIP = True

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

    def read_profiles_statistics(ts_index: int):
        f = result_files[ts_index]
        profile_group = f[PROFILES_GROUP_NAME]

        for output_id, meta in global_profiles_metadata[ts_index].items():
            source_time_set_key = "profile_id", profiles_to_time_set_key[output_id]
            partial_indices = time_set_ranges[source_time_set_key]
            start_index, stop_index = partial_indices[-1]  # The most recent.

            if start_index == stop_index:
                continue

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

    def read_trends_statistics(ts_index):
        f = result_files[ts_index]
        trends_group = f[TRENDS_GROUP_NAME]
        if "trends_statistic" not in trends_group:
            return

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
        helper, ts_index, global_metadata_dict, base_ts_to_time_set_keys_dict
    ):
        """
        Updates the helper. Use/update `global_time_set_indices` from outer scope.
        Merges the index/data_id_domain_id from the various base time set indices into a
        single dict. Also update the time set helper indices returned by the outer function.

        :param Helper helper: One of `profiles_helper` or `trends_helper` to be updated.
        :param int ts_index: The time steps index used. This should be a base time step index.
        :param Dict[int,Dict] global_metadata_dict: Maps base time step index to a list of
            metadata items in effect (`global_profiles_metadata or `global_trends_metadata`).
        :param Dict[int,List[TimeSetKeyType]] base_ts_to_time_set_keys_dict: Maps base time step
            index to a list of affected time step keys (this should be a per output type map)
        """
        nonlocal result_files, time_set_ranges
        if ts_index not in base_ts_to_time_set_keys_dict:
            return SKIP

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
            return SKIP

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
        if not skip:
            read_profiles_statistics(index)

        skip = update_helper(
            trends_helper,
            index,
            global_trends_metadata,
            trends_base_ts_to_time_set_keys,
        )
        if not skip:
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

    :param initial_profiles_time_step_index: The profile global time step index where to
        start collecting metadata. If not supplied on `None` then `0` is used.
    :param final_profiles_time_step_index: The profile global time step index after the last
        to have its metadata collected. If not supplied or `None` all the available time
        steps after `initial_profiles_time_step_index`  are collected.
    :param initial_trends_time_step_index: The trend global time step index where to
        start collecting metadata. If not supplied on `None` then `0` is used.
    :param final_trends_time_step_index: The trend global time step index after the last to
        have its metadata collected. If not supplied or `None` all the available time steps
        after `initial_trends_time_step_index` are collected.
    :param previous_time_set_info: The `time_set_info` from the previous metadata (when
        progressively reading). If omitted a time set truncation is not detected. This is
        only relevant when progressive reading is used (..see: `ConcatenateMetadata`).
    """
    if previous_time_set_info is None:
        previous_time_set_info = {}

    def get_empty_result(profile_index=0, trend_index=0):
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

    if not result_directory.is_dir():
        return get_empty_result()

    result_files = load_result_files(result_directory)
    if len(result_files) == 0:
        return get_empty_result()

    expected_number_of_base_ts = get_number_of_base_time_steps_from(
        previous_time_set_info
    )
    if (expected_number_of_base_ts > 0) and (
        len(result_files) != expected_number_of_base_ts
    ):
        raise ResultsNeedFullReloadError(
            f"Different number of result files: {len(result_files)} but expecting {expected_number_of_base_ts}"
        )

    global_profiles_metadata, global_trends_metadata = read_global_metadata(
        result_files
    )

    def normalize_time_step_index(n, total_size, *, default):
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

    def check_time_set_info_for_truncation(old, new):
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
        return get_empty_result(
            initial_profiles_time_step_index, initial_trends_time_step_index
        )

    if initial_profiles_time_step_index != final_profiles_time_step_index:
        if not (0 <= initial_profiles_time_step_index < total_profiles_time_set_size):
            raise IndexError(
                f"`initial_trends_time_step_index` ({initial_profiles_time_step_index}) outside of valid range: [0, {total_profiles_time_set_size - 1}]"
            )
        if not (0 <= final_profiles_time_step_index <= total_profiles_time_set_size):
            raise IndexError(
                f"`initial_trends_time_step_index` ({final_profiles_time_step_index}) outside of valid range: [0, {total_profiles_time_set_size}]"
            )

    if initial_trends_time_step_index != final_trends_time_step_index:
        if not (0 <= initial_trends_time_step_index < total_trends_time_set_size):
            raise IndexError(
                f"`initial_trends_time_step_index` ({initial_trends_time_step_index}) outside of valid range: [0, {total_trends_time_set_size - 1}]"
            )
        if not (0 <= final_trends_time_step_index <= total_trends_time_set_size):
            raise IndexError(
                f"`initial_trends_time_step_index` ({final_trends_time_step_index}) outside of valid range: [0, {total_trends_time_set_size}]"
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


def read_trends_data(
    result_metadata,
    output_keys=None,
    initial_trends_time_step_index=None,
    final_trends_time_step_index=None,
):
    """
    :param ALFASimResultMetadata result_metadata:

    :param Optional[List[OutputKeyType]] output_keys: Must be trends output ids. Default to ALL
        trends found in `result_metadata`.

    :param int initial_trends_time_step_index: If `None` the initial boundary of the result
        metadata is used.

    :param int final_trends_time_step_index: If `None` the final boundary of the result metadata
        is used.

    :rtype: Dict[OutputKeyType, numpy.array]
    :return: The data for the trends listed in `output_keys`.
    """

    trends_metadata = result_metadata.trends
    result_files = load_result_files(result_metadata.result_directory)
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
            if index is None:
                continue

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
        if len(data_list) == 0:
            trends[trend_key] = numpy.empty((0,), dtype=numpy.float64)
        else:
            trends[trend_key] = numpy.concatenate(data_list)

    return trends


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
    index_counter = 0
    for base_ts in time_set_key:
        time_set_info_item = profile_time_set_info[base_ts]
        know_time_set_zise = index_counter + time_set_info_item.size
        if index_counter <= time_step_index < know_time_set_zise:
            return base_ts, (time_step_index - index_counter)
        else:
            index_counter = know_time_set_zise
    else:
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
    group_name,
    data_attr,
    data_id_suffix="",
    slicer,
):
    """
    This is the core implementation of `read_profiles_data`/`ReadProfilesDomainData`.

    :param str group_name:
    :param str data_attr:
    :param str data_id_suffix:
    :param Callable[Tuple[int], Any] slicer:
    """
    profiles_metadata = result_metadata.profiles
    profiles_time_set_info = result_metadata.time_set_info[PROFILES_GROUP_NAME]

    result_files = load_result_files(result_metadata.result_directory)
    profiles = {}
    for profile_key in output_keys:
        meta = profiles_metadata[profile_key]
        result_key, mapped_time_step_index = _remap_profile_time_step_index(
            profiles_time_set_info, meta["time_set_key"], time_step_index
        )
        f = result_files[result_key]
        profiles_group = f[group_name]
        data_id = meta[data_attr].get(result_key)

        if data_id is None:
            profiles[profile_key] = None
            continue

        data_id += data_id_suffix
        index = slicer(mapped_time_step_index)
        profiles[profile_key] = profiles_group[data_id].__getitem__(index)

    return profiles


def read_profiles_data(result_metadata, output_keys, time_step_index):
    """
    :param ALFASimResultMetadata result_metadata:

    :param List[OutputKeyType] output_keys: Must be profiles output ids.

    :param int time_step_index:

    :rtype: Dict[OutputKeyType, Optional[numpy.array]]
    :return: The data for the profiles listed in `output_keys` for the given `time_step_index`, if
        a profile is not found `None` instead a `numpy.array` is mapped.
    """
    return _read_profile_arrays(
        result_metadata,
        output_keys,
        time_step_index,
        group_name=PROFILES_GROUP_NAME,
        data_attr="data_id",
        slicer=lambda index: (index, slice(None)),
    )


def read_profiles_domain_data(result_metadata, output_keys, time_step_index):
    """
    :param ALFASimResultMetadata result_metadata:

    :param List[OutputKeyType] output_keys: Must be profiles output ids.

    :param int time_step_index:

    :rtype: Dict[OutputKeyType, Optional[numpy.array]]
    :return: The data for the profiles listed in `output_keys` for the given `time_step_index`, if
        a profile is not found `None` instead a `numpy.array` is mapped.
    """
    return _read_profile_arrays(
        result_metadata,
        output_keys,
        time_step_index,
        group_name=META_GROUP_NAME,
        data_attr="domain_id",
        slicer=lambda index: slice(None),
    )


def read_profiles_local_statistics(result_metadata, output_keys, time_step_index):
    """
    :param ALFASimResultMetadata result_metadata:

    :param List[OutputKeyType] output_keys: Must be profiles output ids.

    :param int time_step_index:

    :rtype: Dict[OutputKeyType, Optional[numpy.array]]
    :return: The statistics for the profiles listed in `output_keys` for the given
        `time_step_index`, if the profile is not found `None` instead a `numpy.array` is mapped.
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


def _close_files(files_list):
    """
    :type files_list: List[h5py.File]
    """
    for f in files_list:
        f.close()


# TODO: arthur: This code is duplicated from ben10, try to find a workaround for it...
@contextlib.contextmanager
def cwd(directory):
    """
    Context manager for current directory (uses with_statement)

    e.g.:
        # working on some directory
        with cwd('/home/new_dir'):
            # working on new_dir

        # working on some directory again

    :param str directory:
        Target directory to enter
    """
    old_directory = os.getcwd()
    if directory is not None:
        os.chdir(directory)
    try:
        yield directory
    finally:
        os.chdir(old_directory)


def load_result_files(result_directory: Path) -> Dict[int, h5py.File]:
    """
    Return a dict with the result files.

    Note that once the container dict is collected the files originally returned are closed.
    """

    prefix_len = len(RESULT_FILE_PREFIX)
    # TODO: ASIM-2561: Cache files!

    def open_result_file(filename):

        try:
            with cwd(filename.parent):
                try:
                    return h5py.File(filename.name, "r", libver="latest", swmr=True)
                except OSError as os_error:
                    swmr_message = "Unable to open file (file is not already open for SWMR writing)"
                    if str(os_error) == swmr_message:
                        return h5py.File(
                            filename.name, "r", libver="latest", swmr=False
                        )
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
            from os import path

            name, _ = path.splitext(f)
            files_under_creation.add(Path(name))
        elif ext == "":
            result_files.add(f)
        else:
            raise ValueError(f"Unknown ext: {ext}")

    result_files.difference_update(files_under_creation)  # Ignore incomplete files.
    result_files_sorted = (
        (int(filename.name[prefix_len:]), open_result_file(filename))
        for filename in result_files
    )
    result_files_sorted_dict = _Dict(sorted(result_files_sorted, key=lambda x: x[0]))

    # Close the files once the container is collected.
    import weakref

    weakref.finalize(
        result_files_sorted_dict,
        _close_files,
        files_list=list(result_files_sorted_dict.values()),
    )

    return result_files_sorted_dict


def _global_index_to_file_based_index(
    index: int, time_set_start: int, time_set_size: int
):
    """
    Converts a global index into an index suitable to extract the data from a result file.

    :param index: The Global index.
    :param time_set_start: The starting global index of the time set stored in the file.
    :param time_set_size: The number of time steps stored in the file.

    :return: The equivalent index to use when indexing the data stored in the file.
    """
    if index <= time_set_start:
        return 0
    elif index >= (time_set_start + time_set_size):
        return time_set_size
    else:
        return index - time_set_start


def _read_time_set(dsets, base_ts_list, time_set_info, global_start, global_stop):
    """
    Read a single Time Set (used by `read_time_sets`).


    :param Dict[int, h5py.File] dsets: The time set data sets used to collect the data.
    :param Tuple[int,...] base_ts_list: The base time steps relevant to this time set.
    :param Dict[int,TimeSetInfoItem] time_set_info: The metadata associated with the time set.
    :param int global_start: The global start of the read.
    :param int global_stop: The global stop (exclusive) of the read.

    :rtype: List[numpy.ndarray]
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


def read_time_sets(
    result_metadata,
    time_sets_key_list=None,
    initial_profiles_time_step_index=None,
    final_profiles_time_step_index=None,
    initial_trends_time_step_index=None,
    final_trends_time_step_index=None,
):
    """
    :param ALFASimResultMetadata result_metadata:

    :param str data_file_name:

    :param Optional[List[SourceTimeSetKeyType]] time_sets_key_list: Default to ALL time sets found
        in `result_metadata`.

    :param int initial_profiles_time_step_index: If `None` the initial boundary of the result
        metadata is used.

    :param int final_profiles_time_step_index: If `None` the final boundary of the result metadata
        is used.

    :param int initial_trends_time_step_index: If `None` the initial boundary of the result
        metadata is used.

    :param int final_trends_time_step_index: If `None` the final boundary of the result metadata
        is used.

    :rtype: Dict[SourceTimeSetKeyType, numpy.array]
    :return: The data for the time sets listed in `time_sets_key_list`.
    """
    # TODO: ASIM-2561: Proper AppFacade
    result_files = load_result_files(result_metadata.result_directory)
    if time_sets_key_list is None:
        time_sets_key_list = result_metadata.time_sets.keys()

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


def get_time_set_and_trend_from_trend_id(trend_id, results_metadata):
    time_set_key = ("trend_id", results_metadata.trends[trend_id]["time_set_key"])
    time_set_unit = results_metadata.time_sets_unit
    time_set_values = read_time_sets(results_metadata, [time_set_key])[time_set_key]
    trend_values = read_trends_data(results_metadata, [trend_id])[trend_id]
    trend_unit = results_metadata.trends[trend_id]["unit"]
    return Array(time_set_values, time_set_unit), Array(trend_values, trend_unit)


def get_profile_from_profile_id(profile_id, results_metadata, timestep_id):
    profile_domain_values = read_profiles_domain_data(results_metadata, [profile_id], timestep_id)[profile_id]
    profile_domain_unit = results_metadata.profiles[profile_id]['domain_unit']
    
    profile_values = read_profiles_data(results_metadata, [profile_id], timestep_id)[
        profile_id
    ]
    profile_unit = results_metadata.profiles[profile_id]["unit"]
    
    return Array(profile_domain_values, profile_domain_unit), Array(profile_values, profile_unit)
