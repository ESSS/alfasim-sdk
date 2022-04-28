from alfasim_sdk import get_profile_from_profile_id
from alfasim_sdk import get_time_set_and_trend_from_trend_id
from alfasim_sdk import read_metadata
from alfasim_sdk import RESULTS_FOLDER_NAME


def test_read_results(datadir):
    curve_name = "pressure"

    results_metadata = read_metadata(datadir / RESULTS_FOLDER_NAME)

    trend_ids = [key for key in results_metadata.trends.keys() if curve_name in key]
    profile_ids = [key for key in results_metadata.profiles.keys() if curve_name in key]

    trend_id = trend_ids[0]
    profile_id = profile_ids[0]

    time_set, trend = get_time_set_and_trend_from_trend_id(trend_id, results_metadata)

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

    profile = get_profile_from_profile_id(
        profile_id, results_metadata, timestep_id=last_ts_index
    )
