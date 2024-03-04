import json
import os.path
import shutil
import textwrap
from pathlib import Path
from typing import List
from typing import Sequence
from typing import Tuple

import h5py
import numpy as np
import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch

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
from alfasim_sdk.result_reader.aggregator_constants import TIME_SET_DSET_NAME
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
    time_set = np.array([0, 1, 2, 3, 4, 5, 6, 7])
    global_sensitivity_analysis = np.array(
        [
            [
                [qoi + var + tl for tl in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)]
                for var in [1, 2]
            ]
            for qoi in [10]
        ]
    )
    file_name = result_dir / "uq_result"

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


def _create_and_populate_hm_result_file(
    result_dir: Path,
    result: np.ndarray,
    dataset_key: str,
    limits: Sequence[Tuple[float, float]],
) -> None:
    result_dir.mkdir(parents=True, exist_ok=True)
    result_filepath = result_dir / "result"

    file = h5py.File(result_filepath, "x", libver="latest", locking=False)
    meta_group = file.create_group(META_GROUP_NAME, track_order=True)
    data_group = file.create_group(HISTORY_MATCHING_GROUP_NAME, track_order=True)

    dataset = data_group.create_dataset(
        dataset_key,
        shape=result.shape,
        dtype=np.float64,
        maxshape=tuple(None for _ in result.shape),
    )

    objective_functions = {
        "observed_curve_1": {"trend_id": "trend_1", "property_id": "holdup"},
        "observed_curve_2": {"trend_id": "trend_2", "property_id": "pressure"},
    }

    fake_meta = {
        "parametric_var_1": {
            "parametric_var_id": "parametric_var_1",
            "parametric_var_name": "mg",
            "min_value": limits[0][0],
            "max_value": limits[0][1],
            "objective_functions": objective_functions,
            "data_index": 0,
        },
        "parametric_var_2": {
            "parametric_var_id": "parametric_var_2",
            "parametric_var_name": "mo",
            "min_value": limits[1][0],
            "max_value": limits[1][1],
            "objective_functions": objective_functions,
            "data_index": 1,
        },
    }

    meta_group.attrs[HISTORY_MATCHING_GROUP_NAME] = json.dumps(fake_meta)
    dataset[:] = result

    file.swmr_mode = True
    file.close()


@pytest.fixture()
def hm_probabilistic_results_dir(datadir: Path) -> Path:
    """
    Crete a History Matching result folder with a populated result file for each type of analysis
    (probabilistic and deterministic).
    """
    import numpy as np

    result_dir = datadir / "main-HM-probabilistic"
    probabilistic_result = np.array(
        [[0.1, 0.22, 1.0, 0.8, 0.55], [3.0, 6.0, 5.1, 4.7, 6.3]]
    )
    limits = [(0.0, 1.0), (2.5, 7.5)]

    _create_and_populate_hm_result_file(
        result_dir=result_dir,
        result=probabilistic_result,
        dataset_key=HISTORY_MATCHING_PROBABILISTIC_DSET_NAME,
        limits=limits,
    )

    return result_dir


@pytest.fixture()
def hm_deterministic_results_dir(datadir: Path) -> Path:
    """
    Crete a History Matching result folder with a populated result file for each type of analysis
    (probabilistic and deterministic).
    """
    import numpy as np

    result_dir = datadir / "main-HM-deterministic"
    deterministic_result = np.array([0.1, 3.2])
    limits = [(0.0, 1.0), (2.5, 7.5)]

    _create_and_populate_hm_result_file(
        result_dir=result_dir,
        result=deterministic_result,
        dataset_key=HISTORY_MATCHING_DETERMINISTIC_DSET_NAME,
        limits=limits,
    )

    return result_dir
