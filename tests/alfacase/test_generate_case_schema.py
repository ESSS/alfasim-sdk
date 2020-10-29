from pathlib import Path
from textwrap import dedent
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import attr
import pytest
from barril.units import Array
from barril.units import Scalar

from alfasim_sdk.alfacase.case_description import attrib_enum
from alfasim_sdk.alfacase.case_description import attrib_instance
from alfasim_sdk.alfacase.case_description import attrib_instance_list
from alfasim_sdk.alfacase.case_description import attrib_scalar
from alfasim_sdk.alfacase.case_description import CaseDescription
from alfasim_sdk.alfacase.case_description import CompressorEquipmentDescription
from alfasim_sdk.alfacase.case_description import Numpy1DArray
from alfasim_sdk.alfacase.generate_schema import _obtain_referred_type
from alfasim_sdk.alfacase.generate_schema import generate_alfacase_schema
from alfasim_sdk.alfacase.generate_schema import get_all_classes_that_needs_schema


class TestGenerateStrictYaml:
    def test_list_schema(self):
        @attr.s
        class Foo:
            float_list: List[float] = attr.ib()
            int_list: List[int] = attr.ib()
            bool_list: List[bool] = attr.ib()
            str_list: List[str] = attr.ib()

        schema = generate_alfacase_schema(Foo)
        expected_schema = dedent(
            """\
                foo_schema = Map(
                    {
                        "float_list": Seq(Float()),
                        "int_list": Seq(Int()),
                        "bool_list": Seq(Bool()),
                        "str_list": Seq(Str()),
                    }
                )
            """
        )

        assert schema == expected_schema

    def test_base_types_schema(self):
        @attr.s
        class Foo:
            float_1: float = attr.ib()
            int_1: int = attr.ib()
            bool_1: bool = attr.ib()
            str_1: str = attr.ib()
            float_2: float = attr.ib(default=1e-4)

        schema = generate_alfacase_schema(Foo)
        expected_schema = dedent(
            """\
                foo_schema = Map(
                    {
                        "float_1": Float(),
                        "int_1": Int(),
                        "bool_1": Bool(),
                        "str_1": Str(),
                        Optional("float_2"): Float(),
                    }
                )
            """
        )

        assert schema == expected_schema

    def test_array_schema(self):
        @attr.s
        class Foo:
            array_1: Array = attr.ib()
            array_2: Optional[Array] = attr.ib(default=None)
            array_3: Array = attr.ib(default=Array([1], "K"))

        schema = generate_alfacase_schema(Foo)
        expected_schema = dedent(
            """\
                foo_schema = Map(
                    {
                        "array_1": Map({"values": Seq(Float()), "unit": Str()}),
                        Optional("array_2"): Map({"values": Seq(Float()), "unit": Str()}),
                        Optional("array_3"): Map({"values": Seq(Float()), "unit": Str()}),
                    }
                )
            """
        )

        assert schema == expected_schema

    def test_path(self):
        @attr.s
        class Foo:
            path_1: Path = attr.ib()
            path_2: Path = attr.ib(default=None)

        schema = generate_alfacase_schema(Foo)
        expected_schema = dedent(
            """\
                foo_schema = Map(
                    {
                        "path_1": Str(),
                        Optional("path_2"): Str(),
                    }
                )
            """
        )

        assert schema == expected_schema

    def test_scalar(self):
        @attr.s
        class Foo:
            scalar_1 = attrib_scalar()
            scalar_2 = attrib_scalar(default=None)
            scalar_3 = attrib_scalar(default=Scalar(1, "K"))

        schema = generate_alfacase_schema(Foo)
        expected_schema = dedent(
            """\
                foo_schema = Map(
                    {
                        "scalar_1": Map({"value": Float(), "unit": Str()}),
                        Optional("scalar_2"): Map({"value": Float(), "unit": Str()}),
                        Optional("scalar_3"): Map({"value": Float(), "unit": Str()}),
                    }
                )
            """
        )

        assert schema == expected_schema

    def test_union_schema(self):
        """
        Currently Union is only used for attr classes, and not for multiple types like str | float
        With the exception for PvtModelTable, that accepts str and Path but the YAML only accepts str anyway
        Optional type should be excluded,
        """

        @attr.s
        class X1:
            bool_1: bool = attr.ib()

        @attr.s
        class X2:
            bool_2: bool = attr.ib()

        @attr.s
        class Foo:
            x_1: Union[X1, X2] = attr.ib()
            x_2: Union[X1, X2] = attr.ib(default=X1(bool_1=True))
            x_3: Union[str, Path] = attr.ib(default="SomePath")
            # Optional[str] is equivalent to Union[str, None] and in this case we want only str
            x_4: Optional[str] = attr.ib(default="SomePath")

        schema = generate_alfacase_schema(Foo)
        expected_schema = dedent(
            """\
                foo_schema = Map(
                    {
                        "x_1": Map(
                            {
                                Optional("x1"): Seq(x1_schema),
                                Optional("x2"): Seq(x2_schema),
                            }
                        ),
                        Optional("x_2"): Map(
                            {
                                Optional("x1"): Seq(x1_schema),
                                Optional("x2"): Seq(x2_schema),
                            }
                        ),
                        Optional("x_3"): Str(),
                        Optional("x_4"): Str(),
                    }
                )
            """
        )

        assert schema == expected_schema

    def test_dict_schema(self):
        @attr.s
        class Foo:
            x_1: Dict[str, float] = attr.ib()
            x_2: Dict[str, Array] = attr.ib()
            x_3: Optional[Dict[str, Scalar]] = attr.ib(default=None)

        schema = generate_alfacase_schema(Foo)
        expected_schema = dedent(
            """\
                foo_schema = Map(
                    {
                        "x_1": MapPattern(Str(), Float()),
                        "x_2": MapPattern(Str(), Map({"values": Seq(Float()), "unit": Str()})),
                        Optional("x_3"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
                    }
                )
            """
        )

        assert schema == expected_schema

    def test_numpy_schema(self):
        @attr.s
        class Foo:
            x_1: Numpy1DArray = attr.ib()

        schema = generate_alfacase_schema(Foo)
        expected_schema = dedent(
            """\
                foo_schema = Map(
                    {
                        "x_1": Seq(Float()),
                    }
                )
            """
        )

        assert schema == expected_schema

    def test_attr_schema(self):
        @attr.s
        class X1:
            bool_1: bool = attr.ib()

        @attr.s
        class Foo:
            x_1 = attrib_instance(X1)
            x_2 = attrib_instance_list(X1)

        schema = generate_alfacase_schema(Foo)
        expected_schema = dedent(
            """\
                foo_schema = Map(
                    {
                        Optional("x_1"): x1_schema,
                        Optional("x_2"): Seq(x1_schema),
                    }
                )
            """
        )

        assert schema == expected_schema

    def test_enum_schema(self):
        from enum import Enum

        class Bar(Enum):
            a = "first_item"
            b = "second_item"

        @attr.s
        class Foo:
            x_1: List[Bar] = attr.ib()
            x_2 = attrib_enum(type_=Bar)
            x_3 = attrib_enum(default=Bar.b)

        schema = generate_alfacase_schema(Foo)
        expected_schema = dedent(
            """\
            foo_schema = Map(
                {
                    "x_1": Seq(Enum(['first_item', 'second_item'])),
                    "x_2": Enum(['first_item', 'second_item']),
                    Optional("x_3"): Enum(['first_item', 'second_item']),
                }
            )
            """
        )

        assert schema == expected_schema

    def test_optional_type_hint(self):
        @attr.s
        class Foo:
            x_1: Optional[str] = attr.ib(default=None)

        schema = generate_alfacase_schema(Foo)
        expected_schema = dedent(
            """\
            foo_schema = Map(
                {
                    Optional("x_1"): Str(),
                }
            )
            """
        )
        assert schema == expected_schema

        @attr.s
        class Foo:
            x_1: Optional[str] = attr.ib()

        @attr.s
        class Bar:
            x_1: Union[str, None] = attr.ib()

        import re

        msg = re.escape(
            "StrictYAML doesn't support None value (only missing keys denote a value), "
            "therefore Optional type are only allowed when the case has a default value."
        )

        with pytest.raises(TypeError, match=msg):
            generate_alfacase_schema(Foo)

        with pytest.raises(TypeError, match=msg):
            generate_alfacase_schema(Bar)

    def test_not_know_type(self):
        @attr.s
        class Foo:
            x_1: None = attr.ib()

        import re

        msg = f"Alfacase Schema does not know how to handle {None}"
        with pytest.raises(RuntimeError, match=re.escape(msg)):
            generate_alfacase_schema(Foo)


