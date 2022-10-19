import textwrap
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from alfasim_sdk.result_reader import Results
from alfasim_sdk.testing.fixtures import AlfasimRunnerFixture


@pytest.fixture(name="fake_alfasim")
def fake_alfasim_(
    datadir: Path,
    monkeypatch: MonkeyPatch,
    alfasim_runner: AlfasimRunnerFixture,
    results: Results,
) -> None:
    results_folder = alfasim_runner.alfacase_data_folder

    script_file = datadir / "fake_alfasim.py"
    script_file.write_text(
        textwrap.dedent(
            f"""\
            from distutils.dir_util import copy_tree
            copy_tree(
                {str(results.data_folder)!r},
                {str(results_folder)!r},
            )
            """
        )
    )
    monkeypatch.setenv("ALFASIM_RUNNER", f"python {str(script_file)}")


@pytest.fixture(name="empty_alfacase")
def empty_alfacase_(datadir: Path) -> Path:
    alfacase_file = datadir / "case.alfacase"
    alfacase_file.write_text("name: empty case")
    return alfacase_file


def test_alfasim_runner_fixture_creation(
    datadir: Path,
    monkeypatch: MonkeyPatch,
    alfasim_runner: AlfasimRunnerFixture,
) -> None:
    assert isinstance(alfasim_runner, AlfasimRunnerFixture)
    assert alfasim_runner.datadir is datadir
    assert alfasim_runner.monkeypatch is monkeypatch


def test_alfasim_runner_add_plugin(
    alfasim_runner: AlfasimRunnerFixture,
    fake_alfasim: None,
    empty_alfacase: Path,
    abx_plugin_source: Path,
) -> None:
    alfasim_runner.load_base(empty_alfacase)
    alfasim_runner.add_plugin_folder(abx_plugin_source)

    alfasim_runner.add_plugin(
        textwrap.dedent(
            """\
            name: abx
            """
        )
    )

    assert not alfasim_runner.alfacase_file.is_file()
    results = alfasim_runner.run()
    assert alfasim_runner.alfacase_file.is_file()
    assert len(results.list_profiles()) == 2
