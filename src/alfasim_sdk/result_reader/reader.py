from __future__ import annotations

from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import Sequence
from typing import Tuple
from typing import Union

import attr
import numpy as np
from attr import define
from barril.curve.curve import Curve
from barril.units import Array
from barril.units import Scalar
from typing_extensions import Self

from alfasim_sdk.result_reader.aggregator import ALFASimResultMetadata
from alfasim_sdk.result_reader.aggregator import GlobalSensitivityAnalysisMetadata
from alfasim_sdk.result_reader.aggregator import GSAOutputKey
from alfasim_sdk.result_reader.aggregator import HistoricDataCurveMetadata
from alfasim_sdk.result_reader.aggregator import HistoryMatchingMetadata
from alfasim_sdk.result_reader.aggregator import HMOutputKey
from alfasim_sdk.result_reader.aggregator import (
    read_global_sensitivity_analysis_meta_data,
)
from alfasim_sdk.result_reader.aggregator import read_global_sensitivity_coefficients
from alfasim_sdk.result_reader.aggregator import (
    read_history_matching_historic_data_curves,
)
from alfasim_sdk.result_reader.aggregator import read_history_matching_metadata
from alfasim_sdk.result_reader.aggregator import read_history_matching_result
from alfasim_sdk.result_reader.aggregator import read_metadata
from alfasim_sdk.result_reader.aggregator import read_profiles_data
from alfasim_sdk.result_reader.aggregator import read_profiles_domain_data
from alfasim_sdk.result_reader.aggregator import read_time_sets
from alfasim_sdk.result_reader.aggregator import read_trends_data
from alfasim_sdk.result_reader.aggregator import (
    read_uncertainty_propagation_analyses_meta_data,
)
from alfasim_sdk.result_reader.aggregator import read_uncertainty_propagation_results
from alfasim_sdk.result_reader.aggregator import read_uq_time_set
from alfasim_sdk.result_reader.aggregator import UncertaintyPropagationAnalysesMetaData
from alfasim_sdk.result_reader.aggregator import UPOutputKey
from alfasim_sdk.result_reader.aggregator import UPResult
from alfasim_sdk.result_reader.aggregator_constants import (
    GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME,
)
from alfasim_sdk.result_reader.aggregator_constants import RESULTS_FOLDER_NAME
from alfasim_sdk.result_reader.aggregator_constants import (
    UNCERTAINTY_PROPAGATION_GROUP_NAME,
)


@define(frozen=True)
class ProfileMetadata:
    property_name: str
    element_name: str
    timesteps_count: int

    def __str__(self):
        return f"{self.property_name}@{self.element_name}(timesteps={self.timesteps_count})"


@define(frozen=True)
class PositionalTrendMetadata:
    property_name: str
    element_name: str
    position: Scalar

    def __str__(self):
        return (
            f"{self.property_name}@{self.element_name}({self.position.GetFormatted()})"
        )


@define(frozen=True)
class OverallTrendMetadata:
    property_name: str
    element_name: str

    def __str__(self):
        return f"{self.property_name}@{self.element_name}"


@define(frozen=True)
class GlobalTrendMetadata:
    property_name: str

    def __str__(self):
        return self.property_name


