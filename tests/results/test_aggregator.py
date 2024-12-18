import itertools
import json
import re
import shutil
from pathlib import Path
from typing import List
from typing import Literal

import attr
import h5py
import numpy
import pytest
from pytest import FixtureRequest
from pytest_mock import MockerFixture
from pytest_regressions.num_regression import NumericRegressionFixture

from alfasim_sdk.result_reader.aggregator import concatenate_metadata
from alfasim_sdk.result_reader.aggregator import HistoricDataCurveMetadata
from alfasim_sdk.result_reader.aggregator import HistoryMatchingMetadata
from alfasim_sdk.result_reader.aggregator import open_result_files
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
from alfasim_sdk.result_reader.aggregator import read_profiles_local_statistics
from alfasim_sdk.result_reader.aggregator import read_time_sets
from alfasim_sdk.result_reader.aggregator import read_trends_data
from alfasim_sdk.result_reader.aggregator import (
    read_uncertainty_propagation_analyses_meta_data,
)
from alfasim_sdk.result_reader.aggregator import read_uncertainty_propagation_results
from alfasim_sdk.result_reader.aggregator import (
    read_uq_time_set,
)
from alfasim_sdk.result_reader.aggregator import ResultsNeedFullReloadError
from alfasim_sdk.result_reader.aggregator import TimeSetInfoItem
from alfasim_sdk.result_reader.aggregator_constants import (
    GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME,
)
from alfasim_sdk.result_reader.aggregator_constants import HISTORY_MATCHING_GROUP_NAME
from alfasim_sdk.result_reader.aggregator_constants import META_GROUP_NAME
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
    with pytest.raises(PermissionError, match="Could not access the file"):
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


def test_fancy_path(datadir: Path, request: FixtureRequest):
    """
    Ensure the HDF5 version we are using can work with paths containing non-ascii characters (ASIM-5880).

    The setup is based on `results` fixture (from `conftest.py`).
    """
    repo_root = request.session.fspath
    sample_results_data_folder = repo_root / "sample_alfasim_result/project.data"
    test_data_folder = datadir / "fânçy_påtȟ.data"
    shutil.copytree(sample_results_data_folder, test_data_folder)
    results = Results(test_data_folder)
    # Try to read the results from the fancy named folder.
    assert set([p.property_name for p in results.list_profiles()]) == {
        "pressure",
        "total mass flow rate",
    }


def test_read_time_sets(
    results: Results, num_regression: NumericRegressionFixture
) -> None:
    time_sets = read_time_sets(results.metadata)
    num_regression.check({str(k): v for k, v in time_sets.items()})


def test_read_empty_gsa_metadata(datadir: Path) -> None:
    fake_uq_dir = datadir / "fake_uq_dir"

    uq_metadata = read_global_sensitivity_analysis_meta_data(
        result_directory=fake_uq_dir
    )
    assert uq_metadata.items == {}
    assert Path(uq_metadata.result_directory) == fake_uq_dir

    fake_uq_dir.mkdir(parents=True)
    uq_metadata = read_global_sensitivity_analysis_meta_data(
        result_directory=fake_uq_dir
    )
    assert uq_metadata.items == {}


def test_read_gsa_metadata(global_sa_results_dir: Path) -> None:
    uq_metadata = read_global_sensitivity_analysis_meta_data(global_sa_results_dir)
    global_gsa_meta_data = uq_metadata.items
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


def test_read_gsa_timeset(global_sa_results_dir: Path) -> None:
    time_set = read_uq_time_set(
        result_directory=global_sa_results_dir,
        group_name=GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME,
    )
    assert numpy.all(time_set == [0, 1, 2, 3, 4, 5, 6, 7])


def test_read_uq_global_sensitivity_analysis(global_sa_results_dir: Path) -> None:
    metadata = read_global_sensitivity_analysis_meta_data(global_sa_results_dir)
    data = read_global_sensitivity_coefficients(
        coefficients_key="temperature::parametric_var_1@trend_id_1",
        metadata=metadata,
    )
    assert numpy.all(data == (11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7))

    data = read_global_sensitivity_coefficients(
        coefficients_key="temperature::parametric_var_2@trend_id_1", metadata=metadata
    )
    assert numpy.all(data == (12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7))


def test_read_incomplete_gsa_metadata(global_sa_results_dir: Path) -> None:
    """
    When a .creating result file exists in the results folder,
    the metadata is incomplete, so they will be not read.
    """
    creating_file = global_sa_results_dir / "result.creating"
    creating_file.touch()
    gsa_time_set = read_uq_time_set(
        global_sa_results_dir, GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME
    )
    assert gsa_time_set is None
    gsa_meta_data = read_global_sensitivity_analysis_meta_data(global_sa_results_dir)
    assert gsa_meta_data.items == {}
    coefficients = read_global_sensitivity_coefficients(
        coefficients_key="temperature::parametric_var_1@trend_id_1",
        metadata=gsa_meta_data,
    )
    assert coefficients is None


