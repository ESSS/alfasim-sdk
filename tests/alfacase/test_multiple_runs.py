from pathlib import Path

from alfasim_sdk._internal.alfacase.alfacase_to_case import (
    DescriptionDocument,
    load_case_description,
)
from alfasim_sdk._internal.alfacase.case_description_attributes import (
    FloatExpression,
    ScalarExpression,
)


def test_alfacase_to_case_with_multiple_runs(datadir: Path) -> None:
    alfacase_file = datadir / "test_multiple_runs.alfacase"

    case = load_case_description(DescriptionDocument.from_file(alfacase_file))

    assert case.multiple_runs.variables == {"A": "1", "B": "2", "C": "3", "D": "A + B"}
    assert case.multiple_runs.runs == {
        "1": {"A": 1.1, "B": 2.1, "C": 3.1},
        "2": {"A": 1.11, "B": 2.11, "C": 3.11},
    }

    assert case.numerical_options.maximum_timestep_change_factor == ScalarExpression(
        expr="C", category="dimensionless", unit="-"
    )
    assert case.numerical_options.relaxed_tolerance == FloatExpression(expr="C + 1")


def test_physics_description_with_expressions(datadir: Path) -> None:
    alfacase_file = datadir / "test_multiple_runs.alfacase"

    case = load_case_description(DescriptionDocument.from_file(alfacase_file))
    physics_desc = case.physics

    assert physics_desc.emulsion_pal_rhodes_phi_rel_100 == ScalarExpression(
        expr="A+1", unit="-", category="dimensionless"
    )
    assert physics_desc.emulsion_woelflin_a == ScalarExpression(
        expr="B + C", unit="-", category="dimensionless"
    )
    assert physics_desc.emulsion_inversion_water_cut == ScalarExpression(
        expr="C + A", unit="m3/m3", category="volume per volume"
    )
