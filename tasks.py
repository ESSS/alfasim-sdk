from pathlib import Path

import invoke


@invoke.task
def build(ctx):
    """
    An umbrella task, currently only calls the cog
    """
    cog(ctx)


def schema_file_path() -> Path:
    return Path(__file__).parent / "src/_alfasim_sdk/alfacase/schema.py"


@invoke.task(
    help={
        "check": "Run cog in check mode ensuring that schema has not being changed.",
    }
)
def cog(ctx, check=False):
    """ Executes cog on _alfasim_sdk/alfacase/schema.py to generate the schema for strictyaml. """
    ctx.run(command=f"cog -rc {schema_file_path()}", warn=True)

    from _alfasim_sdk.alfacase.generate_schema import get_all_classes_that_needs_schema
    from _alfasim_sdk.alfacase.case_description import CaseDescription
    from _alfasim_sdk.alfacase.generate_case_description_docstring import (
        generate_definition,
    )

    alfacase_definitions_path = (
        Path(__file__).parent / "docs/source/alfacase_definitions"
    )
    for class_ in get_all_classes_that_needs_schema(CaseDescription):
        output = generate_definition(class_)
        Path(alfacase_definitions_path / f"{class_.__name__}.txt").write_text(output)

    if check:
        check_cog(ctx)


@invoke.task
def check_cog(ctx):
    """
    Check if the _alfasim_sdk/alfacase/schema.py has unstaged modifications.
    """
    ctx.run(f"git diff --no-ext-diff --exit-code {schema_file_path()}")