def test_generate_strict_yaml_schema_for_class():

    schema = generate_alfacase_schema(CompressorEquipmentDescription)
    compressor_expected_schema = dedent(
        """\
        compressor_equipment_description_schema = Map(
            {
                "position": Map({"value": Float(), "unit": Str()}),
                Optional("speed_curve"): speed_curve_description_schema,
                Optional("reference_pressure"): Map({"value": Float(), "unit": Str()}),
                Optional("reference_temperature"): Map({"value": Float(), "unit": Str()}),
                Optional("constant_speed"): Map({"value": Float(), "unit": Str()}),
                Optional("compressor_type"): Enum(['speed_curve', 'constant_speed']),
                Optional("speed_curve_interpolation_type"): Enum(['constant', 'linear', 'quadratic']),
                Optional("flow_direction"): Enum(['forward', 'backward']),
                Optional("table"): compressor_pressure_table_description_schema,
            }
        )
    """
    )
    assert schema == compressor_expected_schema


def test_generate_schema_for_all_cases(file_regression):
    """
    This check helps ensure that the YAMLSchema is being changed consciously because whenever CaseDescription is changed, the schema will change as well.

    If this test fails, make sure that the following steps were made:
    - Update the CaseDescription defined on alfasim_core.common_testing.filled_case_descriptions
        !! filled_case_descriptions helps you to find errors on the YAML import !!

    After that, you can update this test with --force-regen

    Note: Currently the schema doesn't have a version number, but in the future whenever this tests break,
    the version the number will be necessary to be changed and the changelog updated as well.

    Dev note: This test is also a facility to help debug the output generate from COG
    """
    list_of_classes_that_needs_schema = get_all_classes_that_needs_schema(
        CaseDescription
    )
    output = [
        generate_alfacase_schema(class_) for class_ in list_of_classes_that_needs_schema
    ]
    file_regression.check("\n".join(output), encoding="utf-8")


