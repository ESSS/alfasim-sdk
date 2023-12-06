import os.path
import shutil
import textwrap
from pathlib import Path
from typing import List

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch

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
