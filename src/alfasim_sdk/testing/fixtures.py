import os
import subprocess
import tempfile
import textwrap
import uuid
from pathlib import Path
from subprocess import CalledProcessError
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union

import pytest
import strictyaml
from _pytest.compat import assert_never
from _pytest.monkeypatch import MonkeyPatch

from alfasim_sdk import convert_alfacase_to_description
from alfasim_sdk import generate_alfacase_file
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

    def check_not_run(self) -> None:
        assert self._results is None, "Simulation already run"

    def check_base_case_is_loaded(self) -> None:
        assert self._case is not None, "Base case is not loaded"

    def check_base_case_is_not_loaded(self) -> None:
        assert self._case is None, "Base case already loaded"

    def check_can_load_base(self) -> None:
        self.check_not_run()
        self.check_base_case_is_not_loaded()

    def load_base_from_alfacase(self, *parts: Union[str, Path]) -> None:
        """
        Define the base case from an alfacase file.
        """
        self.check_can_load_base()
        self._case = convert_alfacase_to_description(Path(*parts))

    def load_base_from_case_description(
        self, case_description: CaseDescription
    ) -> None:
        """
        Define the base case from a CaseDescription.
        """
        self.check_can_load_base()
        self._case = case_description

    def add_plugin_folder(self, *parts: Union[str, Path]) -> None:
        """
        Define where the plugin files are installed.

        Alternatively one could just define the `ALFASIM_PLUGINS_DIR`
        environment variable.
        """
        self.check_not_run()

        folder = Path(*parts).absolute()
        assert folder.is_dir(), "Plugin folder does not exist"

        plugins_dir = os.environ.get("ALFASIM_PLUGINS_DIR", "")
        plugins_dir = str(folder) + os.path.pathsep + plugins_dir
        self.monkeypatch.setenv("ALFASIM_PLUGINS_DIR", plugins_dir)

    def add_plugin(self, plugin_conf: Union[str]) -> None:
        """
        Add the given plugin configuration to the case to be run.
        """
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
        """
        Run a simulation using the configured case and return a `Results`
        object to access the simulation result and log files.

        :param number_of_threads:
            The number of thread used to run the simulation (`-1` indicates
            to use one thread per virtual core, `0` disable parallelism).
        """
        self.check_not_run()
        self.check_base_case_is_loaded()

        self.alfacase_data_folder.mkdir()
        generate_alfacase_file(self._case, self.alfacase_file)

        try:
            self._run_simulator(
                self.get_runner()
                + [
                    "--run-simulation",
                    f"--alfacase-file={str(self.alfacase_file)}",
                    f"--number-of-threads={number_of_threads}",
                ],
                cwd=self.project_folder,
            )
        except CalledProcessError as error:

            def list_log(log_file):
                try:
                    contents = log_file.read_text()
                except (
                    Exception
                ) as e:  # pragma: no cover (usually the files can be read)
                    contents = f"<ERROR READING FILE: {str(e)}>"

                name = log_file.name
                header_len = 4 + len(name) + 4
                return f'{"=" * header_len}\n=== {log_file.name} ===\n{"=" * header_len}\n{contents}'

            results = Results(self.alfacase_data_folder)
            log_calc = results.log_calc
            log = results.log
            msg = "\n".join([list_log(log_calc), list_log(log)])
            raise RuntimeError(msg) from error
        finally:
            self._results = Results(self.alfacase_data_folder)

        return self.results

    def get_runner(self) -> List[str]:
        """
        Obtain the command line to run the simulation.

        Read the `ALFASIM_RUNNER` environment variable.
        """
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
        subprocess.run(command, cwd=str(cwd), env=current_env, check=True)


@pytest.fixture()
def alfasim_runner(
    datadir: Path,
    monkeypatch: MonkeyPatch,
) -> Iterator[AlfasimRunnerFixture]:
    yield AlfasimRunnerFixture(datadir, monkeypatch)
