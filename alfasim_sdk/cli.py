import sys

import click


@click.command()
def main(args=None):
    """
    Console script for alfasim_sdk.
    """
    click.echo("ALFASim SDK")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
