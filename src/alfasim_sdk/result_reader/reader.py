from pathlib import Path
from typing import Dict
from typing import Sequence
from typing import Tuple
from typing import Union

from attr import define
from barril.curve.curve import Curve
from barril.units import Array
from barril.units import Scalar

from alfasim_sdk.result_reader.aggregator import ALFASimResultMetadata
from alfasim_sdk.result_reader.aggregator import read_metadata
from alfasim_sdk.result_reader.aggregator import read_profiles_data
from alfasim_sdk.result_reader.aggregator import read_profiles_domain_data
from alfasim_sdk.result_reader.aggregator import read_time_sets
from alfasim_sdk.result_reader.aggregator import read_trends_data
from alfasim_sdk.result_reader.aggregator_constants import RESULTS_FOLDER_NAME


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

    def _read_profile_time_set(self, profile_key: str) -> Array:
        """
        Create a profile's timeset from the results.
        """
        metadata = self.metadata
        profile_metadata = metadata.profiles[profile_key]
        profile_time_set_key = profile_metadata["time_set_key"]
        time_set_key = ("profile_id", profile_time_set_key)
        time_sets = read_time_sets(metadata, [time_set_key])
        time_set = time_sets[time_set_key]
        return Array(values=time_set, unit=metadata.time_sets_unit, category="time")

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
            (
                f"Can not locate '{property_name}' trend for element '{element_name}'"
                f" at position '{position_m}'.\nFound positional trends:"
            ),
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
            (
                f"Can not locate overall '{property_name}' trend for element"
                f" '{element_name}'.\nFound overall trends:"
            ),
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

    def _get_profile_key(self, property_name: str, element_name: str) -> str:
        """
        Return the profile key (used to access the profile data in low level) for the
        given property and element.
        """
        metadata = self.metadata
        for profile_key, profile_metadata in metadata.profiles.items():
            if (profile_metadata["property_id"] == property_name) and (
                profile_metadata["network_element_name"] == element_name
            ):
                return profile_key

        msg = [
            (
                f"Can not locate '{property_name}' profile for element '{element_name}'."
                f"\nFound profiles:"
            ),
            *map(str, self.list_profiles()),
        ]
        raise RuntimeError("\n- ".join(msg))

    def get_profile_curve(
        self, property_name: str, element_name: str, index: int
    ) -> Curve:
        """
        Return a profile curve at a given time step index.
        """
        profile_key = self._get_profile_key(property_name, element_name)
        return self._read_profile(profile_key, index)

    def get_profile_time_set(self, property_name: str, element_name: str) -> Array:
        """
        Return the timeset for a given profile.
        """
        profile_key = self._get_profile_key(property_name, element_name)
        return self._read_profile_time_set(profile_key)

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
