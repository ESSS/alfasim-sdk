import json
import os.path
import shutil
import textwrap
from pathlib import Path
from typing import Dict, List

import h5py
import numpy as np
import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch

from alfasim_sdk.result_reader.aggregator import (
    HISTORY_MATCHING_HISTORIC_DATA_GROUP_NAME,
)
from alfasim_sdk.result_reader.aggregator_constants import (
    GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME,
    HISTORY_MATCHING_DETERMINISTIC_DSET_NAME,
    HISTORY_MATCHING_GROUP_NAME,
    HISTORY_MATCHING_PROBABILISTIC_DSET_NAME,
    META_GROUP_NAME,
    TIME_SET_DSET_NAME,
    UNCERTAINTY_PROPAGATION_DSET_MEAN_RESULT,
    UNCERTAINTY_PROPAGATION_DSET_REALIZATION_OUTPUTS,
    UNCERTAINTY_PROPAGATION_DSET_STD_RESULT,
    UNCERTAINTY_PROPAGATION_GROUP_META_ATTR_NAME,
    UNCERTAINTY_PROPAGATION_GROUP_NAME,
)
from alfasim_sdk.result_reader.reader import Results

pytest_plugins = [
    "alfasim_sdk.testing.fixtures",
]


@pytest.fixture()
def results(datadir: Path, request: FixtureRequest) -> Results:
    """
    Result are composed by 3 files.
    The first 2 are contiguous results.
    The last 2 ones overlap, the last causes the previous tu be truncated.
    """
    repo_root = request.session.fspath
    sample_results_data_folder = repo_root / "sample_alfasim_result/project.data"
    test_data_folder = datadir / "project.data"
    assert not test_data_folder.exists()
    shutil.copytree(sample_results_data_folder, test_data_folder)
    assert test_data_folder.is_dir()
    return Results(test_data_folder)


@pytest.fixture()
def creating_results(results: Results) -> List[Path]:
    """
    This fixture will affect ``results`` where all the result files are in
    the "creating" state. The list of files returned can be removed to
    indicate the result files are "ready".
    """
    results_folder = results.results_folder
    creating_results_files = sorted(
        p.with_suffix(".creating") for p in results_folder.iterdir()
    )
    assert len(creating_results_files) == 3
    for p in creating_results_files:
        p.touch()
    return creating_results_files


@pytest.fixture()
def abx_plugin_source(datadir: Path) -> Path:
    """
    Create fake a plugin input model configuration.

    The input models consist of two top level containers "AContainer"
    and "BContainer" and the container children properties are:

    - asd (string);
    - qwe (string);

    The child model is called "X", that is the reason of the very
    creative name "abx" plugin.
    """
    plugin_root = datadir / "test_plugins"
    plugin_file = plugin_root / "abx/artifacts/abx.py"
    plugin_file.parent.mkdir(parents=True)
    plugin_file.write_text(
        textwrap.dedent(
            """\
            import alfasim_sdk

            @alfasim_sdk.data_model(icon="", caption="X")
            class X:
                asd = alfasim_sdk.String(value="some thing", caption="Asd")
                @alfasim_sdk.group(caption="Group Container")
                class AGroup:
                    qwe = alfasim_sdk.String(value="other thing", caption="Qwe")

            @alfasim_sdk.container_model(model=X, icon="", caption="A Cont.")
            class AContainer:
                pass

            @alfasim_sdk.container_model(model=X, icon="", caption="B Cont.")
            class BContainer:
                pass

            @alfasim_sdk.hookimpl
            def alfasim_get_data_model_type():
                return [AContainer, BContainer]
            """
        )
    )
    return plugin_root