def test_alfasim_schema_is_usable():
    """
    Smoke test to ensure that the Schema has valid python syntax
    """
    from strictyaml import as_document

    from alfasim_sdk.alfacase.schema import case_description_schema

    as_document({"name": "Name"}, case_description_schema)


def test_get_cases_class():
    """
    Smoke test to ensure that the descriptions classes didn't change the name.
    If the is broken due to renaming or removal be aware of backward compatibility with ALFAcase files.
    If only Descriptions are being added, you don't need to worry and just update the list above.
    """

    list_of_classes_that_needs_schema = get_all_classes_that_needs_schema(
        CaseDescription
    )
    obtained = {class_.__name__ for class_ in list_of_classes_that_needs_schema}
    expected = {
        "AnnulusDescription",
        "BipDescription",
        "CaseDescription",
        "CaseOutputDescription",
        "CasingDescription",
        "CasingSectionDescription",
        "CompositionDescription",
        "CompressorEquipmentDescription",
        "CompressorPressureTableDescription",
        "CvTableDescription",
        "EnvironmentDescription",
        "EnvironmentPropertyDescription",
        "EquipmentDescription",
        "FluidDescription",
        "FormationDescription",
        "FormationLayerDescription",
        "GasLiftValveEquipmentDescription",
        "HeatSourceEquipmentDescription",
        "HeavyComponentDescription",
        "IPRCurveDescription",
        "IPRModelsDescription",
        "InitialConditionsDescription",
        "InitialPressuresDescription",
        "InitialTemperaturesDescription",
        "InitialTracersMassFractionsDescription",
        "InitialVelocitiesDescription",
        "InitialVolumeFractionsDescription",
        "InternalNodePropertiesDescription",
        "LengthAndElevationDescription",
        "LightComponentDescription",
        "LinearIPRDescription",
        "MassSourceEquipmentDescription",
        "MassSourceNodePropertiesDescription",
        "MaterialDescription",
        "NodeDescription",
        "NumericalOptionsDescription",
        "OpenHoleDescription",
        "OpeningCurveDescription",
        "PackerDescription",
        "PhysicsDescription",
        "PipeDescription",
        "PipeSegmentsDescription",
        "PressureContainerDescription",
        "PressureNodePropertiesDescription",
        "ProfileDescription",
        "ProfileOutputDescription",
        "PumpEquipmentDescription",
        "PvtModelCompositionalDescription",
        "PvtModelCorrelationDescription",
        "PvtModelsDescription",
        "ReferencedPressureContainerDescription",
        "ReferencedTemperaturesContainerDescription",
        "ReferencedTracersMassFractionsContainerDescription",
        "ReferencedVelocitiesContainerDescription",
        "ReferencedVolumeFractionsContainerDescription",
        "ReservoirInflowEquipmentDescription",
        "SeparatorNodePropertiesDescription",
        "SpeedCurveDescription",
        "TableIPRDescription",
        "TablePumpDescription",
        "TemperaturesContainerDescription",
        "TimeOptionsDescription",
        "TracerModelConstantCoefficientsDescription",
        "TracersDescription",
        "TracersMassFractionsContainerDescription",
        "TrendOutputDescription",
        "TubingDescription",
        "ValveEquipmentDescription",
        "VelocitiesContainerDescription",
        "VolumeFractionsContainerDescription",
        "WallDescription",
        "WallLayerDescription",
        "WellDescription",
        "XAndYDescription",
    }
    assert (
        obtained == expected
    ), f"""
           Missing in the expected: {obtained.difference(expected) or None}.
           Extra in expected: {expected.difference(obtained) or None}
       """


def test_obtain_referred_type():
    @attr.s
    class B:
        b = attr.ib()

    @attr.s
    class A:
        x: List[str] = attr.ib()
        y: List[B] = attr.ib()
        z: Union[str, int] = attr.ib()
        w: str = attr.ib()

    assert _obtain_referred_type(attr.fields_dict(A)["x"].type) == [str]
    assert _obtain_referred_type(attr.fields_dict(A)["y"].type) == [B]
    assert _obtain_referred_type(attr.fields_dict(A)["z"].type) == [str, int]

    import re

    msg = re.escape(
        "type_ must be a List or Union referring other types, got <class 'str'>"
    )
    with pytest.raises(TypeError, match=msg):
        assert _obtain_referred_type(attr.fields_dict(A)["w"].type) == [str]
