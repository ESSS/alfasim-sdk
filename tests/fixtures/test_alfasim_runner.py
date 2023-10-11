import textwrap
from pathlib import Path
from typing import Callable

import pytest
from _pytest.monkeypatch import MonkeyPatch

from alfasim_sdk.result_reader import Results
from alfasim_sdk.testing.fixtures import AlfasimRunnerFixture


@pytest.fixture(name="fake_alfasim_return_code")
def fake_alfasim_return_code_(monkeypatch: MonkeyPatch) -> Callable[[int], None]:
    """
    The fake simulator return code defaults to `0`.
    """

    def set_fake_alfasim_return_code(return_code: int) -> None:
        monkeypatch.setenv("FAKE_ALFASIM_RUNNER_RETURN_CODE", str(return_code))

    monkeypatch.setenv("FAKE_ALFASIM_RUNNER_RETURN_CODE", "0")
    return set_fake_alfasim_return_code


@pytest.fixture(name="fake_alfasim")
def fake_alfasim_(
    datadir: Path,
    monkeypatch: MonkeyPatch,
    alfasim_runner: AlfasimRunnerFixture,
    results: Results,
    fake_alfasim_return_code: Callable[[int], None],
) -> None:
    results_folder = alfasim_runner.alfacase_data_folder

    script_file = datadir / "fake_alfasim.py"
    script_file.write_text(
        textwrap.dedent(
            f"""\
            import os
            import sys
            from distutils.dir_util import copy_tree
            copy_tree(
                {str(results.data_folder)!r},
                {str(results_folder)!r},
            )
            return_code = os.environ.get("FAKE_ALFASIM_RUNNER_RETURN_CODE", "0")
            sys.exit(int(return_code))
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
    alfasim_runner.load_base_from_alfacase(empty_alfacase)
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


def test_alfasim_runner_from_case_description(
    alfasim_runner: AlfasimRunnerFixture,
    fake_alfasim: None,
    empty_alfacase: Path,
    abx_plugin_source: Path,
) -> None:
    from alfasim_sdk import convert_alfacase_to_description

    case_description = convert_alfacase_to_description(Path(empty_alfacase))
    alfasim_runner.load_base_from_case_description(case_description)
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


def test_alfasim_runner_invalid_results(
    alfasim_runner: AlfasimRunnerFixture,
    fake_alfasim: None,
    empty_alfacase: Path,
    fake_alfasim_return_code,
) -> None:
    alfasim_runner.load_base_from_alfacase(empty_alfacase)
    fake_alfasim_return_code(1)
    with pytest.raises(RuntimeError, match="run_simulation.*Reading study"):
        alfasim_runner.run()
