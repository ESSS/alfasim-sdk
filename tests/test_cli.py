from alfasim_sdk import cli
from click.testing import CliRunner


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

def test_compile_command(tmpdir, mocker):
    import os
    mocker.patch.object(os, 'getcwd', return_value=tmpdir)

    runner = CliRunner()
    result = runner.invoke(cli.main, ['compile', '--src', tmpdir])
    assert f"Was not possible to find a build.py file in {tmpdir}" == result.exception.args[0]

    (tmpdir / 'build.py').write_text(data='', encoding='utf-8')
    result = runner.invoke(cli.main, ['compile', '--src', tmpdir])
    assert result.exception is None
    assert result.output == ''

