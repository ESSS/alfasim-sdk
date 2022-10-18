import shutil
import textwrap
from pathlib import Path
from typing import List

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch


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
def abx_plugin(abx_plugin_source: Path, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ALFASIM_PLUGINS_DIR", str(abx_plugin_source))