@pytest.fixture()
def importable_plugin_source(datadir: Path) -> Path:
    """
    Create a fake plugin input model configuration.

    The input models consist of two top level containers "AContainer"
    and "BContainer" and the container children properties are:

    - asd (string);
    - qwe (string);

    The child model is called "X", that is the reason of the very
    creative name "abx" plugin.
    """
    plugin_root = datadir / "test_plugins"
    plugin_file = plugin_root / "importable/artifacts/importable.py"
    plugin_file.parent.mkdir(parents=True)
    plugin_file.write_text(
        textwrap.dedent(
            """\
            import alfasim_sdk
            from alfasim_sdk_plugins.importable.models import Foo

            @alfasim_sdk.hookimpl
            def alfasim_get_data_model_type():
                return [Foo]
            """
        )
    )
    namespace = plugin_file.parent / "alfasim_sdk_plugins"
    models_file = namespace / "importable/models.py"
    models_file.parent.mkdir(parents=True, exist_ok=True)
    models_file.write_text(
        textwrap.dedent(
            """\
            import alfasim_sdk

            @alfasim_sdk.data_model(icon="", caption="The Foo")
            class Foo:
                bar = alfasim_sdk.String(value="some default bar", caption="Bar")
            """
        )
    )
    buz_file = namespace / "importable/buz.py"
    buz_file.parent.mkdir(parents=True, exist_ok=True)
    buz_file.write_text("BUZ = 'fiz buz!'\n")
    return plugin_root


@pytest.fixture()
def clear_alfasim_plugins_dir(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("ALFASIM_PLUGINS_DIR", raising=False)


@pytest.fixture()
def abx_plugin(
    clear_alfasim_plugins_dir: None,
    abx_plugin_source: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "ALFASIM_PLUGINS_DIR",
        str(abx_plugin_source),
        prepend=os.path.pathsep,
    )


@pytest.fixture()
def importable_plugin(
    clear_alfasim_plugins_dir: None,
    importable_plugin_source: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "ALFASIM_PLUGINS_DIR",
        str(importable_plugin_source),
        prepend=os.path.pathsep,
    )


@pytest.fixture()
def global_sa_results_dir(datadir: Path) -> Path:
    """
    Crete a global sensitivity analysis result folder
    with a result file.
    """
    import numpy as np

    result_dir = datadir / "fake_uq_dir"
    result_dir.mkdir(parents=True)
    time_set = np.array([1, 2, 3, 4, 5, 6, 7])
    global_sensitivity_analysis = np.array(
        [
            [
                [qoi + var + tl for tl in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)]
                for var in [1, 2]
            ]
            for qoi in [10]
        ]
    )
    file_name = result_dir / "result"

    file = h5py.File(file_name, "x", libver="latest", locking=False)
    meta_group = file.create_group(META_GROUP_NAME, track_order=True)
    global_sensitivity_analysis_group = file.create_group(
        GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME, track_order=True
    )
    global_sensitivity_analysis_group.create_dataset(
        TIME_SET_DSET_NAME, shape=(0,), dtype=np.float64, maxshape=(None,)
    )
    global_sensitivity_analysis_group.create_dataset(
        GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME,
        shape=global_sensitivity_analysis.shape,
        dtype=np.float64,
        maxshape=(None, None, None),
    )

    fake_meta = {
        "temperature::parametric_var_1@trend_id_1": {
            "property_id": "temperature",
            "trend_id": "trend_id_1",
            "category": "dimensionless",
            "parametric_var_id": "parametric_var_id_1",
            "parametric_var_name": "A",
            "network_element_name": "Conexao 1",
            "position": 100.0,
            "position_unit": "m",
            "unit": "-",
            "qoi_index": 0,
            "qoi_data_index": 0,
        },
        "temperature::parametric_var_2@trend_id_1": {
            "property_id": "temperature",
            "trend_id": "trend_id_1",
            "category": "dimensionless",
            "parametric_var_id": "parametric_var_id_2",
            "parametric_var_name": "B",
            "network_element_name": "Conexao 1",
            "position": 100.0,
            "position_unit": "m",
            "unit": "-",
            "qoi_index": 0,
            "qoi_data_index": 1,
        },
    }

    meta_group.attrs["global_sensitivity_analysis"] = json.dumps(fake_meta)
    time_set_dset = global_sensitivity_analysis_group[TIME_SET_DSET_NAME]
    new_time_set_shape = time_set.shape
    time_set_dset.resize(new_time_set_shape)
    time_set_dset[:] = time_set
    gsa_data_set = global_sensitivity_analysis_group[
        GLOBAL_SENSITIVITY_ANALYSIS_GROUP_NAME
    ]
    gsa_data_set[:] = global_sensitivity_analysis
    file.close()
    return result_dir


