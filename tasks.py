from pathlib import Path

import invoke


@invoke.task
def build(ctx):
    """
    An umbrella task, currently only calls the cog
    """
    cog(ctx)


def schema_file_path() -> Path:
    return Path(__file__).parent / "alfasim_sdk/alfacase/schema.py"


@invoke.task(help={"check": "Check whether the schema has been modified or not"})
def cog(ctx, check=False):
    """ Executes cog on alfasim_sdk/alfacase/schema.py to generate the schema for strictyaml. """
    ctx.run(command=f"cog -rc {schema_file_path()}", warn=True)

    if check:
        check_cog(ctx)


@invoke.task
def check_cog(ctx):
    """
    Check if the alfasim_sdk/alfacase/schema.py has unstaged modifications.
    """
    ctx.run(f"git diff --no-ext-diff --exit-code {schema_file_path()}")
