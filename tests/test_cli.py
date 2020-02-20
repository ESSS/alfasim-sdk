import os

from click.testing import CliRunner

from alfasim_sdk import cli


def test_command_line_interface():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output


def test_command_package(tmp_path, mocker):
    import sys

    runner = CliRunner()
    plugin_dir = tmp_path / "acme"
    artifacts_dir = plugin_dir / "artifacts"

    lib_name = "acme.dll" if sys.platform == "win32" else "libacme.so"
    lib_file = artifacts_dir / f"{lib_name}"

    runner.invoke(
        cli.main,
        [
            "template",
            "--caption=Acme",
            "--plugin-id=acme",
            "--author-email=acme@acme.com",
            "--author-name=ACME",
            f"--dst={tmp_path}",
        ],
    )

    # Creating a fake compile.py file and a fake shared library
    (plugin_dir / "compile.py").write_text(data="", encoding="utf-8")
    artifacts_dir.mkdir()
    lib_file.write_text("", encoding="utf-8")

    # Mocking _get_plugin_id_from_dll to pretend that the same plugin_id from yaml is the same inside the DLL
    from hookman.plugin_config import PluginInfo

    mocker.patch.object(
        PluginInfo,
        "_get_plugin_id_from_dll",
        side_effect=(lambda id_from_config_file: id_from_config_file),
    )

    result = runner.invoke(
        cli.main,
        [
            "package",
            "--package-name=acme",
            f"--plugin-dir={plugin_dir}",
            f"--dst={plugin_dir}",
        ],
    )

    assert result.output == ""
    assert result.exit_code == 0
    os_type = "win" if os.sys.platform == "win32" else "linux"
    package_filename = f"acme-1.0.0-{os_type}64.hmplugin"
    assert (plugin_dir / package_filename).is_file()


def test_command_template(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        cli.main,
        [
            "template",
            "--caption=Acme",
            "--plugin-id=acme",
            "--author-email=acme@acme.com",
            "--author-name=ACME",
            f"--dst={tmp_path}",
        ],
    )
    assert result.output == ""
    assert result.exit_code == 0


def test_compile_command(tmp_path):
    runner = CliRunner()
    result = runner.invoke(cli.main, ["compile", "--plugin-dir", tmp_path])
    assert (
        f"Was not possible to find a compile.py file in {tmp_path}"
        == result.exception.args[0]
    )

    (tmp_path / "compile.py").write_text(data="", encoding="utf-8")
    result = runner.invoke(cli.main, ["compile", "--plugin-dir", tmp_path])
    assert result.exception is None
    assert result.output == ""
