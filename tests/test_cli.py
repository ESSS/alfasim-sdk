from click.testing import CliRunner

from alfasim_sdk import cli


def test_command_line_interface():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output


def test_command_package(tmpdir):
    import sys
    from pathlib import Path

    runner = CliRunner()
    plugin_dir = Path(tmpdir / "acme")
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
            f"--dst={Path(tmpdir)}",
        ],
    )

    # Creating a fake compile.py file and a fake shared library
    (plugin_dir / "compile.py").write_text(data="", encoding="utf-8")
    artifacts_dir.mkdir()
    lib_file.write_text("", encoding="utf-8")

    result = runner.invoke(
        cli.main,
        [
            "package",
            "--package-name=Acme",
            f"--plugin-dir={plugin_dir}",
            f"--dst={plugin_dir}",
        ],
    )

    assert result.output == ""
    assert result.exit_code == 0


def test_command_template(tmpdir):
    from pathlib import Path

    runner = CliRunner()
    result = runner.invoke(
        cli.main,
        [
            "template",
            "--caption=Acme",
            "--plugin-id=acme",
            "--author-email=acme@acme.com",
            "--author-name=ACME",
            f"--dst={Path(tmpdir)}",
        ],
    )
    assert result.output == ""
    assert result.exit_code == 0


def test_compile_command(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli.main, ["compile", "--plugin-dir", tmpdir])
    assert (
        f"Was not possible to find a compile.py file in {tmpdir}"
        == result.exception.args[0]
    )

    (tmpdir / "compile.py").write_text(data="", encoding="utf-8")
    result = runner.invoke(cli.main, ["compile", "--plugin-dir", tmpdir])
    assert result.exception is None
    assert result.output == ""
