from pathlib import Path

import invoke


@invoke.task
def build(ctx):
    """
    An umbrella task, currently only calls the cog
    """
    cog(ctx)


def schema_file_path() -> Path:
    return Path(__file__).parent / "src/alfasim_sdk/_internal/alfacase/schema.py"


def case_description_source_file_path() -> Path:
    return (
        Path(__file__).parent / "src/alfasim_sdk/_internal/alfacase/case_description.py"
    )


def alfacase_definitions_path() -> Path:
    return Path(__file__).parent / "docs/source/alfacase_definitions"


@invoke.task(
    help={
        "check": "Run cog in check mode ensuring that schema has not being changed.",
    }
)
def cog(ctx, check=False):
    """
    Executes cog:

    - on `_internal/alfacase/case_description.py`;
    - on `_internal/alfacase/schema.py` to generate the schema for strictyaml;
    - generate some documentation files;
    """
    ctx.run(command=f"cog -rc {case_description_source_file_path()}", warn=True)
    ctx.run(command=f"cog -rc {schema_file_path()}", warn=True)

    from alfasim_sdk._internal.alfacase.generate_schema import (
        get_all_classes_that_needs_schema,
    )
    from alfasim_sdk._internal.alfacase.case_description import CaseDescription
    from alfasim_sdk._internal.alfacase.generate_case_description_docstring import (
        generate_definition,
    )

    for class_ in get_all_classes_that_needs_schema(CaseDescription):
        output = generate_definition(class_)
        Path(alfacase_definitions_path() / f"{class_.__name__}.txt").write_text(output)

    from alfasim_sdk._internal.alfacase.generate_case_description_docstring import (
        generate_list_of_units,
        CATEGORIES_USED_ON_DESCRIPTION,
    )

    for category in CATEGORIES_USED_ON_DESCRIPTION:
        output = generate_list_of_units(category)
        category_for_path = category.replace(" ", "_")
        Path(
            alfacase_definitions_path() / f"list_of_unit_for_{category_for_path}.txt"
        ).write_text(output)

    if check:
        check_cog(ctx)


@invoke.task
def check_cog(ctx):
    """
    Check if the cogged files have unstaged modifications:

    - `_internal/alfacase/case_description.py`;
    - `_internal/alfacase/schema.py`;
    - generated documentation files;
    """
    ctx.run(f"git diff --no-ext-diff --exit-code {case_description_source_file_path()}")
    ctx.run(f"git diff --no-ext-diff --exit-code {schema_file_path()}")
    ctx.run(f"git diff --no-ext-diff --exit-code {alfacase_definitions_path()}")
