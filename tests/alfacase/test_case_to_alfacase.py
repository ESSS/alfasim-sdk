import re
from pathlib import Path

import pytest
from barril.units import Array, Scalar

from alfasim_sdk import (
    MultiInputType,
    NumericalOptionsDescription,
)
from alfasim_sdk._internal.alfacase import case_description
from alfasim_sdk._internal.alfacase.alfacase import _convert_description_to_yaml
from alfasim_sdk._internal.alfacase.alfacase_to_case import DescriptionDocument

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
