from pathlib import Path

from alfasim_sdk import (
    EmulsionDropletSizeModelType,
    EmulsionInversionPointModelType,
    EmulsionRelativeViscosityModelType,
)
from alfasim_sdk._internal.alfacase.alfacase_to_case import (
    DescriptionDocument,
    load_case_description,
)


def test_migrate_emulsion_enums(datadir: Path) -> None:
    """
    Test the situation where the alfacase files have set the removed enumeration value
    `model_default` from emulsion properties Enum, updating it to a new default value (ASIM-6137).
    """
    alfacase_file = datadir / "test_migrate_emulsion_enums.alfacase"
    case = load_case_description(DescriptionDocument.from_file(alfacase_file))

    assert (
        case.physics.emulsion_relative_viscosity_model
        is EmulsionRelativeViscosityModelType.Brinkman1952
    )
    assert (
        case.physics.emulsion_droplet_size_model
        is EmulsionDropletSizeModelType.Brauner2001
    )
    assert (
        case.physics.emulsion_inversion_point_model
        is EmulsionInversionPointModelType.BraunerUllmann2002
    )
