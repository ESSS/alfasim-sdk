import os
import sys
from pathlib import Path
from textwrap import dedent

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
def new(dst, caption, plugin_id, author_name, author_email):
    r"""
    Generate a new plugin directory structure and files.

    The template folder will be placed on the ``dst`` option, that by default is the current directory from where the command
    was invoked.

    A ``tasks.py`` will be generated containing default tasks, and which can be further customized if needed.
    Run ``invoke --list`` to get a list of the available tasks.

    The files generated and their contents are ready to be used and have the following structure:

    .. code-block:: bash

        <dest>
        \---<plugin_id>
            |   CMakeLists.txt
            |   tasks.py
            |
            +---assets
            |       plugin.yaml
            |       README.md
            |
            \---src
                |   CMakeLists.txt
                |   hook_specs.h
                |   <plugin_id>.cpp
                |
                \---python
                    |   <plugin_id>.py
                    |
                    \---alfasim_sdk_plugins
                        \---<plugin_id>
                                __init__.py

    Any python code placed in ``alfasim_sdk_plugins/<plugin_id>`` is importable by using ``import alfasim_sdk_plugins.<plugin_id>.<my_extra_module>``.
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
    (python_folder / f"{plugin_id}.py").touch()

    importable_module = python_folder / "alfasim_sdk_plugins" / plugin_id
    importable_module.mkdir(parents=True)
    (importable_module / "__init__.py").touch()

    # remove compile.py created by hookman
    compile_file = dst / plugin_id / "compile.py"
    if compile_file.is_file():
        compile_file.unlink()

    # create tasks.py in the plugin root
    invoke_tasks_file = dst / plugin_id / "tasks.py"
    invoke_tasks_file.touch()
    invoke_tasks_file.open("w").write(_invoke_tasks_file_content())


def _get_hook_specs_file_path() -> Path:
    import alfasim_sdk._internal.hook_specs

    return Path(alfasim_sdk._internal.hook_specs.__file__)


def _invoke_tasks_file_content() -> str:
    return dedent(
        """\
        from alfasim_sdk.default_tasks import *
        from invoke import task

        # Customize this file with your own invoke tasks.
    """
    )


if __name__ == "__main__":
    sys.exit(console_main())  # pragma: no cover
