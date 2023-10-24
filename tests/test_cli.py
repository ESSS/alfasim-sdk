from click.testing import CliRunner

from alfasim_sdk._internal.cli import console_main


def test_command_line_interface():
    runner = CliRunner()
    help_result = runner.invoke(console_main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output


def test_command_new(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        console_main,
        [
            "new",
            "--caption=Acme",
            "--plugin-id=acme",
            "--author-email=acme@acme.com",
            "--author-name=ACME",
            f"--dst={tmp_path}",
        ],
    )
    assert result.output == ""
    assert result.exit_code == 0

    plugin_dir = tmp_path / "acme"
    assets_dir = plugin_dir / "assets"
    compile_file = plugin_dir / "tasks.py"
    assert plugin_dir.is_dir()
    assert assets_dir.is_dir()
    assert compile_file.is_file()
