from typing import Any

from strictyaml import YAML
from strictyaml.parser import generic_load

from alfasim_sdk._internal.alfacase.case_description_attributes import DescriptionError


def migrate_alfacase_yaml_to_latest(yaml_contents: str) -> str:
    """
    Migrates the given YAML contents of an alfacase file to the latest schema version.

    We follow an approach similar to database migration, where we change the underlying data
    directly before attempting to load it using the schema.

    This function loads the yaml data as a `dict` and passes it on to various functions that are
    responsible for migrating one aspect that has changed in the `alfacase` file since its first
    version, which can then be loaded by the Schema directly.

    Returns the updated YAML which can be handed over to the schema functions.
    """
    # generic_load does not raise error when try to read an invalid yaml text based.
    yaml_data = generic_load(yaml_contents, allow_flow_style=True)
    if not isinstance(yaml_data.data, dict):
        raise DescriptionError(
            f"Expected a mapping for the alfacase file, but got: {yaml_data.data}"
        )

    # Copy to allowing in place modifications.
    copied_yaml_data = yaml_data.data.copy()

    migrate_emulsion_enums(copied_yaml_data)
    migrate_numeric_options(copied_yaml_data)
    # Append new migration functions here.

    return YAML(copied_yaml_data).as_yaml()


def migrate_emulsion_enums(data: dict[str, Any]) -> None:
    """
    Replace the removed ModelDefault variant from emulsion enums to equivalent values (ASIM-6317).
    """
    match data:
        case {"physics": {"emulsion_relative_viscosity_model": "model_default"}}:
            data["physics"]["emulsion_relative_viscosity_model"] = "brinkman1952"

    match data:
        case {"physics": {"emulsion_droplet_size_model": "model_default"}}:
            data["physics"]["emulsion_droplet_size_model"] = "brauner2001"

    match data:
        case {"physics": {"emulsion_inversion_point_model": "model_default"}}:
            data["physics"]["emulsion_inversion_point_model"] = (
                "brauner_and_ullmann_2002"
            )


def migrate_numeric_options(data: dict[str, Any]) -> None:
    """
    Replace float properties to dict to be later transformed by Scalar.
    Some properties in NumericOptions were changed from a plain `float` to a `Scalar` (ASIM-5436):

    numeric_options:
      maximum_timestep_change_factor: 1.0
      maximum_cfl_value: 100.0
    To:
        numeric_options:
          maximum_timestep_change_factor:
            value: 1.0
            unit: "-"
          maximum_cfl_value:
            value: 100.0
        unit: "-"
    """

    numerical_options = data.get("numerical_options")
    if numerical_options is None:
        return

    def try_change_to_scalar(property_name: str) -> None:
        value = numerical_options.get(property_name)
        if value is None:
            return

        value = numerical_options[property_name]
        if isinstance(value, str):
            numerical_options[property_name] = {
                "value": str(value),
                "unit": "-",
            }

    try_change_to_scalar("maximum_timestep_change_factor")
    try_change_to_scalar("maximum_cfl_value")