class Results:
    """
    Allows reading trend and profile curves from alfasim simulation results
    using network element names instead internal alfasim ids.
    """

    def __init__(self, alfacase_data_folder: Path):
        self._data_folder = alfacase_data_folder
        self._position_margin = 0.01
        self._metadata: ALFASimResultMetadata = None

    @property
    def data_folder(self) -> Path:
        """
        The data folder used to run the simulation.
        """
        return self._data_folder

    @property
    def results_folder(self) -> Path:
        return self._data_folder / RESULTS_FOLDER_NAME

    @property
    def metadata(self) -> ALFASimResultMetadata:
        # Lazy load the metadata object.
        if self._metadata is None:
            self._metadata = read_metadata(self.results_folder)

        return self._metadata

    @property
    def status(self) -> Path:
        return self.data_folder / "status/status.json"

    @property
    def log(self) -> Path:
        return self.data_folder / "log.txt"

    @property
    def log_calc(self) -> Path:
        return self.data_folder / "log_calc.txt"

    def _read_trend(self, trend_key: str) -> Curve:
        """
        Create a trend curve from the results.
        """
        metadata = self.metadata
        trend_metadata = metadata.trends[trend_key]
        time_set_key = ("trend_id", trend_metadata["time_set_key"])
        time_sets = read_time_sets(metadata, [time_set_key])
        time_set = time_sets[time_set_key]

        trend_data = read_trends_data(metadata, [trend_key])
        data = trend_data[trend_key]

        return Curve(
            image=Array(
                values=data,
                unit=trend_metadata["unit"],
                category=trend_metadata["category"],
            ),
            domain=Array(values=time_set, unit="s", category="time"),
        )

    def _read_profile(self, profile_key: str, index: int) -> Curve:
        """
        Create a profile curve from the results.
        """
        metadata = self.metadata
        profile_metadata = metadata.profiles[profile_key]
        domains = read_profiles_domain_data(metadata, [profile_key], index)
        domain = domains[profile_key]

        images = read_profiles_data(metadata, [profile_key], index)
        image = images[profile_key]

        return Curve(
            image=Array(
                values=image,
                unit=profile_metadata["unit"],
                category=profile_metadata["category"],
            ),
            domain=Array(
                values=domain, unit=profile_metadata["domain_unit"], category="length"
            ),
        )

    def get_positional_trend_curve(
        self,
        property_name: str,
        element_name: str,
        position: Union[Scalar, Tuple[float, str]],
    ) -> Curve:
        """
        Return a positional trend.
        """
        if not isinstance(position, Scalar):
            value, unit = position
            position = Scalar(value, unit)

        metadata = self.metadata
        position_m: float = position.GetValue("m")
        for trend_key, trend_metadata in metadata.trends.items():
            if (
                (trend_metadata["property_id"] == property_name)
                and (trend_metadata["network_element_name"] == element_name)
                and ("position" in trend_metadata)
            ):
                md_pos: float = trend_metadata["position"]
                if abs(position_m - md_pos) < self._position_margin:
                    return self._read_trend(trend_key)

        msg = [
            f"Can not locate '{property_name}' trend for element '{element_name}' at position '{position_m}'.\nFound positional trends:",
            *map(str, self.list_positional_trends()),
        ]
        raise RuntimeError("\n- ".join(msg))

    def get_overall_trend_curve(self, property_name: str, element_name: str) -> Curve:
        """
        Return an overall trend.
        """
        metadata = self.metadata
        for trend_key, trend_metadata in metadata.trends.items():
            if (
                (trend_metadata["property_id"] == property_name)
                and (trend_metadata["network_element_name"] == element_name)
                and ("position" not in trend_metadata)
            ):
                return self._read_trend(trend_key)

        msg = [
            f"Can not locate overall '{property_name}' trend for element '{element_name}'.\nFound overall trends:",
            *map(str, self.list_overall_trends()),
        ]
        raise RuntimeError("\n- ".join(msg))

    def get_global_trend_curve(self, property_name: str) -> Curve:
        """
        Return a global trend.
        """
        metadata = self.metadata
        for trend_key, trend_metadata in metadata.trends.items():
            if (trend_metadata["property_id"] == property_name) and (
                trend_metadata["network_element_name"] is None
            ):
                return self._read_trend(trend_key)

        msg = [
            f"Can not locate '{property_name}' global trend.\nFound global trends:",
            *map(str, self.list_global_trends()),
        ]
        raise RuntimeError("\n- ".join(msg))

    def list_positional_trends(self) -> Sequence[PositionalTrendMetadata]:
        """
        List the collected positional trends.
        """
        metadata = self.metadata
        return [
            PositionalTrendMetadata(
                trend_metadata["property_id"],
                trend_metadata["network_element_name"],
                Scalar(trend_metadata["position"], "m"),
            )
            for trend_metadata in metadata.trends.values()
            if "position" in trend_metadata
        ]

    def list_overall_trends(self) -> Sequence[OverallTrendMetadata]:
        """
        List the collected overall trends.
        """
        metadata = self.metadata
        return [
            OverallTrendMetadata(
                trend_metadata["property_id"],
                trend_metadata["network_element_name"],
            )
            for trend_metadata in metadata.trends.values()
            if (
                (trend_metadata["network_element_name"] is not None)
                and ("position" not in trend_metadata)
            )
        ]

    def list_global_trends(self) -> Sequence[GlobalTrendMetadata]:
        """
        List the collected global trends.
        """
        metadata = self.metadata
        return [
            GlobalTrendMetadata(trend_metadata["property_id"])
            for trend_metadata in metadata.trends.values()
            if (trend_metadata["network_element_name"] is None)
        ]

    def get_profile_curve(
        self, property_name: str, element_name: str, index: int
    ) -> Curve:
        """
        Return a profile curve at a given time step index.
        """
        metadata = self.metadata
        for profile_key, profile_metadata in metadata.profiles.items():
            if (profile_metadata["property_id"] == property_name) and (
                profile_metadata["network_element_name"] == element_name
            ):
                return self._read_profile(profile_key, index)

        msg = [
            f"Can not locate '{property_name}' profile for element '{element_name}'.\nFound profiles:",
            *map(str, self.list_profiles()),
        ]
        raise RuntimeError("\n- ".join(msg))

    def list_profiles(self) -> Sequence[ProfileMetadata]:
        """
        List the collected profiles (and how many timesteps are present).
        """
        metadata = self.metadata

        def get_profile_metadata(meta: Dict) -> ProfileMetadata:
            # This is not a simple string formatting because we need to
            # calculate the time set size.
            time_set_info = metadata.time_set_info["profiles"]
            time_set_key = meta["time_set_key"]
            time_set_size = sum(time_set_info[base_ts].size for base_ts in time_set_key)
            return ProfileMetadata(
                meta["property_id"],
                meta["network_element_name"],
                time_set_size,
            )

        return [
            get_profile_metadata(profile_metadata)
            for profile_metadata in metadata.profiles.values()
        ]