def test_read_history_matching_result_metadata(
    hm_probabilistic_results_dir: Path,
    datadir: Path,
) -> None:
    """
    Check reading the HM metadata from a probabilistic result file, which should be enough to
    evaluate the deterministic metadata too as they are handled exactly the same.
    """
    hm_results_dir = hm_probabilistic_results_dir

    # Existent and completed result file, metadata should be filled.
    metadata = read_history_matching_metadata(hm_results_dir)

    assert metadata.result_directory == hm_results_dir
    assert metadata.objective_functions == {
        "observed_curve_1": {"trend_id": "trend_1", "property_id": "holdup"},
        "observed_curve_2": {"trend_id": "trend_2", "property_id": "pressure"},
    }
    assert metadata.parametric_vars == {"mg": 0.5, "mo": 4.0}
    assert metadata.historic_data_curve_infos == [
        HistoricDataCurveMetadata(
            curve_id="observed_curve_1",
            curve_name="curve 1",
            domain_unit="s",
            image_unit="m3/m3",
            image_category="volume fraction",
        ),
        HistoricDataCurveMetadata(
            curve_id="observed_curve_2",
            curve_name="curve 2",
            domain_unit="s",
            image_unit="Pa",
            image_category="pressure",
        ),
    ]

    expected_meta1 = HistoryMatchingMetadata.HMItem(
        parametric_var_id="parametric_var_1",
        parametric_var_name="mg",
        min_value=0.0,
        max_value=1.0,
        data_index=0,
    )

    expected_meta2 = HistoryMatchingMetadata.HMItem(
        parametric_var_id="parametric_var_2",
        parametric_var_name="mo",
        min_value=2.5,
        max_value=7.5,
        data_index=1,
    )

    items_meta = metadata.hm_items
    assert items_meta["parametric_var_1"] == expected_meta1
    assert items_meta["parametric_var_2"] == expected_meta2

    # Result file still being created, metadata should be empty.
    creating_file = hm_results_dir / "result.creating"
    creating_file.touch()

    metadata = read_history_matching_metadata(hm_results_dir)
    assert metadata.result_directory == hm_results_dir
    assert metadata.hm_items == {}

    creating_file.unlink()

    # Non-existent result directory, metadata should be empty.
    unexistent_result_dir = Path("foo/bar")
    metadata = read_history_matching_metadata(unexistent_result_dir)
    assert metadata.result_directory == unexistent_result_dir
    assert metadata.hm_items == {}

    # Not really expected, but existing result file with empty metadata content should also return
    # an empty metadata.
    result_path = datadir / "results"
    result_path.mkdir(parents=True, exist_ok=True)
    result_filepath = result_path / "result"

    with h5py.File(result_filepath, "x", libver="latest", locking=False) as file:
        meta_group = file.create_group(META_GROUP_NAME, track_order=True)
        meta_group.attrs[HISTORY_MATCHING_GROUP_NAME] = json.dumps({})

    metadata = read_history_matching_metadata(result_path)
    assert metadata.result_directory == result_path
    assert metadata.hm_items == {}


@pytest.mark.parametrize("hm_type", ("HM-probabilistic", "HM-deterministic"))
def test_read_history_matching_result_data(
    hm_probabilistic_results_dir: Path,
    hm_deterministic_results_dir: Path,
    hm_type: Literal["HM-probabilistic", "HM-deterministic"],
) -> None:
    """
    Check reading the result of both HM type analysis. Both results are available simultaneously by
    the means of the fixtures, but only one is used at a time.
    """
    import numpy as np

    # Setup.
    if hm_type == "HM-probabilistic":
        expected_results = {
            "parametric_var_1": np.array([0.1, 0.22, 1.0, 0.8, 0.55]),
            "parametric_var_2": np.array([3.0, 6.0, 5.1, 4.7, 6.3]),
        }
        results_dir = hm_probabilistic_results_dir
    else:
        assert hm_type == "HM-deterministic"
        expected_results = {"parametric_var_1": 0.1, "parametric_var_2": 3.2}
        results_dir = hm_deterministic_results_dir

    metadata = read_history_matching_metadata(results_dir)

    # Read the result of a single parametric var entry.
    result = read_history_matching_result(
        metadata, hm_type=hm_type, hm_result_key="parametric_var_1"
    )
    assert len(result) == 1
    assert len(result) == 1
    assert result["parametric_var_1"] == pytest.approx(
        expected_results["parametric_var_1"]
    )

    # Read the result of all entries.
    result = read_history_matching_result(metadata, hm_type=hm_type)
    assert len(result) == 2
    assert result["parametric_var_1"] == pytest.approx(
        expected_results["parametric_var_1"]
    )
    assert result["parametric_var_2"] == pytest.approx(
        expected_results["parametric_var_2"]
    )

    # Unexistent result key, result should be empty.
    result = read_history_matching_result(
        metadata, hm_type=hm_type, hm_result_key="foo"
    )
    assert result == {}

    # Result still being created, result should be empty.
    creating_file = results_dir / "result.creating"
    creating_file.touch()

    result = read_history_matching_result(metadata, hm_type=hm_type)
    assert result == {}

    creating_file.unlink()

    # Receiving an invalid History Matching type should raise.
    with pytest.raises(ValueError, match="type `foobar` not supported"):
        read_history_matching_result(metadata, "foobar")  # type: ignore