@pytest.fixture()
def up_results_dir(datadir: Path) -> Path:
    """
    Crete a uncertainty propagation analyses result folder
    with a result file.
    """

    import numpy as np

    result_dir = datadir / "fake_dir"
    result_dir.mkdir(parents=True)
    time_set = np.array([0, 1, 2, 3, 4, 5, 6, 7])
    realization_outputs = np.array(
        [
            [
                [
                    i + (qoi_index * 10) + tl
                    for tl in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)
                ]
                for qoi_index, trend_property in enumerate(
                    [("trend_id_1", "temperature"), ("trend_id_1", "absolute_pressure")]
                )
            ]
            for i in range(5)
        ]
    )
    file_name = result_dir / "result"
    with h5py.File(file_name, "x", libver="latest", locking=False) as file:
        meta_group = file.create_group(META_GROUP_NAME, track_order=True)
        uncertainty_propagation_group = file.create_group(
            UNCERTAINTY_PROPAGATION_GROUP_NAME, track_order=True
        )
        fake_meta = {
            "temperature@trend_id_1": {
                "property_id": "temperature",
                "trend_id": "trend_id_1",
                "category": "temperature",
                "network_element_name": "Conexao 1",
                "position": 100.0,
                "position_unit": "m",
                "unit": "K",
                "samples": 5,
                "sample_indexes": [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]],
                "result_index": 0,
            },
            "absolute_pressure@trend_id_1": {
                "property_id": "absolute_pressure",
                "trend_id": "trend_id_1",
                "category": "pressure",
                "network_element_name": "Conexao 1",
                "position": 100.0,
                "position_unit": "m",
                "unit": "bar",
                "samples": 5,
                "sample_indexes": [[1, 0], [1, 1], [1, 2], [1, 3], [1, 4]],
                "result_index": 1,
            },
        }
        meta_group.attrs[UNCERTAINTY_PROPAGATION_GROUP_META_ATTR_NAME] = json.dumps(
            fake_meta
        )
        time_set_dset = uncertainty_propagation_group.create_dataset(
            name=TIME_SET_DSET_NAME, shape=time_set.shape
        )
        time_set_dset[:] = time_set

        realization_outputs_dset = uncertainty_propagation_group.create_dataset(
            name=UNCERTAINTY_PROPAGATION_DSET_REALIZATION_OUTPUTS,
            shape=realization_outputs.shape,
            maxshape=(None, None, None),
        )
        realization_outputs = realization_outputs
        realization_outputs_dset[:] = realization_outputs

        mean_results_array = np.mean(realization_outputs, axis=0)
        mean_results = uncertainty_propagation_group.create_dataset(
            name=UNCERTAINTY_PROPAGATION_DSET_MEAN_RESULT,
            shape=mean_results_array.shape,
            maxshape=(None, None),
        )
        mean_results[:] = mean_results_array

        std_results_array = np.std(realization_outputs, axis=0)
        std_results = uncertainty_propagation_group.create_dataset(
            name=UNCERTAINTY_PROPAGATION_DSET_STD_RESULT,
            shape=std_results_array.shape,
            maxshape=(None, None),
        )
        std_results[:] = std_results_array
        file.swmr_mode = True
    return result_dir


