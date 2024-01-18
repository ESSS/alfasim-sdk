import itertools
import re
from pathlib import Path
from typing import List

import attr
import numpy
import pytest
from pytest_mock import MockerFixture
from pytest_regressions.num_regression import NumericRegressionFixture

from alfasim_sdk.result_reader.aggregator import concatenate_metadata, read_global_sensitivity_analysis_meta_data, \
read_global_sensitivity_coefficients, read_global_sensitivity_analysis_time_set
from alfasim_sdk.result_reader.aggregator import open_result_files
from alfasim_sdk.result_reader.aggregator import read_metadata
from alfasim_sdk.result_reader.aggregator import read_profiles_local_statistics
from alfasim_sdk.result_reader.aggregator import read_time_sets
from alfasim_sdk.result_reader.aggregator import read_trends_data
from alfasim_sdk.result_reader.aggregator import ResultsNeedFullReloadError
from alfasim_sdk.result_reader.aggregator import TimeSetInfoItem
from alfasim_sdk.result_reader.aggregator_constants import RESULTS_FOLDER_NAME
from alfasim_sdk.result_reader.reader import Results


def test_read_empty_metadata_no_results(datadir: Path) -> None:
    fake_folder = datadir / "foo.data" / RESULTS_FOLDER_NAME

    md = read_metadata(fake_folder)
    initial_boundaries, final_boundaries = md.time_steps_boundaries
    assert (0, 0) == initial_boundaries == final_boundaries

    fake_folder.mkdir(parents=True)
    md = read_metadata(fake_folder)
    initial_boundaries, final_boundaries = md.time_steps_boundaries
    assert (0, 0) == initial_boundaries == final_boundaries


def test_read_metadata_from_results_sanity(results: Results) -> None:
    results_folder = results.results_folder
    md = read_metadata(results_folder)
    assert ((0, 0), (14, 62)) == md.time_steps_boundaries


def test_read_empty_metadata_creating_results(
    results: Results, creating_results: List[Path]
) -> None:
    results_folder = results.results_folder
    md = read_metadata(results_folder)
    assert ((0, 0), (0, 0)) == md.time_steps_boundaries


def test_read_metadata_need_reload_error(
    results: Results, creating_results: List[Path]
) -> None:
    results_folder = results.results_folder

    creating_results[0].unlink()  # Simulation has 1 result file.
    md = read_metadata(results_folder)

    # Use a fake time set info to simulate a simulation rerun.
    previous_time_set_info = {
        "profiles": {
            0: TimeSetInfoItem(global_start=0, size=5, uuid="fake-uuid"),
        },
        "trends": {
            0: TimeSetInfoItem(global_start=0, size=24, uuid="fake-uuid"),
        },
    }
    with pytest.raises(ResultsNeedFullReloadError):
        read_metadata(
            results_folder,
            previous_time_set_info=previous_time_set_info,
        )

    # Simulate a restart (now the results have two files).
    creating_results[1].unlink()
    with pytest.raises(ResultsNeedFullReloadError):
        read_metadata(results_folder, previous_time_set_info=md.time_set_info)

    # Simulate a restart (using a different reference).
    md = read_metadata(results_folder)
    creating_results[1].touch()
    creating_results[2].unlink()
    with pytest.raises(ResultsNeedFullReloadError):
        read_metadata(results_folder, previous_time_set_info=md.time_set_info)


def test_read_metadata_with_negative_bounds(results: Results) -> None:
    full_md = read_metadata(results.results_folder)
    assert full_md.profile_time_steps_boundaries == (0, 14)
    assert full_md.trends_time_steps_boundaries == (0, 62)

    partial_md = read_metadata(
        results.results_folder,
        initial_profiles_time_step_index=2,
        final_profiles_time_step_index=-2,
        initial_trends_time_step_index=10,
        final_trends_time_step_index=-10,
    )
    assert partial_md.profile_time_steps_boundaries == (2, 12)
    assert partial_md.trends_time_steps_boundaries == (10, 52)


def test_read_metadata_explict_empty(results: Results) -> None:
    md = read_metadata(
        results.results_folder,
        initial_profiles_time_step_index=2,
        final_profiles_time_step_index=2,
        initial_trends_time_step_index=10,
        final_trends_time_step_index=10,
    )
    assert md.time_steps_boundaries == ((2, 10), (2, 10))


@pytest.mark.parametrize(
    "index_arg_name",
    [
        "initial_profiles_time_step_index",
        "final_profiles_time_step_index",
        "initial_trends_time_step_index",
        "final_trends_time_step_index",
    ],
)
def test_read_metadata_invalid_index(results: Results, index_arg_name: str) -> None:
    expected_msg = f"`{index_arg_name}` (999) outside of valid range"
    with pytest.raises(IndexError, match=re.escape(expected_msg)):
        read_metadata(results.results_folder, **{index_arg_name: 999})