def _non_empty_dict_validator(values_type: type) -> Callable:
    def validator(inst: Any, attribute: attr.Attribute, value: Any) -> None:
        attr.validators.min_len(1)(inst, attribute, value)
        attr.validators.instance_of(dict)(inst, attribute, value)
        assert isinstance(value, dict)

        some_dict_value = list(value.values())[0]
        if not isinstance(some_dict_value, values_type):
            raise ValueError(
                f"values of dict attribute `{attribute.name}` should be of type {values_type},"
                f" received: {type(some_dict_value)}"
            )

    return validator


def _non_empty_attr_validator(attr_name: str) -> Callable:
    def validator(inst: Any, attribute: attr.Attribute, value: Any) -> None:
        attr.validators.min_len(1)(inst, attribute, getattr(value, attr_name))

    return validator


@define(frozen=True, eq=False)
class GlobalSensitivityAnalysisResults:
    timeset: np.ndarray = attr.field(validator=attr.validators.min_len(1))
    coefficients: dict[GSAOutputKey, np.ndarray] = attr.field(
        validator=attr.validators.min_len(1)
    )
    metadata: GlobalSensitivityAnalysisMetadata = attr.field(
        validator=_non_empty_attr_validator("items")
    )

    @classmethod
    def from_directory(cls, result_dir: Path) -> Self | None:
        metadata = read_global_sensitivity_analysis_meta_data(result_dir)
        if metadata is None:
            return None

        return cls(
            timeset=read_uq_time_set(
                result_dir, GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME
            ),
            coefficients=read_global_sensitivity_coefficients(metadata),
            metadata=metadata,
        )

    def get_sensitivity_curve(
        self, property_name: str, element_name: str, parametric_var_id: str
    ) -> Curve:
        output_key = GSAOutputKey(
            property_name=property_name,
            element_name=element_name,
            parametric_var_id=parametric_var_id,
        )
        meta = self.metadata.items[output_key]
        coefficients = self.coefficients[output_key]
        image = Array(meta.category, values=coefficients, unit=meta.unit)
        domain = Array(self.timeset, "s")
        return Curve(image=image, domain=domain)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, GlobalSensitivityAnalysisResults):
            return False

        return (
            np.array_equal(self.timeset, other.timeset)
            and _all_dict_close(self.coefficients, other.coefficients)
            and self.metadata == other.metadata
        )


