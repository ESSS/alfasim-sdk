import os
import subprocess
import sys
from pathlib import Path

import click
from hookman.hookman_generator import HookManGenerator

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

plugin_dir_option = click.option(
    "--plugin-dir",
    default=os.getcwd(),
    type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
    help="Path to the plugin directory, where configuration and the shared library is located.",
)


def destination_option(*, help):
    return click.option(
        "--dst",
        default=os.getcwd(),
        type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
        help=help,
    )


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """
    Console script for alfasim-sdk.
    """
    pass


@main.command()
@destination_option(help="A path to where the output package should be created.")
@click.option(
    "--caption",
    prompt="-- Plugin Caption",
    help="Caption to be used across the application to identify the plugin",
)
@click.option("--plugin-id", prompt="-- Plugin Id", help="The name of the plugin")
@click.option(
    "--author-name",
    prompt="-- Author Name",
    help="Name of the plugin author to be displayed",
)
@click.option(
    "--author-email",
    prompt="-- Author Email",
    help="Email of the plugin author to be displayed",
)
def template(dst, caption, plugin_id, author_name, author_email):
    """
    Console script for alfasim_sdk.
    """
    dst = Path(dst)
    hook_specs_file_path = _get_hook_specs_file_path()
    hm = HookManGenerator(hook_spec_file_path=hook_specs_file_path)
    alfasim_sdk_include = ["#include <alfasim_sdk_api/alfasim_sdk.h>"]
    hm.generate_plugin_template(
        caption,
        plugin_id,
        author_email,
        author_name,
        dst,
        extra_includes=alfasim_sdk_include,
    )

    source_folder = dst / plugin_id / "src"
    python_folder = dst / plugin_id / "python"
    python_folder.mkdir()
    Path(source_folder / f"{plugin_id}.py").write_text("")


@main.command(name="compile")
@plugin_dir_option
def _compile(plugin_dir):
    plugin_dir = Path(plugin_dir)
    compile_script = plugin_dir / "compile.py"
    if not compile_script.is_file():
        raise FileNotFoundError(
            f"Was not possible to find a compile.py file in {plugin_dir}"
        )
    import alfasim_sdk

    _env = os.environ.copy()
    _env["SDK_INCLUDE_DIR"] = alfasim_sdk.get_alfasim_sdk_api_path()
    subprocess.check_call(["python", str(compile_script)], env=_env)  # nosec


@main.command()
@click.pass_context
@plugin_dir_option
@destination_option(help="A path to where the output package should be created.")
@click.option("--package-name", prompt="-- Package Name", help="Name of the package")
def package(ctx, plugin_dir, package_name, dst):
    ctx.invoke(_compile, plugin_dir=plugin_dir)
    ctx.invoke(package_only, plugin_dir=plugin_dir, package_name=package_name, dst=dst)


@main.command()
@click.pass_context
@plugin_dir_option
@destination_option(help="A path to where the output package should be created.")
@click.option("--package-name", prompt="-- Package Name", help="Name of the package")
def package_only(ctx, plugin_dir, package_name, dst):
    plugin_dir = Path(plugin_dir)
    dst = Path(dst)
    hook_specs_file_path = _get_hook_specs_file_path()
    hm = HookManGenerator(hook_spec_file_path=hook_specs_file_path)
    hm.generate_plugin_package(package_name, plugin_dir, dst)


def _get_hook_specs_file_path() -> Path:
    import alfasim_sdk.hook_specs

    return Path(alfasim_sdk.hook_specs.__file__)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