def test_concatenate_metadata_plain(results: Results) -> None:
    results_folder = results.results_folder

    md_a = read_metadata(
        results_folder,
        final_profiles_time_step_index=5,
        final_trends_time_step_index=40,
    )
    assert ((0, 0), (5, 40)) == md_a.time_steps_boundaries
    md_b = read_metadata(
        results_folder,
        initial_profiles_time_step_index=5,
        initial_trends_time_step_index=40,
    )
    assert ((5, 40), (14, 62)) == md_b.time_steps_boundaries

    md_c = concatenate_metadata(md_a, md_b)
    assert ((0, 0), (14, 62)) == md_c.time_steps_boundaries

    md_middle = read_metadata(
        results_folder,
        initial_profiles_time_step_index=5,
        initial_trends_time_step_index=40,
        final_profiles_time_step_index=5,
        final_trends_time_step_index=40,
    )
    md_aa = concatenate_metadata(md_a, md_middle)
    assert ((0, 0), (5, 40)) == md_aa.time_steps_boundaries
    md_bb = concatenate_metadata(md_middle, md_b)
    assert ((5, 40), (14, 62)) == md_bb.time_steps_boundaries


def test_concatenate_metadata_handle_time_sets(results: Results) -> None:
    results_folder = results.results_folder

    md_only_profile = read_metadata(
        results_folder,
        final_profiles_time_step_index=14,
        final_trends_time_step_index=0,
    )
    assert md_only_profile.time_sets == [("profile_id", (0, 2605, 4478))]
    md_only_trend = read_metadata(
        results_folder,
        initial_profiles_time_step_index=14,
        initial_trends_time_step_index=0,
    )
    assert md_only_trend.time_sets == [("trend_id", (0, 2605, 4478))]
    md_c = concatenate_metadata(md_only_profile, md_only_trend)
    assert md_c.time_sets == [
        ("profile_id", (0, 2605, 4478)),
        ("trend_id", (0, 2605, 4478)),
    ]


def test_concatenate_metadata_error_conditions_directory(results: Results) -> None:
    md = results.metadata
    other_md = attr.evolve(md, result_directory=md.result_directory / "other")
    with pytest.raises(RuntimeError, match="different sources"):
        concatenate_metadata(md, other_md)


def test_concatenate_metadata_error_conditions_more_files(
    results: Results, creating_results: List[Path]
) -> None:
    creating_results[0].unlink()
    md = results.metadata
    creating_results[1].unlink()
    other_md = read_metadata(results.results_folder)
    with pytest.raises(
        ResultsNeedFullReloadError, match="need to have matching number_of_files"
    ):
        concatenate_metadata(md, other_md)


def test_concatenate_metadata_error_conditions_not_adjacent(
    results: Results, creating_results: List[Path]
) -> None:
    creating_results[0].unlink()
    md = results.metadata
    creating_results[0].touch()
    creating_results[2].unlink()
    other_md = read_metadata(results.results_folder)
    with pytest.raises(RuntimeError, match="must be adjacent"):
        concatenate_metadata(md, other_md)


def test_cant_access_file_exception_handle(
    mocker: MockerFixture, results: Results
) -> None:
    mocker.patch("h5py.File", side_effect=PermissionError)
    with pytest.raises(PermissionError, match="Could not access folder"):
        with open_result_files(results.results_folder):
            assert False, "This should not be reached in this test"  # pragma: no cover


def test_file_not_swmr_exception_handle(
    mocker: MockerFixture, results: Results
) -> None:
    not_in_swmr_mode_smg = (
        "Unable to open file (file is not already open for SWMR writing)"
    )
    mocker.patch(
        "h5py.File",
        side_effect=itertools.cycle([OSError(not_in_swmr_mode_smg), mocker.Mock()]),
    )
    with open_result_files(results.results_folder) as files:
        assert files is not None


def test_load_result_files_creating(results: Results) -> None:
    # Sanity.
    assert (results.results_folder / "results_00000").is_file()
    assert (results.results_folder / "results_02605").is_file()
    assert (results.results_folder / "results_04478").is_file()
    assert not (results.results_folder / "results_00000.creating").is_file()
    assert not (results.results_folder / "results_02605.creating").is_file()
    assert not (results.results_folder / "results_04478.creating").is_file()
    # None result file is marked as "creating".
    with open_result_files(results.results_folder) as files:
        assert set(files) == {0, 2605, 4478}

    (results.results_folder / "results_04478.creating").touch()
    with open_result_files(results.results_folder) as files:
        assert set(files) == {0, 2605}

    (results.results_folder / "results_04478.txt").touch()
    with pytest.raises(ValueError):
        with open_result_files(results.results_folder):
            assert False, "This should not be reached in this test"  # pragma: no cover


