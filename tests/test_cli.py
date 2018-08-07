from click.testing import CliRunner

from alfasim_sdk import cli


def test_command_line_interface():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_command_template(tmpdir):
    from pathlib import Path
    runner = CliRunner()
    result = runner.invoke(cli.main, [
        'template',
        '--plugin-name=Acme',
        '--shared-lib-name=acme',
        '--author-email=acme@acme.com',
        '--author-name=ACME',
        f'--dst={Path(tmpdir)}',
    ])
    assert result.output == ''
    assert result.exit_code == 0
