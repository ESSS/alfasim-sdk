import os
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
    default=None,
    type=click.Path(exists=True, dir_okay=True, writable=True, resolve_path=True),
    help='Path to where the template generated should be placed')
@click.option('--plugin-name', prompt='-- Plugin Name', help='Name of the plugin to be displayed')
@click.option('--shared-lib-name', prompt='-- Shared Library Name', help='The filename of the compiled plugin')
@click.option('--author-name', prompt='-- Author Name', help='Name of the plugin author to be displayed')
@click.option('--author-email', prompt='-- Author Email', help='Email of the plugin author to be displayed')
def template(dst, plugin_name, shared_lib_name, author_name, author_email,):
    """
    Console script for alfasim_sdk.
    """
    if dst is None:
        dst = Path(os.getcwd())
    dst = Path(dst)
    import importlib
    hook_spec = importlib.util.find_spec('alfasim_sdk.hook_specs')
    hook_spec_path = Path(hook_spec.origin)
    hm = HookManGenerator(hook_spec_file_path=hook_spec_path)
    hm.generate_plugin_template(plugin_name, shared_lib_name, author_email, author_name, dst)

    return 0

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
