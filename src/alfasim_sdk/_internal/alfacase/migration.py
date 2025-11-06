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
