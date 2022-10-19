import os
import subprocess
import tempfile
import textwrap
import uuid
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

import pytest
import strictyaml
from _pytest.compat import assert_never
from _pytest.monkeypatch import MonkeyPatch

from alfasim_sdk import convert_alfacase_to_description
from alfasim_sdk import convert_description_to_alfacase
from alfasim_sdk._internal.alfacase.alfacase_to_case import DescriptionDocument
from alfasim_sdk._internal.alfacase.case_description import CaseDescription
from alfasim_sdk._internal.alfacase.case_description_attributes import DescriptionError
from alfasim_sdk._internal.alfacase.plugin_alfacase_to_case import load_plugin
from alfasim_sdk._internal.alfacase.schema import plugin_description_schema
from alfasim_sdk.result_reader.reader import Results


class AlfasimRunnerFixture:
    def __init__(self, datadir: Path, monkeypatch: MonkeyPatch):
        self.datadir = datadir
        self.monkeypatch = monkeypatch
        self._project_folder: Optional[Path] = None
        self._case: Optional[CaseDescription] = None
        self._results: Optional[Results] = None

    @property
    def project_folder(self) -> Path:
        if self._project_folder is None:
            self._project_folder = Path(tempfile.mkdtemp(dir=self.datadir))
        return self._project_folder

    @property
    def alfacase_file(self) -> Path:
        return self.project_folder / "case.alfacase"

    @property
    def alfacase_data_folder(self) -> Path:
        return self.project_folder / "case.data"

    @property
    def results(self) -> Results:
        return self._results

    def check_not_run(self) -> bool:
        assert self._results is None, "Simulation already run"

    def check_base_case_is_loaded(self) -> bool:
        assert self._case is not None, "Base case is not loaded"

    def check_base_case_is_not_loaded(self) -> bool:
        assert self._case is None, "Base case already loaded"

    def load_base(self, *parts: Union[str, Path]) -> None:
        self.check_not_run()
        self.check_base_case_is_not_loaded()

        self._case = convert_alfacase_to_description(Path(*parts))

    def add_plugin_folder(self, *parts: Union[str, Path]) -> None:
        self.check_not_run()

        folder = Path(*parts).absolute()
        assert folder.is_dir(), "Plugin folder does not exist"

        plugins_dir = os.environ.get("ALFASIM_PLUGINS_DIR", "")
        plugins_dir = str(folder) + os.path.pathsep + plugins_dir
        self.monkeypatch.setenv("ALFASIM_PLUGINS_DIR", plugins_dir)

    def add_plugin(self, plugin_conf: Union[str]) -> None:
        self.check_not_run()
        self.check_base_case_is_loaded()

        if isinstance(plugin_conf, str):
            self.add_plugin_from_yaml(plugin_conf)
        else:
            assert_never(plugin_conf)  # pragma: no cover

    def add_plugin_from_yaml(self, plugin_conf: str) -> None:
        self.check_not_run()
        self.check_base_case_is_loaded()

        plugin_conf = textwrap.dedent(plugin_conf)
        try:
            content = strictyaml.dirty_load(
                yaml_string=plugin_conf,
                schema=plugin_description_schema,
                allow_flow_style=True,
            )
        except strictyaml.YAMLValidationError as e:  # pragma: no cover
            raise DescriptionError(str(e))

        alfacase_content = DescriptionDocument(content, self.alfacase_file)
        plugin_description = load_plugin(alfacase_content)
        assert plugin_description is not None, (
            "Can not load the plugin info,"
            " maybe you forgot to call `add_plugin_folder`"
        )
        self._case.plugins.append(plugin_description)

        plugins_names = [p.name for p in self._case.plugins]
        assert len(plugins_names) == len(set(plugins_names)), "\n- ".join(
            ["Plugins's configuration must be unique:", *plugins_names]
        )

    def run(self, *, number_of_threads: int = -1) -> Results:
        self.check_not_run()
        self.check_base_case_is_loaded()

        alfacase = convert_description_to_alfacase(self._case)
        project_folder = self.project_folder

        self.alfacase_data_folder.mkdir()
        self.alfacase_file.write_text(alfacase, encoding="utf-8")

        self._run_simulator(
            self.get_runner()
            + [
                "--run-simulation",
                f"--alfacase-file={str(self.alfacase_file)}",
                f"--number-of-threads={number_of_threads}",
            ],
            cwd=project_folder,
        )

        self._results = Results(self.alfacase_data_folder)
        return self.results

    def get_runner(self) -> List[str]:
        runner_from_env = os.environ.get("ALFASIM_RUNNER")
        assert runner_from_env is not None, (
            "Can not locate the simulator."
            " Set the environment variable 'ALFASIM_RUNNER'."
        )
        return runner_from_env.split(" ")

    def _run_simulator(self, command: List[str], cwd: Path) -> None:
        current_env = os.environ.copy()
        current_env["ALFASIM_PID_FILE_SECRET"] = f"testing-{uuid.uuid4()}"

        assert cwd.is_dir() and os.access(str(cwd), os.W_OK)
        proc = subprocess.Popen(command, cwd=str(cwd), env=current_env)
        proc.communicate()


@pytest.fixture()
def alfasim_runner(
    datadir: Path,
    monkeypatch: MonkeyPatch,
) -> AlfasimRunnerFixture:
    yield AlfasimRunnerFixture(datadir, monkeypatch)