def _all_dict_close(a: dict[Any, np.ndarray], b: dict[Any, np.ndarray]) -> bool:
    if a.keys() != b.keys():
        return False
    return all(np.array_equal(a[key], b[key]) for key in a)


@define(frozen=True)
class _BaseHistoryMatchingResults:
    historic_data_curves: dict[str, tuple[HistoricDataCurveMetadata, Curve]]
    metadata: HistoryMatchingMetadata = attr.field(
        validator=_non_empty_attr_validator("hm_items")
    )


@define(frozen=True)
class HistoryMatchingDeterministicResults(_BaseHistoryMatchingResults):
    deterministic_values: dict[HMOutputKey, float] = attr.field(
        validator=_non_empty_dict_validator(values_type=float)
    )

    @classmethod
    def from_directory(cls, result_dir: Path) -> Self | None:
        metadata = read_history_matching_metadata(result_dir)
        if metadata is None:
            return None

        return cls(
            deterministic_values=read_history_matching_result(
                metadata, "HM-deterministic"
            ),
            historic_data_curves=_read_curves_data(metadata),
            metadata=metadata,
        )


@define(frozen=True, eq=False)
class HistoryMatchingProbabilisticResults(_BaseHistoryMatchingResults):
    probabilistic_distributions: dict[HMOutputKey, np.ndarray] = attr.field(
        validator=_non_empty_dict_validator(values_type=np.ndarray)
    )

    @classmethod
    def from_directory(cls, result_dir: Path) -> Self | None:
        metadata = read_history_matching_metadata(result_dir)
        if metadata is None:
            return None

        return cls(
            probabilistic_distributions=read_history_matching_result(
                metadata, "HM-probabilistic"
            ),
            historic_data_curves=_read_curves_data(metadata),
            metadata=metadata,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, HistoryMatchingProbabilisticResults):
            return False

        return (
            _all_dict_close(
                self.probabilistic_distributions, other.probabilistic_distributions
            )
            and self.historic_data_curves == other.historic_data_curves
            and self.metadata == other.metadata
        )


def _read_curves_data(
    metadata: HistoryMatchingMetadata,
) -> dict[str, tuple[HistoricDataCurveMetadata, Curve]]:
    raw_curves = read_history_matching_historic_data_curves(metadata)
    curves_info = metadata.historic_data_curve_infos or []
    curves_info_map = {info.curve_id: info for info in curves_info}

    result: dict[str, tuple[HistoricDataCurveMetadata, Curve]] = {}
    for curve_id, raw_curve in raw_curves.items():
        info = curves_info_map[curve_id]
        image = Array(info.image_category, raw_curve[0], info.image_unit)
        domain = Array("time", raw_curve[1], info.domain_unit)
        result[curve_id] = (info, Curve(image, domain))
    return result


@define(frozen=True, eq=False)
class UncertaintyPropagationResults:
    timeset: np.ndarray = attr.field(validator=attr.validators.min_len(1))
    results: dict[UPOutputKey, UPResult] = attr.field(
        validator=_non_empty_dict_validator(UPResult)
    )
    metadata: UncertaintyPropagationAnalysesMetaData = attr.field(
        validator=_non_empty_attr_validator("items")
    )

    @classmethod
    def from_directory(cls, result_dir: Path) -> Self | None:
        metadata = read_uncertainty_propagation_analyses_meta_data(result_dir)
        if metadata is None:
            return None

        return cls(
            timeset=read_uq_time_set(result_dir, UNCERTAINTY_PROPAGATION_GROUP_NAME),
            results=read_uncertainty_propagation_results(metadata),
            metadata=metadata,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, UncertaintyPropagationResults):
            return False

        return (
            np.array_equal(self.timeset, other.timeset)
            and self.results == other.results
            and self.metadata == other.metadata
        )
