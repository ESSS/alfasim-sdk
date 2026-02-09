import re
from pathlib import Path

import pytest
from barril.units import Array, Scalar
from pytest_regressions.file_regression import FileRegressionFixture

from alfasim_sdk import (
    MultiInputType,
    NumericalOptionsDescription,
)
from alfasim_sdk._internal.alfacase import case_description
from alfasim_sdk._internal.alfacase.alfacase import (
    _convert_description_to_yaml,
    generate_alfacase_file,
)
from alfasim_sdk._internal.alfacase.alfacase_to_case import DescriptionDocument
from alfasim_sdk._internal.alfacase.case_description import (
    CaseDescription,
    MultipleRunsDescription,
    PhysicsDescription,
)
from alfasim_sdk._internal.alfacase.case_description_attributes import (
    ScalarExpression, ArrayExpression,
)
from alfasim_sdk._internal.alfacase.case_to_alfacase import _convert_value_to_valid_alfacase_format

from ..common_testing.alfasim_sdk_common_testing.case_builders import (
    build_simple_segment,
)


def test_convert_description_to_alfacase_with_empty_dict(datadir: Path) -> None:
    """
    Ensure that the conversion from a description into a Alfacase it's not generating empty dict.
    Since it's not a valid syntax for strictyaml resulting in an InconsistentIndentationDisallowed error
    """

    simple_case = case_description.CaseDescription(
        name="Simple Case",
        pipes=[
            case_description.PipeDescription(
                name="pipe",
                source="mass_source_inlet",
                target="pressure_outlet",
                segments=build_simple_segment(),
                profile=case_description.ProfileDescription(
                    x_and_y=case_description.XAndYDescription(
                        x=Array([0], "m"), y=Array([0], "m")
                    )
                ),
            )
        ],
    )
    simple_case_alfacase_content = _convert_description_to_yaml(simple_case)
    assert "wall_description: {}" not in simple_case_alfacase_content
    assert "tables: {}" not in simple_case_alfacase_content
    # Smoke check, ensures that the alfacase is loaded correctly without errors
    simple_case_alfacase_file = datadir / "simple_case.alfacase"
    simple_case_alfacase_file.write_text(
        data=simple_case_alfacase_content, encoding="UTF-8"
    )
    loaded_alfacase = DescriptionDocument.from_file(simple_case_alfacase_file)

    assert loaded_alfacase.content["name"].data == simple_case.name


@pytest.mark.parametrize(
    "remove", [pytest.param(True, id="remove"), pytest.param(False, id="keep")]
)
@pytest.mark.parametrize("input_type", [MultiInputType.Constant, MultiInputType.Curve])
def test_remove_redundant_input_type_data_option(
    remove: bool, input_type: MultiInputType
) -> None:
    mass_source_equipment_description = case_description.MassSourceEquipmentDescription(
        position=Scalar(0, "m"), temperature_input_type=input_type
    )
    yaml = _convert_description_to_yaml(
        mass_source_equipment_description, remove_redundant_input_type_data=remove
    )

    def has_key_in_yaml(key: str) -> bool:
        pattern = rf"^\s*{re.escape(key)}\s*:"
        return bool(re.search(pattern, yaml, re.MULTILINE))

    if remove:
        assert not has_key_in_yaml("temperature_input_type")
        if input_type == MultiInputType.Constant:
            assert has_key_in_yaml("temperature")
            assert not has_key_in_yaml("temperature_curve")
        elif input_type == MultiInputType.Curve:
            assert not has_key_in_yaml("temperature")
            assert has_key_in_yaml("temperature_curve")

    else:
        assert has_key_in_yaml("temperature_input_type")
        assert has_key_in_yaml("temperature")
        assert has_key_in_yaml("temperature_curve")


def test_convert_description_to_alfacase_with_nan_float():
    """
    Ensure that NaN is generated as `.nan` instead of `nan`, and '.inf' instead of `inf`
    because of YAML specification 1.2 that only accepts `.nan` and `.inf`, `+.inf`, `-.inf`.
    """

    simple_case = case_description.CaseDescription(
        numerical_options=NumericalOptionsDescription(
            tolerance=float("inf"), relaxed_tolerance=float("nan")
        )
    )
    simple_case_alfacase_content = _convert_description_to_yaml(simple_case)
    assert "relaxed_tolerance: .nan" in simple_case_alfacase_content
    assert "tolerance: .inf" in simple_case_alfacase_content

    simple_case = case_description.CaseDescription(
        numerical_options=NumericalOptionsDescription(
            tolerance=float("+inf"), relaxed_tolerance=float("-inf")
        )
    )
    simple_case_alfacase_content = _convert_description_to_yaml(simple_case)
    assert "tolerance: .inf" in simple_case_alfacase_content
    assert "relaxed_tolerance: -.inf" in simple_case_alfacase_content


def test_convert_case_with_multiple_runs(
    file_regression: FileRegressionFixture, datadir: Path
) -> None:
    multiple_runs = MultipleRunsDescription(
        variables={"A": 1.0, "B": 2.0, "C": 3.0},
        runs={
            "1": {"A": 1.1, "B": 2.1, "C": 3.1},
            "2": {"A": 1.11, "B": 2.11, "C": 3.11},
        },
    )
    numerical_options = NumericalOptionsDescription(
        maximum_cfl_value=ScalarExpression(
            expr="C+2", category="dimensionless", unit="m"
        )
    )
    physics_description = PhysicsDescription(
        emulsion_woelflin_a=ScalarExpression(expr="A + 1", unit="-"),
        emulsion_woelflin_b=ScalarExpression(expr="A + B", unit="-"),
    )
    case_description = CaseDescription(
        physics=physics_description,
        multiple_runs=multiple_runs,
        numerical_options=numerical_options,
    )
    alfacase_file = datadir / "my_alfacase.alfacase"
    generate_alfacase_file(case_description, alfacase_file)
    file_regression.check(
        alfacase_file.read_text(encoding="UTF-8"), extension=".alfacase"
    )

def test_convert_array_expression() -> None:
    aray_expression = ArrayExpression(category="dimensionless", unit="%", exprs=[1.0, "A", 3.0, "A + B"])
    converted_value = _convert_value_to_valid_alfacase_format(value=aray_expression, enable_flow_style_on_numpy=False)
    assert converted_value == {'exprs': ['1.0', 'A', '3.0', 'A + B'], 'unit': '%'}

def test_simple_case_with_array_expr(datadir: Path, file_regression: FileRegressionFixture) -> None:
    """
    Teste a simple case where a simple case description has some ArrayExpressions.
    """
    simple_case = case_description.CaseDescription(
        name="Simple Case",
        pipes=[
            case_description.PipeDescription(
                name="pipe",
                source="mass_source_inlet",
                target="pressure_outlet",
                segments=build_simple_segment(),
                profile=case_description.ProfileDescription(
                    x_and_y=case_description.XAndYDescription(
                        x=ArrayExpression(category="length", exprs=["A", 2.0, "A+B", 4.0], unit="m"), y=ArrayExpression(category="length", exprs=["A", 2.0, "A+B", 4.0], unit="m")
                    )
                ),
            )
        ],
    )

    alfacase_file = datadir / "my_alfacase.alfacase"
    generate_alfacase_file(simple_case, alfacase_file)
    file_regression.check(alfacase_file.read_text(encoding="UTF-8"), extension=".alfacase")
