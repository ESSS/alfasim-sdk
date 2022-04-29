from barril.units import Array

from alfasim_sdk import get_profile_from_profile_id
from alfasim_sdk import get_time_set_and_trend_from_trend_id
from alfasim_sdk import load_result_files
from alfasim_sdk import META_GROUP_NAME
from alfasim_sdk import read_metadata
from alfasim_sdk import read_profiles_domain_data
from alfasim_sdk import RESULTS_FOLDER_NAME


def test_read_results(datadir, num_regression):
    """ "TODO: arthur: Improve/evolve this test"""

    curve_name = "pressure"

    results_metadata = read_metadata(datadir / RESULTS_FOLDER_NAME)

    trend_ids = [key for key in results_metadata.trends.keys() if curve_name in key]
    profile_ids = [key for key in results_metadata.profiles.keys() if curve_name in key]

    trend_id = trend_ids[0]
    profile_id = profile_ids[0]

    time_set, trend = get_time_set_and_trend_from_trend_id(trend_id, results_metadata)

    obtained_trends = {
        "domain [h]": time_set.GetValues("h"),
        "image [bar]": trend.GetValues("bar"),
    }
    num_regression.check(obtained_trends, basename="trends")

    def get_last_time_set_index():
        time_set_info = results_metadata.time_set_info["profiles"]
        time_set_key = results_metadata.profiles[profile_id]["time_set_key"]
        total_time_steps = sum(
            (
                info.size
                for base_ts, info in time_set_info.items()
                if base_ts in time_set_key
            ),
            0,
        )
        last_ts_index = total_time_steps - 1

        return last_ts_index

    profile_domain, profile_image = get_profile_from_profile_id(
        profile_id, results_metadata, timestep_id=get_last_time_set_index()
    )

    obtained_profiles = {
        "domain [m]": profile_domain.GetValues("m"),
        "image [bar]": profile_image.GetValues("bar"),
    }
    num_regression.check(obtained_profiles, basename="profiles")