def test_read_profiles_local_statistics(
    results: Results, num_regression: NumericRegressionFixture
) -> None:
    local_statistics = read_profiles_local_statistics(
        results.metadata, list(results.metadata.profiles.keys()), 0
    )
    num_regression.check(local_statistics)


def test_read_trends_data_bounds_check(results: Results) -> None:
    with pytest.raises(ValueError, match="Invalid initial_trends_time_step_index"):
        read_trends_data(results.metadata, initial_trends_time_step_index=999)

    with pytest.raises(ValueError, match="Invalid final_trends_time_step_index"):
        read_trends_data(results.metadata, final_trends_time_step_index=999)


def test_read_trends_data_empty_arrays_when_no_time_set_info(results: Results) -> None:
    fake_metadata = attr.evolve(results.metadata, time_set_info={})
    trends = read_trends_data(fake_metadata)
    base_id = "project.study_container.item00001.output_options.trend_out_definition_container"
    assert set(trends.keys()) == {
        f"pipe total liquid volume@{base_id}.item00003",
        f"mixture temperature@{base_id}.item00002",
        f"pressure@{base_id}.item00002",
        f"timestep@{base_id}.item00001",
    }
    assert all([len(trend_data) == 0 for trend_data in trends.values()])


def test_read_time_sets(
    results: Results, num_regression: NumericRegressionFixture
) -> None:
    time_sets = read_time_sets(results.metadata)
    num_regression.check({str(k): v for k, v in time_sets.items()})

def test_read_empty_uq_metadata(datadir: Path) -> None:
    fake_uq_dir = datadir / "fake_uq_dir"

    uq_metadata = read_global_sensitivity_analysis_meta_data(result_directory=fake_uq_dir)
    assert uq_metadata.gsa_items == {}
    assert Path(uq_metadata.result_directory) == fake_uq_dir

    fake_uq_dir.mkdir(parents=True)
    uq_metadata = read_global_sensitivity_analysis_meta_data(result_directory=fake_uq_dir)
    assert uq_metadata.gsa_items == {}

def test_read_uq_metadata(global_sa_results_dir: Path) -> None:
    uq_metadata = read_global_sensitivity_analysis_meta_data(global_sa_results_dir)
    global_gsa_meta_data = uq_metadata.gsa_items
    meta_var_1 = global_gsa_meta_data["temperature::parametric_var_1@trend_id_1"]
    assert meta_var_1.qoi_index == 0
    assert meta_var_1.qoi_data_index == 0
    assert meta_var_1.position == 100.0
    assert meta_var_1.parametric_var_name == "A"

    meta_var_2 = global_gsa_meta_data["temperature::parametric_var_2@trend_id_1"]
    assert meta_var_2.qoi_index == 0
    assert meta_var_2.qoi_data_index == 1
    assert meta_var_2.position == 100.0
    assert meta_var_2.parametric_var_name == "B"

def test_read_uq_timeset(global_sa_results_dir: Path) -> None:
    time_set = read_global_sensitivity_analysis_time_set(
        result_directory=global_sa_results_dir
    )
    assert numpy.all(time_set == [0, 1, 2, 3, 4, 5, 6, 7])


def test_read_uq_global_sensitivity_analysis(global_sa_results_dir: Path) -> None:
    metadata = read_global_sensitivity_analysis_meta_data(global_sa_results_dir)
    data = read_global_sensitivity_coefficients(
        coefficients_key="temperature::parametric_var_1@trend_id_1", metadata=metadata,
    )
    assert numpy.all(
        data
        == (11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7)
    )

    data = read_global_sensitivity_coefficients(
        coefficients_key="temperature::parametric_var_2@trend_id_1",metadata=metadata
    )
    assert numpy.all(
        data
        == (12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7)
    )


def test_read_incomplete_uq_metadata(global_sa_results_dir: Path) -> None:
    """
    When a .creating result file exists in the results folder,
    the metadata is incomplete, so they will be not read.
    """
    creating_file = global_sa_results_dir / 'uq_result.creating'
    creating_file.touch()
    gsa_time_set = read_global_sensitivity_analysis_time_set(global_sa_results_dir)
    assert gsa_time_set is None
    gsa_meta_data = read_global_sensitivity_analysis_meta_data(global_sa_results_dir)
    assert gsa_meta_data.gsa_items == {}
    coefficients = read_global_sensitivity_coefficients(coefficients_key="temperature::parametric_var_1@trend_id_1",metadata=gsa_meta_data)
    assert coefficients is None
