from pathlib import Path

from alfasim_sdk.alfacase import case_description


def GenerateAlfacaseFile(
    alfacase_description: case_description.CaseDescription, alfacase_file: Path
):
    """
    Dump the case_description to the given alfacase_file, using YAML format.

    PvtModels that are of mode constants.PVT_MODEL_TABLE will be dumped into a separate file (.alfatable).
    """
    _GenerateAlfatableFileForPvtModelsDescription(
        alfacase_description.pvt_models, alfacase_file
    )
    alfacase_file_content = ConvertDescriptionToAlfacase(alfacase_description)
    alfacase_file.write_text(alfacase_file_content, encoding="utf-8")


def _GenerateAlfatableFileForPvtModelsDescription(
    pvt_models: case_description.PvtModelsDescription, alfacase_file: Path
):
    """
    Create `.alfatable` files for each pvt_model which the mode is constants.PVT_MODEL_TABLE
    """
    from alfasim_sdk.alfacase.alfatable import GenerateAlfatableFile

    for pvt_name, pvt_table_description in pvt_models.table_parameters.items():
        alfatable_file = GenerateAlfatableFile(
            alfacase_file=alfacase_file,
            alfatable_filename=pvt_name,
            description=pvt_table_description,
        )
        pvt_models.tables[pvt_name] = alfatable_file.name
    pvt_models.table_parameters.clear()


def ConvertDescriptionToAlfacase(
    alfacase_description, *, enable_flow_style_on_numpy: bool = False
) -> str:
    """
    Convert a given case (decorated with attrs) to YAML representation.
    The strictyaml conversion ("as_yaml") requires that all items from dict are strings

    :param enable_flow_style_on_numpy:
        Signalize that numpy arrays should dumped with flow style enabled

        enable_flow_style_on_numpy=False
        .. code-block:: python

            pressure:
                - 1
                - 2

        enable_flow_style_on_numpy=True
       .. code-block:: python

            pressure: [1, 2]

    """
    import attr
    from alfasim_sdk.alfacase._case_to_alfacase import ConvertDictToValidAlfacaseFormat
    from strictyaml import YAML

    case_description_dict = ConvertDictToValidAlfacaseFormat(
        attr.asdict(alfacase_description, recurse=False),
        enable_flow_style_on_numpy=enable_flow_style_on_numpy,
    )
    return YAML(case_description_dict).as_yaml()


def ConvertAlfacaseToCase(file_alfacase: Path) -> case_description.CaseDescription:
    """
    Return a alfasim_sdk.alfacase.case_description.Case with all information provided on file_yaml
    """
    from alfasim_sdk.alfacase._alfacase_to_case import (
        LoadCaseDescription,
        DescriptionDocument,
    )

    return LoadCaseDescription(DescriptionDocument.FromFile(file_alfacase))