def test_read_history_matching_historic_data_curves(
    hm_probabilistic_results_dir: Path,
    hm_deterministic_results_dir: Path,
) -> None:
    """
    Check reading the historic data curves from the result file of both HM type analysis.
    """
    result_directories = (hm_probabilistic_results_dir, hm_deterministic_results_dir)
    for result_dir in result_directories:
        metadata = read_history_matching_metadata(result_dir)
        curves = read_history_matching_historic_data_curves(metadata)
        assert len(curves) == 2
        assert curves["observed_curve_1"] == pytest.approx(
            numpy.array([[0.1, 0.5, 0.9], [1.1, 2.2, 3.3]])
        )
        assert curves["observed_curve_2"] == pytest.approx(
            numpy.array([[1.0, 5.0, 9.0, 3.1], [1.2, 2.3, 3.4, 4.5]])
        )

    # For completeness, check result when passing some invalid directory.
    meta = HistoryMatchingMetadata.empty(result_directory=Path("foo"))
    assert read_history_matching_historic_data_curves(meta) == {}


def test_read_history_matching_historic_data_curves_backward_compatibility(
    hm_results_dir_without_historic_data: Path,
) -> None:
    """
    Check reading the historic data curves from an old result file which doesn't have historic data
    curves data in it (pre ASIM-5713).
    """
    result_dir = hm_results_dir_without_historic_data
    metadata = read_history_matching_metadata(result_dir)
    curves = read_history_matching_historic_data_curves(metadata)
    assert curves == {}


def test_read_uncertainty_propagation_results(
    datadir: Path, up_results_dir: Path, num_regression: NumericRegressionFixture
) -> None:
    empty_metadata = read_uncertainty_propagation_analyses_meta_data(
        result_directory=datadir
    )
    assert empty_metadata.items == {}
    result = read_uncertainty_propagation_results(
        metadata=empty_metadata, results_key="absolute_pressure@trend_id_1"
    )
    assert result is None

    metadata = read_uncertainty_propagation_analyses_meta_data(
        result_directory=up_results_dir
    )
    assert list(metadata.items.keys()) == [
        "temperature@trend_id_1",
        "absolute_pressure@trend_id_1",
    ]

    assert metadata.items["temperature@trend_id_1"].result_index == 0
    assert metadata.items["temperature@trend_id_1"].sample_indexes == [
        [0, 0],
        [0, 1],
        [0, 2],
        [0, 3],
        [0, 4],
    ]

    assert metadata.items["absolute_pressure@trend_id_1"].result_index == 1
    assert metadata.items["absolute_pressure@trend_id_1"].sample_indexes == [
        [1, 0],
        [1, 1],
        [1, 2],
        [1, 3],
        [1, 4],
    ]

    result = read_uncertainty_propagation_results(
        metadata=metadata, results_key="temperature@trend_id_1"
    )
    dict_1 = {
        "sample_0": result.realization_output[0],
        "sample_1": result.realization_output[-1],
        "mean_result": result.mean_result,
        "std_result": result.std_result,
    }
    num_regression.check(dict_1, basename="temperature@trend_id_1")
    result = read_uncertainty_propagation_results(
        metadata=metadata, results_key="absolute_pressure@trend_id_1"
    )
    dict_2 = {
        "sample_0": result.realization_output[0],
        "sample_1": result.realization_output[-1],
        "mean_result": result.mean_result,
        "std_result": result.std_result,
    }
    num_regression.check(dict_2, basename="absolute_pressure@trend_id_1")
