import os
import subprocess
import sys
from pathlib import Path

import click

from hookman.hookman_generator import HookManGenerator

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """
    Console script for alfasim-sdk.
    """
    pass


@main.command()
@click.option('--dst',
    default=os.getcwd(),
    type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
    help='Path to where the template generated should be placed')
@click.option('--plugin-name', prompt='-- Plugin Name', help='Name of the plugin to be displayed')
@click.option('--shared-lib-name', prompt='-- Shared Library Name', help='The filename of the compiled plugin')
@click.option('--author-name', prompt='-- Author Name', help='Name of the plugin author to be displayed')
@click.option('--author-email', prompt='-- Author Email', help='Email of the plugin author to be displayed')
def template(dst, plugin_name, shared_lib_name, author_name, author_email,):
    """
    Console script for alfasim_sdk.
    """
    dst = Path(dst)
    hook_specs_file_path = _get_hook_specs_file_path()
    hm = HookManGenerator(hook_spec_file_path=hook_specs_file_path)
    hm.generate_plugin_template(plugin_name, shared_lib_name, author_email, author_name, dst)


@main.command()
@click.option('--src',
    default=os.getcwd(),
    type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
    help='Path to where the plugin folder is located')
def compile(src):
    src = Path(src)
    build_script = src / 'build.py'
    if not build_script.is_file():
        raise FileNotFoundError(f"Was not possible to find a build.py file in {src}")

    subprocess.run(['python', str(build_script)])


@click.option('--plugin-dir',
    type=click.Path(exists=True,resolve_path=True),
    help='Path to the plugin directory, where configuration and the shared library is located.' )
def package(plugin_dir):
    if plugin_dir is None:
        plugin_dir = Path(os.getcwd())
    plugin_dir = Path(plugin_dir)

    hook_specs_file_path = _get_hook_specs_file_path()
    hm = HookManGenerator(hook_spec_file_path=hook_specs_file_path)
    hm.generate_plugin_package(plugin_dir)
    return 0

def _get_hook_specs_file_path():
    import importlib
    hook_spec = importlib.util.find_spec('alfasim_sdk.hook_specs')
    hook_spec_path = Path(hook_spec.origin)
    return hook_spec_path


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
