import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List
from zipfile import ZipFile

import pytest
from _pytest.monkeypatch import MonkeyPatch

from alfasim_sdk._internal.alfasim_sdk_utils import get_current_version


plugin_id = "acme"
invoke_cmd = shutil.which("invoke")
alfasim_sdk_cmd = shutil.which("alfasim-sdk")


@pytest.fixture()
def new_plugin_dir(tmp_path: Path) -> Path:
    result = subprocess.run(
        [
            f"{alfasim_sdk_cmd}",
            "new",
            f"--caption={plugin_id.capitalize()}",
            f"--plugin-id={plugin_id}",
            f"--author-email={plugin_id}@test.com",
            f"--author-name={plugin_id.upper()}",
            f"--dst={tmp_path}",
        ],
        capture_output=True,
    )

    assert result.stdout.decode("utf-8") == ""
    assert result.stderr.decode("utf-8") == ""

    plugin_dir = tmp_path / plugin_id
    assert plugin_dir.is_dir()

    tasks_file = plugin_dir / "tasks.py"
    assert tasks_file.is_file()

    return plugin_dir


def test_compile_task(new_plugin_dir: Path, monkeypatch: MonkeyPatch):
    monkeypatch.chdir(new_plugin_dir)

    subprocess.run(
        [f"{invoke_cmd}", "compile"],
    )
    artifacts_dir = Path("artifacts")
    assert artifacts_dir.is_dir()

    lib_name = f"{plugin_id}.dll" if sys.platform == "win32" else f"lib{plugin_id}.so"
    lib_file = artifacts_dir / f"{lib_name}"
    assert lib_file.is_file()


def test_compile_clean_task(new_plugin_dir: Path, monkeypatch: MonkeyPatch):
    monkeypatch.chdir(new_plugin_dir)

    build_dir_old = new_plugin_dir / "build"
    build_dir_old.mkdir(exist_ok=True, parents=True)

    artifacts_dir_old = new_plugin_dir / "artifacts"
    artifacts_dir_old.mkdir(exist_ok=True, parents=True)

    subprocess.run(
        [
            f"{invoke_cmd}",
            "compile",
            "--clean",
        ],
    )
    artifacts_dir = Path("artifacts")
    assert artifacts_dir.is_dir()

    lib_name = f"{plugin_id}.dll" if sys.platform == "win32" else f"lib{plugin_id}.so"
    lib_file = artifacts_dir / f"{lib_name}"
    assert lib_file.is_file()


