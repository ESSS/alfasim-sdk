from pathlib import Path

from alfasim_sdk._internal.alfacase import case_description
from alfasim_sdk._internal.alfacase.alfacase import _convert_description_to_yaml
from alfasim_sdk._internal.alfacase.alfacase_to_case import get_category_for
from alfasim_sdk._internal.alfacase.case_description_attributes import Numpy1DArray


def generate_alfatable_file(
    alfacase_file: Path,
    alfatable_filename: str,
    description: case_description.CaseDescription
    | case_description.PvtModelPtTableParametersDescription
    | case_description.PvtModelPhTableParametersDescription,
) -> Path:
    """
    Create `.alfatable` file for the given description.
    """
    from boltons.strutils import slugify

    alfatable_content = _convert_description_to_yaml(
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
) -> case_description.PvtModelPtTableParametersDescription:
    """
    Load the content from the alfatable in the given file_path. The validation is turned off due to performance issues.
    """
    import numpy as np
    from barril.units import Scalar
    from strictyaml.ruamel.main import YAML

    yaml = YAML(typ="safe", pure=True)
    content = yaml.load(Path(file_path))

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

    def get_scalar_for_key(key: str) -> Scalar:
        unit = key_and_unit[key]
        category = get_category_for(unit)
        if category is None:
            raise RuntimeError(
                f"Could not find category for unit={unit} (key={key}), file: {file_path}"
            )
        return Scalar(category, content[key]["value"], content[key]["unit"])

    return case_description.PvtModelPtTableParametersDescription(
        pressure_values=Numpy1DArray(np.array(content["pressure_values"])),
        temperature_values=Numpy1DArray(np.array(content["temperature_values"])),
        table_variables=[
            Numpy1DArray(np.array(value)) for value in content["table_variables"]
        ],
        variable_names=content["variable_names"],
        label=content.get("label", None),
        number_of_phases=content["number_of_phases"],
        warn_when_outside=content["warn_when_outside"],
        pressure_std=get_scalar_for_key("pressure_std"),
        temperature_std=get_scalar_for_key("temperature_std"),
        gas_density_std=get_scalar_for_key("gas_density_std"),
        oil_density_std=get_scalar_for_key("oil_density_std"),
        water_density_std=get_scalar_for_key("water_density_std"),
        gas_oil_ratio=get_scalar_for_key("gas_oil_ratio"),
        gas_liquid_ratio=get_scalar_for_key("gas_liquid_ratio"),
        water_cut=get_scalar_for_key("water_cut"),
        total_water_fraction=get_scalar_for_key("total_water_fraction"),
    )
