from barril.units import Array

from alfasim_sdk.alfacase import case_description
from alfasim_sdk.alfacase._alfacase_to_case import DescriptionDocument
from alfasim_sdk.alfacase.alfacase import ConvertDescriptionToAlfacase
from alfasim_sdk.alfacase.case_description import NumericalOptionsDescription
from alfasim_sdk.common_testing.case_builders import BuildSimpleSegment


def testConvertDescriptionToAlfacaseWithEmptyDict(tmp_path):
    """
    Ensure that the convertion from a description into a Alfacase it's not generating empty dict.
    Since it's not a valid syntax for strictyaml resulting in an InconsistentIndentationDisallowed error
    """

    simple_case = case_description.CaseDescription(
        name="Simple Case",
        pipes=[
            case_description.PipeDescription(
                name="pipe",
                source="mass_source_inlet",
                target="pressure_outlet",
                segments=BuildSimpleSegment(),
                profile=case_description.ProfileDescription(
                    x_and_y=case_description.XAndYDescription(
                        x=Array([0], "m"), y=Array([0], "m")
                    )
                ),
            )
        ],
    )
    simple_case_alfacase_content = ConvertDescriptionToAlfacase(simple_case)
    assert "wall_description: {}" not in simple_case_alfacase_content
    assert "tables: {}" not in simple_case_alfacase_content
    # Smoke check, ensures that the alfacase is loaded correctly without errors
    simple_case_alfacase_file = tmp_path / "simple_case.alfacase"
    simple_case_alfacase_file.write_text(
        data=simple_case_alfacase_content, encoding="UTF-8"
    )
    loaded_alfacase = DescriptionDocument.FromFile(simple_case_alfacase_file)

    assert loaded_alfacase.content["name"].data == simple_case.name


def testConvertDescriptionToAlfacaseWithNanFloat():
    """
    Ensure that NaN is generated as `.nan` instead of `nan`, and '.inf' instead of `inf`
    because of YAML specification 1.2 that only accepts `.nan` and `.inf`, `+.inf`, `-.inf`.
    """

    simple_case = case_description.CaseDescription(
        numerical_options=NumericalOptionsDescription(
            tolerance=float("inf"), relaxed_tolerance=float("nan")
        )
    )
    simple_case_alfacase_content = ConvertDescriptionToAlfacase(simple_case)
    assert "relaxed_tolerance: .nan" in simple_case_alfacase_content
    assert "tolerance: .inf" in simple_case_alfacase_content

    simple_case = case_description.CaseDescription(
        numerical_options=NumericalOptionsDescription(
            tolerance=float("+inf"), relaxed_tolerance=float("-inf")
        )
    )
    simple_case_alfacase_content = ConvertDescriptionToAlfacase(simple_case)
    assert "tolerance: .inf" in simple_case_alfacase_content
    assert "relaxed_tolerance: -.inf" in simple_case_alfacase_content
