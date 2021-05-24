from pathlib import Path

from alfasim_sdk._internal.alfacase import case_description


def generate_alfacase_file(
    alfacase_description: case_description.CaseDescription, alfacase_file: Path
) -> None:
    """
    Dump the case_description to the given alfacase_file, using YAML format.

    PvtModels that are of mode constants.PVT_MODEL_TABLE will be dumped into a separate file (.alfatable).
    """
    _generate_alfatable_file_for_pvt_models_description(
        alfacase_description.pvt_models, alfacase_file
    )
    alfacase_file_content = convert_description_to_alfacase(alfacase_description)
    alfacase_file.write_text(alfacase_file_content, encoding="utf-8")


def _generate_alfatable_file_for_pvt_models_description(
    pvt_models: case_description.PvtModelsDescription, alfacase_file: Path
) -> None:
    """
    Create `.alfatable` files for each pvt_model which the mode is constants.PVT_MODEL_TABLE.
    """
    from alfasim_sdk import generate_alfatable_file

    for pvt_name, pvt_table_description in pvt_models.table_parameters.items():
        alfatable_file = generate_alfatable_file(
            alfacase_file=alfacase_file,
            alfatable_filename=pvt_name,
            description=pvt_table_description,
        )
        pvt_models.tables[pvt_name] = alfatable_file.name
    pvt_models.table_parameters.clear()


def convert_description_to_alfacase(
    alfacase_description: case_description.CaseDescription,
    *,
    enable_flow_style_on_numpy: bool = False,
    remove_redundant_input_type_data: bool = True,
) -> str:
    """
    Convert a given case (decorated with attrs) to YAML representation.
    The strictyaml conversion ("as_yaml") requires that all items from dict are strings.

    :param alfacase_description:
        Alfasim case description.

    :param enable_flow_style_on_numpy:
        Signalize that numpy arrays should dumped with flow style enabled.

        enable_flow_style_on_numpy=False
        .. code-block:: python

            pressure:
                - 1
                - 2

        enable_flow_style_on_numpy=True
       .. code-block:: python

            pressure: [1, 2]

    :param remove_redundant_input_type_data:
        For transient entries remove input type selector, and the unused constant or curve entries.

    """
    import attr
    from strictyaml import YAML
    from .case_to_alfacase import convert_dict_to_valid_alfacase_format

    case_description_dict = convert_dict_to_valid_alfacase_format(
        attr.asdict(alfacase_description, recurse=False),
        enable_flow_style_on_numpy=enable_flow_style_on_numpy,
        remove_redundant_input_type_data=remove_redundant_input_type_data,
    )
    return YAML(case_description_dict).as_yaml()


def convert_alfacase_to_description(
    file_alfacase: Path,
) -> case_description.CaseDescription:
    """
    Return a :class:`alfasim_sdk._internal.alfacase.case_description` with all information provided on file_yaml.
    """
    from alfasim_sdk._internal.alfacase.alfacase_to_case import load_case_description
    from alfasim_sdk._internal.alfacase.alfacase_to_case import DescriptionDocument

    return load_case_description(DescriptionDocument.from_file(file_alfacase))