def _create_and_populate_hm_result_file(
    result_dir: Path,
    result: np.ndarray,
    result_dataset_key: str,
    historic_data_curves: Dict[str, np.ndarray],
) -> None:
    result_dir.mkdir(parents=True, exist_ok=True)
    result_filepath = result_dir / "result"

    with h5py.File(result_filepath, "x", libver="latest", locking=False) as file:
        meta_group = file.create_group(META_GROUP_NAME, track_order=True)
        result_group = file.create_group(HISTORY_MATCHING_GROUP_NAME, track_order=True)

        result_group.create_dataset(result_dataset_key, data=result)

        objective_functions = {
            "observed_curve_1": {"trend_id": "trend_1", "property_id": "holdup"},
            "observed_curve_2": {"trend_id": "trend_2", "property_id": "pressure"},
        }
        parametric_vars = {"mg": 0.5, "mo": 4.0}

        fake_meta = {
            "parametric_var_1": {
                "parametric_var_id": "parametric_var_1",
                "parametric_var_name": "mg",
                "min_value": 0.0,
                "max_value": 1.0,
                "objective_functions": objective_functions,
                "parametric_vars": parametric_vars,
                "data_index": 0,
            },
            "parametric_var_2": {
                "parametric_var_id": "parametric_var_2",
                "parametric_var_name": "mo",
                "min_value": 2.5,
                "max_value": 7.5,
                "objective_functions": objective_functions,
                "parametric_vars": parametric_vars,
                "data_index": 1,
            },
        }
        if historic_data_curves:
            historic_curves_group = file.create_group(
                HISTORY_MATCHING_HISTORIC_DATA_GROUP_NAME
            )
            for curve_id, curve in historic_data_curves.items():
                historic_curves_group.create_dataset(curve_id, data=curve)

            historic_curves_meta = [
                {
                    "curve_id": "observed_curve_1",
                    "curve_name": "curve 1",
                    "domain_unit": "s",
                    "image_unit": "m3/m3",
                    "image_category": "volume fraction",
                },
                {
                    "curve_id": "observed_curve_2",
                    "curve_name": "curve 2",
                    "domain_unit": "s",
                    "image_unit": "Pa",
                    "image_category": "pressure",
                },
            ]
            meta_entries = list(fake_meta.values())
            for entry in meta_entries:
                entry["historic_data_curves_info"] = historic_curves_meta

        meta_group.attrs[HISTORY_MATCHING_GROUP_NAME] = json.dumps(fake_meta)

        file.swmr_mode = True


@pytest.fixture()
def hm_probabilistic_results_dir(datadir: Path) -> Path:
    """
    Create a History Matching Probabilistic result folder with a populated HDF5 file.
    """
    import numpy as np

    result_dir = datadir / "main-HM-probabilistic"
    probabilistic_result = np.array(
        [[0.1, 3.0], [0.22, 6.0], [1.0, 5.1], [0.8, 4.7], [0.55, 6.3]]
    )
    historic_data_curves = {
        "observed_curve_1": np.array([[0.1, 0.5, 0.9], [1.1, 2.2, 3.3]]),
        "observed_curve_2": np.array([[1.0, 5.0, 9.0, 3.1], [1.2, 2.3, 3.4, 4.5]]),
    }

    _create_and_populate_hm_result_file(
        result_dir=result_dir,
        result=probabilistic_result,
        result_dataset_key=HISTORY_MATCHING_PROBABILISTIC_DSET_NAME,
        historic_data_curves=historic_data_curves,
    )

    return result_dir


@pytest.fixture()
def hm_deterministic_results_dir(datadir: Path) -> Path:
    """
    Create a History Matching Deterministic result folder with a populated HDF5 file.
    """
    import numpy as np

    result_dir = datadir / "main-HM-deterministic"
    deterministic_result = np.array([0.1, 3.2])
    historic_data_curves = {
        "observed_curve_1": np.array([[0.1, 0.5, 0.9], [1.1, 2.2, 3.3]]),
        "observed_curve_2": np.array([[1.0, 5.0, 9.0, 3.1], [1.2, 2.3, 3.4, 4.5]]),
    }

    _create_and_populate_hm_result_file(
        result_dir=result_dir,
        result=deterministic_result,
        result_dataset_key=HISTORY_MATCHING_DETERMINISTIC_DSET_NAME,
        historic_data_curves=historic_data_curves,
    )

    return result_dir


@pytest.fixture()
def hm_results_dir_without_historic_data(datadir: Path) -> Path:
    """
    Create a History Matching Deterministic result folder with a populated HDF5 file in the old
    format, i.e. without historic data curves.
    """
    import numpy as np

    result_dir = datadir / "main-HM-deterministic"
    deterministic_result = np.array([0.1, 3.2])

    _create_and_populate_hm_result_file(
        result_dir=result_dir,
        result=deterministic_result,
        result_dataset_key=HISTORY_MATCHING_DETERMINISTIC_DSET_NAME,
        historic_data_curves={},
    )

    return result_dir
