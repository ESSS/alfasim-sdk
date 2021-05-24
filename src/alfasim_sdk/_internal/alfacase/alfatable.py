from pathlib import Path

from alfasim_sdk._internal.alfacase import case_description
from alfasim_sdk._internal.alfacase.alfacase_to_case import get_category_for


def generate_alfatable_file(
    alfacase_file: Path,
    alfatable_filename: str,
    description: case_description.CaseDescription,
) -> Path:
    """
    Create `.alfatable` file for the given description.
    """
    from boltons.strutils import slugify

    from alfasim_sdk import convert_description_to_alfacase

    alfatable_content = convert_description_to_alfacase(
        description, enable_flow_style_on_numpy=True
    )
    alfatable_file = (
        alfacase_file.parent
        / f"{alfacase_file.stem}.{slugify(alfatable_filename)}.alfatable"
    )
    alfatable_file.write_text(alfatable_content, encoding="utf-8")
    return alfatable_file


def load_pvt_model_table_parameters_description_from_alfatable(
    file_path: Path,
) -> case_description.PvtModelTableParametersDescription:
    """
    Load the content from the alfatable in the given file_path. The validation is turned off due to performance issues.
    """
    from ruamel import yaml as ruamelyaml
    from barril.units import Scalar
    import numpy as np

    content = ruamelyaml.safe_load(Path(file_path).read_text(encoding="UTF-8"))

    table_parameter_keys_and_values = {
        "pressure_values": np.array(content["pressure_values"]),
        "temperature_values": np.array(content["temperature_values"]),
        "table_variables": [np.array(value) for value in content["table_variables"]],
        "variable_names": content["variable_names"],
        "label": content.get("label", None),
        "number_of_phases": content["number_of_phases"],
        "warn_when_outside": content["warn_when_outside"],
    }
    key_and_unit = {
        "pressure_std": "bar",
        "temperature_std": "degC",
        "gas_density_std": "kg/m3",
        "oil_density_std": "kg/m3",
        "water_density_std": "kg/m3",
        "gas_oil_ratio": "sm3/sm3",
        "gas_liquid_ratio": "sm3/sm3",
        "water_cut": "-",
        "total_water_fraction": "-",
    }

    table_parameter_keys_and_scalars = {
        key: Scalar(get_category_for(unit), content[key]["value"], content[key]["unit"])
        for key, unit in key_and_unit.items()
    }
    return case_description.PvtModelTableParametersDescription(
        **table_parameter_keys_and_values, **table_parameter_keys_and_scalars
    )
