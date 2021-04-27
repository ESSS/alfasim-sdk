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
def console_main():
    pass


@console_main.command()
@destination_option(
    help="""
    A path to where the plugin project should be created.
    Default: Current directory
    """
)
@click.option(
    "--caption",
    prompt="-- Plugin Caption",
    help="Caption to be used across the application to identify the plugin",
)
@click.option("--plugin-id", prompt="-- Plugin Id", help="The name of the plugin")
@click.option(
    "--author-name",
    prompt="-- Author Name",
    help="Name of the plugin author, this value is stored in plugin metadata and not displayed on the application explicitly",
)
@click.option(
    "--author-email",
    prompt="-- Author Email",
    help="Email of the plugin author, this value is stored in plugin metadata and not displayed on the application explicitly",
)
def template(dst, caption, plugin_id, author_name, author_email):
    r"""
    Generate a template with the necessary files and structure to create a plugin.

    The template folder will be placed on the ``dst`` option, that by default is the current directory from where the command
    was invoked.

    The files generated and their contents are ready to be used or customized and have the following structure:

    .. code-block:: bash

        \---myplugin
        |   CMakeLists.txt
        |   compile.py
        |
        +---assets
        |       plugin.yaml
        |       README.md
        |
        \---src
            |   CMakeLists.txt
            |   hook_specs.h
            |   myplugin.cpp
            |
            \---python
                    myplugin.py

    """
    dst = Path(dst)
    hook_specs_file_path = _get_hook_specs_file_path()
    hm = HookManGenerator(hook_spec_file_path=hook_specs_file_path)
    alfasim_sdk_include = ["<alfasim_sdk_api/alfasim_sdk.h>"]
    default_impls_for_hooks = [
        "HOOK_INITIALIZE(ctx){",
        "    return 0;",
        "}",
        "HOOK_FINALIZE(ctx){",
        "    return 0;",
        "}",
    ]

    hm.generate_plugin_template(
        caption,
        plugin_id,
        author_email,
        author_name,
        dst,
        extra_includes=alfasim_sdk_include,
        extra_body_lines=default_impls_for_hooks,
        exclude_hooks=["HOOK_FINALIZE", "HOOK_INITIALIZE"],
    )

    source_folder = dst / plugin_id / "src"
    python_folder = source_folder / "python"
    python_folder.mkdir()
    Path(python_folder / f"{plugin_id}.py").touch()


@console_main.command(name="compile")
@plugin_dir_option
def _compile(plugin_dir):
    """
    Compile the plugin from the given plugin-dir option. When not provided plugin-dir will be the current folder location.

    This command basically calls the compile.py informing the location of the header files of alfasim_sdk_api.
    For more details about the build steps, check the compile.py generated for your plugin project.
    """
    plugin_dir = Path(plugin_dir)
    compile_script = plugin_dir / "compile.py"
    if not compile_script.is_file():
        raise FileNotFoundError(
            f"Was not possible to find a compile.py file in {plugin_dir}"
        )
    import alfasim_sdk

    env = os.environ.copy()
    env["SDK_INCLUDE_DIR"] = alfasim_sdk.get_alfasim_sdk_api_path()
    subprocess.check_call(["python", str(compile_script)], env=env)  # nosec


@console_main.command()
@click.pass_context
@plugin_dir_option
@destination_option(help="A path to where the output package should be created.")
@click.option("--package-name", prompt="-- Package Name", help="Name of the package")
def package(ctx, plugin_dir, package_name, dst):
    """
    Creates a new ``<package-name>.hmplugin`` file containing all the necessary files.

    This command will first invoke the ``compile`` command to generate the shared library, and after that, the plugin
    package will be generated with all the content available from the directory assets and artifacts.

    By default, the ``package`` command will assume that the plugin project is the current directory and the generated file
    will be placed also in the current directory.

    In order to change that, it's possible to use the options ``plugin-dir`` and ``dst``
    """
    ctx.invoke(_compile, plugin_dir=plugin_dir)
    ctx.invoke(package_only, plugin_dir=plugin_dir, package_name=package_name, dst=dst)


@console_main.command()
@click.pass_context
@plugin_dir_option
@destination_option(help="A path to where the output package should be created.")
@click.option("--package-name", prompt="-- Package Name", help="Name of the package")
def package_only(ctx, plugin_dir, package_name, dst):
    """
    Generate a ``<package_name>.hmplugin`` file with all the content from the directory assets and artifacts.

    By default, the package will be created inside the folder plugin_dir, however, it's possible
    to give another path filling the dst argument.
    """
    plugin_dir = Path(plugin_dir)
    dst = Path(dst)
    hook_specs_file_path = _get_hook_specs_file_path()
    hm = HookManGenerator(hook_spec_file_path=hook_specs_file_path)
    from alfasim_sdk._internal.constants import EXTRAS_REQUIRED_VERSION_KEY
    from alfasim_sdk._internal.alfasim_sdk_utils import (
        get_extras_default_required_version,
    )

    extras_defaults = {
        EXTRAS_REQUIRED_VERSION_KEY: get_extras_default_required_version()
    }
    hm.generate_plugin_package(
        package_name, plugin_dir, dst, extras_defaults=extras_defaults
    )


@console_main.command()
@click.pass_context
@plugin_dir_option
def update(ctx, plugin_dir):
    """
    Updates plugin files automatically generated by ALFAsim-SDK.
    The plugin folder is informed with plugin-dir option.
    When not provided plugin-dir will be the current folder location.

    It is important to update the automatically generated files from each plugin when
    a new version of ALFAsim-SDK is released. Otherwise compilation problems can occur.

    The files updated are: |br|
    - ´<plugin_folder>/src/hook_specs.h´ |br|
    """
    hook_specs_file_path = _get_hook_specs_file_path()
    hm = HookManGenerator(hook_spec_file_path=hook_specs_file_path)

    plugin_folder = Path(plugin_dir)
    hook_specs_h_path = plugin_folder / "src" / "hook_specs.h"

    if not hook_specs_h_path.exists() or not hook_specs_h_path.is_file():
        raise FileNotFoundError(
            f"Was not possible to find 'src/hook_specs.h' file in {plugin_dir}"
        )

    plugin_id = plugin_folder.name
    plugin_location = plugin_folder.parent
    hm.generate_hook_specs_header(plugin_id, plugin_location)


def _get_hook_specs_file_path() -> Path:
    import alfasim_sdk._internal.hook_specs

    return Path(alfasim_sdk._internal.hook_specs.__file__)


if __name__ == "__main__":
    sys.exit(console_main())  # pragma: no cover