def test_compile_task_cmake_extra_args(new_plugin_dir: Path, monkeypatch: MonkeyPatch):
    monkeypatch.chdir(new_plugin_dir)

    cmake_extra_args = "-DMY_VARIABLE=TEST -DMY_OTHER_VARIABLE=TEST"

    result = subprocess.run(
        [f"{invoke_cmd}", "compile", "-c", cmake_extra_args, "--debug"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    message_chunk = "MY_VARIABLE"
    assert message_chunk in result.stdout.decode("utf-8")


def test_package_task(new_plugin_dir: Path, monkeypatch: MonkeyPatch):
    monkeypatch.chdir(new_plugin_dir)

    package_dir_old = new_plugin_dir / "package"
    package_dir_old.mkdir(exist_ok=True, parents=True)
    subprocess.run(
        [
            f"{invoke_cmd}",
            "package",
            f"--package-name={plugin_id}",
        ],
    )

    from alfasim_sdk._internal.alfasim_sdk_utils import get_current_version

    os_type = "win" if os.sys.platform == "win32" else "linux"
    curr_sdk_version = get_current_version()
    package_filename = Path(f"acme-1.0.0-sdk-{curr_sdk_version}-{os_type}64.hmplugin")
    assert package_filename.is_file()


def test_package_task_empty_package_name(
    new_plugin_dir: Path, monkeypatch: MonkeyPatch
):
    monkeypatch.chdir(new_plugin_dir)

    package_dir_old = new_plugin_dir / "package"
    package_dir_old.mkdir(exist_ok=True, parents=True)
    subprocess.run(
        [
            f"{invoke_cmd}",
            "package",
        ],
    )

    from alfasim_sdk._internal.alfasim_sdk_utils import get_current_version

    os_type = "win" if os.sys.platform == "win32" else "linux"
    curr_sdk_version = get_current_version()
    package_filename = Path(f"acme-1.0.0-sdk-{curr_sdk_version}-{os_type}64.hmplugin")
    assert package_filename.is_file()


def test_update_task(new_plugin_dir: Path, monkeypatch: MonkeyPatch):
    monkeypatch.chdir(new_plugin_dir)
    plugin_src_folder = new_plugin_dir / "src"
    plugin_hook_spec_h_path = plugin_src_folder / "hook_specs.h"

    # Erase previous created file
    plugin_hook_spec_h_path.write_text(data="", encoding="utf-8")
    assert plugin_hook_spec_h_path.stat().st_size == 0
    result = subprocess.run(
        [f"{invoke_cmd}", "update"],
        capture_output=True,
    )
    success_message_chunk = "Successfully updated alfasim-sdk's files"
    assert success_message_chunk in result.stdout.decode("utf-8")
    assert result.stderr.decode("utf-8") == ""
    assert plugin_hook_spec_h_path.stat().st_size > 0
    assert plugin_hook_spec_h_path.read_text(encoding="utf-8") != ""


def test_uninstall_plugin(
    new_plugin_dir: Path, tmp_path: Path, monkeypatch: MonkeyPatch
):
    monkeypatch.chdir(new_plugin_dir)
    install_dir = tmp_path / ".alfasim_plugins"
    plugin_dir = install_dir / plugin_id
    plugin_dir.mkdir(parents=True, exist_ok=True)
    assert plugin_dir.is_dir()

    subprocess.run(
        [f"{invoke_cmd}", "uninstall-plugin", "--install-dir", f"{install_dir}"]
    )
    assert not plugin_dir.is_dir()


def test_uninstall_plugin_user_folder(
    new_plugin_dir: Path, tmp_path: Path, monkeypatch: MonkeyPatch
):
    monkeypatch.chdir(new_plugin_dir)
    user_folder_env_var = "USERPROFILE" if sys.platform == "win32" else "HOME"
    env = {**os.environ, user_folder_env_var: str(tmp_path)}
    install_dir = tmp_path / ".alfasim_plugins"
    plugin_dir = install_dir / plugin_id
    plugin_dir.mkdir(parents=True, exist_ok=True)
    assert plugin_dir.is_dir()

    subprocess.run(
        [f"{invoke_cmd}", "uninstall-plugin"],
        env=env,
    )
    assert not plugin_dir.is_dir()


def test_uninstall_plugin_invalid_dir(
    new_plugin_dir: Path, tmp_path: Path, monkeypatch: MonkeyPatch
):
    monkeypatch.chdir(new_plugin_dir)
    install_dir = tmp_path / "invalid"
    install_dir.touch()  # Creating as file to produce an error

    result = subprocess.run(
        [f"{invoke_cmd}", "uninstall-plugin", "--install-dir", f"{install_dir}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    error_message_chunk = "is not a valid installation directory"
    assert error_message_chunk in result.stdout.decode("utf-8")


def get_plugin_installed_files(
    plugin_dir: Path, monkeypatch: MonkeyPatch
) -> List[Path]:
    """
    Get the files that are installed in the user folder when the user calls
    invoke install-plugin-to-user-folder
    """
    monkeypatch.chdir(plugin_dir)
    assets_dir = plugin_dir / "assets"
    artifacts_dir = plugin_dir / "artifacts"
    lib_name = f"{plugin_id}.dll" if sys.platform == "win32" else f"lib{plugin_id}.so"
    expected_files = [
        artifacts_dir / lib_name,
        artifacts_dir / f"{plugin_id}.py",
        assets_dir / "plugin.yaml",
        assets_dir / "README.md",
    ]
    return expected_files


def create_fake_hmplugin(plugin_dir: Path, monkeypatch: MonkeyPatch) -> Path:
    monkeypatch.chdir(plugin_dir)
    assets_dir = plugin_dir / "assets"
    assert assets_dir.is_dir()
    artifacts_dir = plugin_dir / "artifacts"
    artifacts_dir.mkdir()
    fake_files = get_plugin_installed_files(plugin_dir, monkeypatch)

    os_type = "win" if os.sys.platform == "win32" else "linux"
    curr_sdk_version = get_current_version()
    hmplugin_filename = Path(
        f"{plugin_id}-1.0.0-sdk-{curr_sdk_version}-{os_type}64.hmplugin"
    )

    with ZipFile(hmplugin_filename, "w") as package_file:
        for file in fake_files:
            file.write_text(data="", encoding="utf-8")
            package_file.write(file, arcname=file.relative_to(plugin_dir))

    return hmplugin_filename


def test_install_plugin(new_plugin_dir: Path, tmp_path: Path, monkeypatch: MonkeyPatch):
    fake_hmplugin = create_fake_hmplugin(new_plugin_dir, monkeypatch)
    assert fake_hmplugin.is_file()
    fake_hmplugin_files = get_plugin_installed_files(new_plugin_dir, monkeypatch)
    install_dir = tmp_path / ".alfasim_plugins"

    subprocess.run(
        [f"{invoke_cmd}", "install-plugin", "--install-dir", f"{install_dir}"]
    )

    monkeypatch.chdir(install_dir)
    for file in fake_hmplugin_files:
        relative_path = Path(
            plugin_id + "/" + file.parent.stem + "/" + file.stem + file.suffix
        )
        assert relative_path.is_file()


def test_install_plugin_user_folder(
    new_plugin_dir: Path, tmp_path: Path, monkeypatch: MonkeyPatch
):
    fake_hmplugin = create_fake_hmplugin(new_plugin_dir, monkeypatch)
    assert fake_hmplugin.is_file()
    fake_hmplugin_files = get_plugin_installed_files(new_plugin_dir, monkeypatch)

    user_folder_env_var = "USERPROFILE" if sys.platform == "win32" else "HOME"
    env = {**os.environ, user_folder_env_var: str(tmp_path)}
    install_dir = tmp_path / ".alfasim_plugins"

    subprocess.run([f"{invoke_cmd}", "install-plugin"], env=env)

    monkeypatch.chdir(install_dir)
    for file in fake_hmplugin_files:
        relative_path = Path(
            plugin_id + "/" + file.parent.stem + "/" + file.stem + file.suffix
        )
        assert relative_path.is_file()


def test_install_plugin_missing_plugin(new_plugin_dir: Path, monkeypatch: MonkeyPatch):
    monkeypatch.chdir(new_plugin_dir)

    result = subprocess.run(
        [f"{invoke_cmd}", "install-plugin"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    error_message_chunk = "Could not find any '*.hmplugin'"
    assert result.returncode == 1
    assert error_message_chunk in result.stdout.decode("utf-8")


def test_install_plugin_invalid_file(new_plugin_dir: Path, monkeypatch: MonkeyPatch):
    monkeypatch.chdir(new_plugin_dir)

    invalid_file = new_plugin_dir / "invalid.hmplugin"
    invalid_file.mkdir()  # Creating as a dir to force the error to happen
    result = subprocess.run(
        [f"{invoke_cmd}", "install-plugin"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    error_message_chunk = "is not valid"
    assert result.returncode == 1
    assert error_message_chunk in result.stdout.decode("utf-8")


def test_reinstall_plugin(
    new_plugin_dir: Path, tmp_path: Path, monkeypatch: MonkeyPatch
):
    fake_hmplugin_files = get_plugin_installed_files(new_plugin_dir, monkeypatch)
    monkeypatch.chdir(new_plugin_dir)
    install_dir = tmp_path / ".alfasim_plugins"
    plugin_dir = install_dir / plugin_id
    plugin_dir.mkdir(parents=True, exist_ok=True)
    assert plugin_dir.is_dir()

    subprocess.run(
        [
            f"{invoke_cmd}",
            "reinstall-plugin",
            "--package-name",
            f"{plugin_id}",
            "--install-dir",
            f"{install_dir}",
        ],
    )

    monkeypatch.chdir(install_dir)
    for file in fake_hmplugin_files:
        relative_path = Path(
            plugin_id + "/" + file.parent.stem + "/" + file.stem + file.suffix
        )
        assert relative_path.is_file()


def test_clean_task(new_plugin_dir: Path, monkeypatch: MonkeyPatch):
    monkeypatch.chdir(new_plugin_dir)
    build_folder = new_plugin_dir / "build"
    build_folder.mkdir(parents=True, exist_ok=True)
    assert build_folder.is_dir()

    # Test if a build folder of a child dir is removed as well
    extra_build_folder = new_plugin_dir / "src" / "build"
    extra_build_folder.mkdir(parents=True, exist_ok=True)
    assert extra_build_folder.is_dir()

    os_type = "win" if os.sys.platform == "win32" else "linux"
    curr_sdk_version = get_current_version()
    hm_plugin_file = Path(
        f"{plugin_id}-1.0.0-sdk-{curr_sdk_version}-{os_type}64.hmplugin"
    )
    hm_plugin_file.touch()
    assert hm_plugin_file.is_file()

    subprocess.run([f"{invoke_cmd}", "clean"])

    assert not build_folder.exists()
    assert not hm_plugin_file.exists()


@pytest.mark.skipif(
    sys.platform != "win32", reason="msvc task is only available on windows"
)
def test_msvc_task(new_plugin_dir: Path, monkeypatch: MonkeyPatch):
    from strictyaml.ruamel import YAML

    monkeypatch.chdir(new_plugin_dir)

    artifacts_dir = new_plugin_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    spec_file = new_plugin_dir / f"{plugin_id}.spec.yml"
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.dump({"msvc_compiler": "2022"}, spec_file)
    assert spec_file.is_file()
    assert spec_file.stat().st_size > 0

    subprocess.run([f"{invoke_cmd}", "msvc"])

    msvc_dir = new_plugin_dir / "msvc"
    sln_file = msvc_dir / (plugin_id + ".sln")
    assert msvc_dir.is_dir()
    assert sln_file.is_file()


@pytest.mark.skipif(
    sys.platform != "linux", reason="this test should be only run on linux"
)
def test_msvc_linux(new_plugin_dir: Path, monkeypatch: MonkeyPatch):
    monkeypatch.chdir(new_plugin_dir)

    result = subprocess.run(
        [f"{invoke_cmd}", "msvc"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    error_message = "msvc task only available on windows environment"
    assert result.returncode == 0
    assert error_message in result.stdout.decode("utf-8")
