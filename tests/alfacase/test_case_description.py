import re
import textwrap
from collections.abc import Callable
from pathlib import Path
from textwrap import dedent
from typing import Any

import attr
import pytest
from attr._make import _CountingAttr
from barril.curve.curve import Curve
from barril.units import Array, Scalar

from alfasim_sdk import CaseDescription, MaterialDescription, NodeCellType
from alfasim_sdk._internal import constants
from alfasim_sdk._internal.alfacase import case_description
from alfasim_sdk._internal.alfacase.case_description_attributes import (
    DescriptionError,
    InvalidReferenceError,
    attrib_array,
    attrib_curve,
    attrib_enum,
    attrib_instance,
    attrib_instance_list,
    attrib_scalar,
    collapse_array_repr,
    generate_multi_input,
    generate_multi_input_dict,
    numpy_array_validator,
    to_array,
    to_curve,
)

from ..common_testing.alfasim_sdk_common_testing.case_builders import (
    build_simple_segment,
)


# Note: the table parameters descriptions have the same methods, so it could
# implement some tests for the both
@pytest.fixture(
    params=(
        case_description.PvtModelPtTableParametersDescription,
        case_description.PvtModelPhTableParametersDescription,
    ),
    ids=("pt_table_description", "ph_table_description"),
)
def table_parameters_description(request):
    return request.param


def test_physics_description_path_validator(tmp_path):
    """
    Ensure PhysicsDescription.restart_filepath only accepts created files
    """
    import re
    from pathlib import Path

    expected_error = re.escape(
        f"'restart_filepath' must be {Path} (got '' that is a {str})."
    )
    with pytest.raises(TypeError, match=expected_error):
        case_description.PhysicsDescription(restart_filepath="")  # type:ignore[arg-type]

    tmp_file = tmp_path / "tmp.txt"
    tmp_file.touch()
    assert case_description.PhysicsDescription(restart_filepath=tmp_file)
    assert case_description.PhysicsDescription(restart_filepath=None)


def test_cv_table_description():
    expected_msg = "Opening and Flow Coefficient must have the same size, got 2 items for flow_coefficient and 1 for opening"
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        case_description.CvTableDescription(
            opening=Array([0.0], "-"),
            flow_coefficient=Array([0.0, 2], "(galUS/min)/(psi^0.5)"),
        )


def test_table_pump_description_length():
    expected_msg = dedent(
        """\
    speeds, void_fractions, flow_rates, pressure_boosts, heads, efficiencies and powers must have the same size, got:
        - 2 items for speeds
        - 2 items for void_fractions
        - 2 items for flow_rates
        - 1 items for pressure_boosts
        - 1 items for heads
        - 1 items for efficiencies
        - 1 items for powers
    """
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        case_description.TablePumpDescription(
            speeds=Array([1, 2], "rpm"),
            void_fractions=Array([1, 2], "-"),
            flow_rates=Array([1, 2], "m3/s"),
            pressure_boosts=Array([1], "bar"),
            heads=Array([1], "m"),
            efficiencies=Array([1], "-"),
            powers=Array([1], "W"),
        )
    
    # Test torques validation separately
    expected_msg_torques = dedent(
        """\
    torques must be either empty or have the same size as other fields, got:
        - 2 items expected
        - 1 items for torques
    """
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg_torques)):
        case_description.TablePumpDescription(
            speeds=Array([1, 2], "rpm"),
            void_fractions=Array([1, 2], "-"),
            flow_rates=Array([1, 2], "m3/s"),
            pressure_boosts=Array([1, 2], "bar"),
            heads=Array([1, 2], "m"),
            efficiencies=Array([1, 2], "-"),
            powers=Array([1, 2], "W"),
            torques=Array([1], "N.m"),
        )

    # Check if the defaults values works well
    case_description.TablePumpDescription()


def test_compressor_pressure_table_description_length():
    expected_msg = dedent(
        """\
    speed_entries, corrected_mass_flow_rate_entries, pressure_ratio_table and isentropic_efficiency_table must have the same size, got:
        - 2 items for speed_entries
        - 2 items for corrected_mass_flow_rate_entries
        - 2 items for pressure_ratio_table
        - 1 items for isentropic_efficiency_table
    """
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        case_description.CompressorPressureTableDescription(
            speed_entries=Array([1, 2], "rpm"),
            corrected_mass_flow_rate_entries=Array([1, 2], "kg/s"),
            pressure_ratio_table=Array([1, 2], "-"),
            isentropic_efficiency_table=Array([1], "-"),
        )

    # Check if the defaults values works well
    case_description.CompressorPressureTableDescription()


def test_instance_attribute_list():
    @attr.s
    class X:
        pass

    @attr.s
    class Y:
        pass

    @attr.s(kw_only=True, auto_attribs=True)
    class Foo:
        attr_1: list[X] = attrib_instance_list(X)

    # Check validator of attrib_instance_list
    expected_msg = f"'attr_1' must be {list} (got X() that is a {X})."
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(attr_1=X())  # type:ignore[arg-type]

    expected_msg = f"'attr_1' must be {X} (got Y() that is a {Y})."
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(attr_1=[Y()])  # type:ignore[list-item]

    expected_msg = f"'attr_1' must be {list} (got None that is a {type(None)})."
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(attr_1=None)  # type:ignore[arg-type]

    # Smoke check
    assert Foo(attr_1=[X()])


def test_instance_attribute():
    @attr.s
    class X:
        pass

    @attr.s
    class Y:
        pass

    @attr.s(kw_only=True, auto_attribs=True)
    class Foo:
        attr_1: X = attrib_instance(X)
        attr_2: list[X] = attrib_instance_list(X)

    # Check validator of attrib_instance
    expected_msg = f"'attr_1' must be {X} (got Y() that is a {Y})."
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(attr_1=Y())  # type:ignore[arg-type]

    # Smoke check
    assert Foo(attr_1=X())


def test_curve_attributes_converter():
    @attr.s(auto_attribs=True)
    class Foo:
        x: Curve = attrib_curve(category="length", domain_category="time")

    expected_msg = "Expected pair (image_array, domain_array) or Curve, got None (type: <class 'NoneType'>)"
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(x=None)  # type:ignore[arg-type]

    # Fail to convert image (error context).
    expected_msg = "Curve image: Expected pair (values, unit) or Array, got None (type: <class 'NoneType'>)"
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(x=(None, None))  # type:ignore[arg-type]

    # Fail to convert domain (error context).
    expected_msg = "Curve domain: Expected pair (values, unit) or Array, got None (type: <class 'NoneType'>)"
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(x=(([1, 11, 111], "m"), None))  # type:ignore[arg-type]

    # Image and domain does not have the same size.
    expected_msg = (
        "The length of the image (3) is different from the size of the domain (2)"
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        Foo(x=(([1, 11, 111], "m"), ([0, 10], "s")))  # type:ignore[arg-type]

    Foo(x=(([1, 11, 111], "m"), ([0, 10, 20], "s")))  # type:ignore[arg-type]


def test_scalar_attribute():
    expected_msg = (
        "If `default` is not a scalar then `category` is required to be not `None`"
    )
    for kwargs in [{}, {"default": None}]:
        with pytest.raises(ValueError, match=expected_msg):

            @attr.s(kw_only=True)
            class Bar:
                x = attrib_scalar(**kwargs)  # type:ignore[arg-type]

    @attr.s(kw_only=True, auto_attribs=True)
    class Foo:
        position: Scalar = attrib_scalar(default=Scalar(1, "m"))
        position_2: Scalar | None = attrib_scalar(default=None, category="length")

    # Check position
    instance_with_scalar = Foo(position=Scalar(1, "m"))
    assert isinstance(instance_with_scalar.position, Scalar)

    instance_with_tuple = Foo(position=(1, "m"))  # type:ignore[arg-type]
    assert isinstance(instance_with_tuple.position, Scalar)

    expected_msg = (
        "Expected pair (value, unit) or Scalar, got None (type: <class 'NoneType'>)"
    )
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(position=None)  # type:ignore[arg-type]

    # Check position_1 (accepts None)
    instance_with_scalar = Foo(position_2=Scalar(1, "m"))
    assert isinstance(instance_with_scalar.position, Scalar)

    instance_with_tuple = Foo(position_2=(1, "m"))  # type:ignore[arg-type]
    assert isinstance(instance_with_tuple.position, Scalar)

    assert Foo(position_2=None).position_2 is None


def test_enum_attribute():
    from enum import Enum

    class X(Enum):
        A = "A"
        B = "B"

    @attr.s(kw_only=True, auto_attribs=True)
    class Foo:
        attr_1: X = attrib_enum(default=X.A)

    # Check validator of Enum
    expected_msg_for_enum = "'attr_1' must be in <enum 'X'> (got 's')"
    with pytest.raises(ValueError, match=re.escape(expected_msg_for_enum)):
        Foo(attr_1="s")  # type:ignore[arg-type]

    # Type_ is mandatory when default is not provided
    expected_msg = "Default or type_ parameter must be provided"
    with pytest.raises(RuntimeError, match=re.escape(expected_msg)):
        attrib_enum()

    # Avoiding shooting in the foot =)
    expected_msg = (
        "Default must be a member of Enum and not the Enum class itself, "
        "got <enum 'X'> while expecting some of the following members X.A, X.B"
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        attrib_enum(default=X)


@pytest.fixture()
def default_case(tmp_path) -> case_description.CaseDescription:
    """
    Minimum valid CaseDescription with pvt configured
    """
    tab_file = tmp_path / "dummy.tab"
    file_content = [
        'PVTTABLE LABEL = "PVT1",PHASE = THREE,',
        'PVTTABLE LABEL = "PVT2", PHASE = THREE,',
    ]
    tab_file.write_text("\n".join(file_content))
    return case_description.CaseDescription(
        pvt_models=case_description.PvtModelsDescription(
            default_model="PVT2",
            tables={"PVT1": f"{tab_file}"},
            correlations={"PVT2": case_description.PvtModelCorrelationDescription()},
            compositional={"PVT3": case_description.PvtModelCompositionalDescription()},
            pt_table_parameters={
                "PVT4": case_description.PvtModelPtTableParametersDescription.create_empty()
            },
            ph_table_parameters={
                "PVT5": case_description.PvtModelPhTableParametersDescription.create_empty()
            },
            constant_properties={
                "PVT6": case_description.PvtModelConstantPropertiesDescription()
            },
        )
    )


@pytest.fixture()
def default_well() -> case_description.WellDescription:
    """
    Minimum valid WellDescription
    """
    return case_description.WellDescription(
        name="Well 1",
        profile=case_description.ProfileDescription(
            length_and_elevation=case_description.LengthAndElevationDescription(
                length=Array([0.0] + [1000] * 2, "m"),
                elevation=Array([0.0] + [1.2] * 2, "m"),
            )
        ),
        stagnant_fluid="Lift Gas",
        top_node="Node 1",
        bottom_node="Node 2",
        annulus=case_description.AnnulusDescription(
            has_annulus_flow=False, top_node="Node 1"
        ),
        formation=case_description.FormationDescription(
            reference_y_coordinate=Scalar(0, "m")
        ),
        environment=case_description.EnvironmentDescription(
            thermal_model=constants.PipeThermalModelType.SteadyState
        ),
    )


def _empty_profile():
    """Helper function to get a empty profile for tests."""
    return case_description.ProfileDescription(
        x_and_y=case_description.XAndYDescription(x=Array([0], "m"), y=Array([0], "m"))
    )


def test_check_pvt_model_files_handling_white_space(default_case, tmp_path):
    """
    PvtModelsDescription.tables accept which PvtModel should be included from the file by passing the argument

    """
    case = attr.evolve(
        default_case,
        pvt_models=case_description.PvtModelsDescription(
            default_model="PVT1", tables={"PVT1": f"{tmp_path / 'dummy.tab'}| PVT1"}
        ),
    )
    case.ensure_valid_references()


def test_check_restart_file_exists(default_case, tmp_path):
    """Ensure that the method EnsureValidReferences from CaseDescription catches errors with invalid restart files."""
    restart_file = tmp_path / "dummy.restart"
    case = attr.evolve(
        default_case,
        physics=case_description.PhysicsDescription(
            initial_condition_strategy=constants.InitialConditionStrategyType.Restart,
            restart_filepath=restart_file,
        ),
    )
    expected_error = re.escape(f"Restart file '{restart_file}' is not a valid file")

    with pytest.raises(
        InvalidReferenceError,
        match=expected_error,
    ):
        case.ensure_valid_references()

    restart_file.write_text("Restart file contents")
    case.ensure_valid_references()


def test_check_restart_point_filepath(
    default_case: case_description.CaseDescription, tmp_path: Path
) -> None:
    """Ensure that setting restart_filepath points to a valid file."""
    restart_filepath = tmp_path / "dummy.restart"

    # File does not exist yet.
    case = attr.evolve(
        default_case,
        physics=case_description.PhysicsDescription(
            initial_condition_strategy=constants.InitialConditionStrategyType.Restart,
            restart_filepath=restart_filepath,
        ),
    )
    with pytest.raises(
        DescriptionError,
        match="Restart file .* is not a valid file",
    ):
        case.ensure_valid_references()

    restart_filepath.touch()
    case.ensure_valid_references()


class TestResetInvalidReferences:
    def test_remove_pvt_entry_from_pvt_models_when_pvt_model_is_invalid(
        self, default_case, tmp_path
    ):
        """
        Check if the PVTModel referred from case.pvt_models.tables is inside a pvt file,
        if invalid the entry must be removed, when calling case.ResetInvalidReferences()
        """

        case = attr.evolve(
            default_case,
            pvt_models=case_description.PvtModelsDescription(
                default_model="PVT1",
                tables={"PVT1": f"{tmp_path / 'dummy.tab'}|INVALID"},
            ),
        )
        case.reset_invalid_references()
        assert case.pvt_models.tables == {}
        assert case.pvt_models.default_model is None
        case = case_description.CaseDescription(
            pvt_models=case_description.PvtModelsDescription(
                default_model="PVT2", tables={"PVT2": f"{tmp_path / 'dummy.tab'}|PVT2"}
            )
        )
        case.reset_invalid_references()
        assert case.pvt_models.default_model == "PVT2"

    def test_remove_pvt_entry_from_pvt_models_when_file_is_invalid(self):
        """
        Remove the PVT entry from case.pvt_models.tables if the file is not a file when calling ResetInvalidReferences()
        """
        case = case_description.CaseDescription(
            pvt_models=case_description.PvtModelsDescription(
                default_model="PVT1", tables={"PVT1": "SomePath"}
            )
        )
        case.reset_invalid_references()
        assert case.pvt_models.tables == {}
        assert case.pvt_models.default_model is None

    def test_pvt_model_default(self, default_case):
        """
        If default_model has an invalid reference, the value must reset to None when calling ResetInvalidReferences()
        """
        case = attr.evolve(
            default_case,
            pvt_models=attr.evolve(default_case.pvt_models, default_model="InvalidPVT"),
        )
        case.reset_invalid_references()
        assert case.pvt_models.default_model is None

    def test_pipe_pvt_model(self, default_case, default_well):
        """
        If a Elements on case uses an invalid PvtModel, the pvt_model must reset to None when calling ResetInvalidReferences()
        """
        case = attr.evolve(
            default_case,
            nodes=[
                case_description.NodeDescription(
                    name="Node 1",
                    node_type=NodeCellType.Pressure,
                    pvt_model="InvalidPVT",
                )
            ],
            wells=[
                attr.evolve(
                    default_well,
                    pvt_model="InvalidPVT",
                    annulus=case_description.AnnulusDescription(
                        has_annulus_flow=False,
                        pvt_model="InvalidPVT",
                        top_node="Node 1",
                    ),
                )
            ],
            pipes=[
                case_description.PipeDescription(
                    name="Pipe 1",
                    pvt_model="InvalidPVT",
                    source="in",
                    target="out",
                    profile=_empty_profile(),
                    segments=build_simple_segment(),
                    equipment=case_description.EquipmentDescription(
                        mass_sources={
                            "Mass Equip. 1": case_description.MassSourceEquipmentDescription(
                                position=Scalar(0, "m")
                            )
                        }
                    ),
                )
            ],
        )

        case.reset_invalid_references()
        assert case.pipes[0].pvt_model is None
        assert case.nodes[0].pvt_model is None
        assert case.wells[0].pvt_model is None
        assert case.wells[0].annulus.pvt_model is None


class TestEnsureValidReferences:
    """
    Ensure that the attributes from CaseDescription that have references to other elements are valid.
    """

    def test_pvt_model_are_valid(self, default_case: CaseDescription) -> None:
        """
        Check that the validation for invalid references works for all types of PvtModel
        (Composition, Correlation, Tables, Constant and TableParameters).
        """
        case = attr.evolve(
            default_case,
            pipes=[
                case_description.PipeDescription(
                    name="Pipe 1",
                    pvt_model="PVT1",
                    source="in",
                    target="out",
                    profile=_empty_profile(),
                    segments=build_simple_segment(),
                ),
                case_description.PipeDescription(
                    name="Pipe 2",
                    pvt_model="PVT2",
                    source="in",
                    target="out",
                    profile=_empty_profile(),
                    segments=build_simple_segment(),
                ),
                case_description.PipeDescription(
                    name="Pipe 3",
                    pvt_model="PVT3",
                    source="in",
                    target="out",
                    profile=_empty_profile(),
                    segments=build_simple_segment(),
                ),
                case_description.PipeDescription(
                    name="Pipe 4",
                    pvt_model="PVT4",
                    source="in",
                    target="out",
                    profile=_empty_profile(),
                    segments=build_simple_segment(),
                ),
                case_description.PipeDescription(
                    name="Pipe 5",
                    pvt_model="PVT5",
                    source="in",
                    target="out",
                    profile=_empty_profile(),
                    segments=build_simple_segment(),
                ),
                case_description.PipeDescription(
                    name="Pipe 6",
                    pvt_model="PVT6",
                    source="in",
                    target="out",
                    profile=_empty_profile(),
                    segments=build_simple_segment(),
                ),
            ],
        )
        # Add the Constant PVT as a valid reference (ASIM-6291).
        [constant_property] = list(case.pvt_models.constant_properties.keys())
        assert constant_property == "PVT6"

    def test_pvt_model_from_file_is_in_valid(self, default_case, tmp_path):
        """
        When a PVTModel informed from the user on a file doesn't exist,
        a InvalidReferenceError must be raised when case.EnsureValidReferences is called.
        """
        case = attr.evolve(
            default_case,
            pvt_models=case_description.PvtModelsDescription(
                default_model="PVT1",
                tables={"PVT1": f"{tmp_path / 'dummy.tab'}|INVALID"},
            ),
        )
        expect_message = "'INVALID' could not be found on 'dummy.tab', available models are: 'PVT1, PVT2'"
        with pytest.raises(
            InvalidReferenceError,
            match=re.escape(expect_message),
        ):
            case.ensure_valid_references()

        # Ensure the test finishes in a valid state
        case = case_description.CaseDescription(
            pvt_models=case_description.PvtModelsDescription(
                default_model="PVT2", tables={"PVT2": f"{tmp_path / 'dummy.tab'}|PVT2"}
            )
        )
        case.ensure_valid_references()
        assert case.pvt_models.default_model == "PVT2"

    def test_pvt_models_with_invalid_pvtfile(self, tmp_path):
        """
        When a PVTModel assigned on case.pvt_models.tables doesn't exist,
        a InvalidReferenceError exception must be raised when case.EnsureValidReferences is called.
        """
        case = case_description.CaseDescription(
            pvt_models=case_description.PvtModelsDescription(
                default_model="PVT1", tables={"PVT1": "SomePath|PVT1"}
            )
        )
        expect_message = "Error on 'PVT1', 'SomePath' is not a valid file"
        with pytest.raises(
            InvalidReferenceError,
            match=re.escape(expect_message),
        ):
            case.ensure_valid_references()

        # Ensure the test finishes in a valid state
        tmp_file = tmp_path / "dummy.tab"
        tmp_file.write_text("")

        case = case_description.CaseDescription(
            pvt_models=case_description.PvtModelsDescription(
                default_model="PVT2", tables={"PVT2": f"{tmp_file}"}
            )
        )
        case.ensure_valid_references()
        assert case.pvt_models.default_model == "PVT2"

    def test_pvt_model_default_behavior(self, default_case, default_well):
        """
        1) CaseDescription should accept components that uses PvtModel as None while default_model is configured.
        2) default_model must be a valid pvt_model defined on pvt_models
        3) If default_model is None, all components that uses pvt_model must be assigined.
        """
        from alfasim_sdk._internal.constants import NodeCellType

        case = attr.evolve(
            default_case,
            pvt_models=attr.evolve(default_case.pvt_models, default_model="PVT2"),
            nodes=[
                case_description.NodeDescription(
                    name="Node 1", node_type=NodeCellType.Pressure, pvt_model=None
                )
            ],
            pipes=[
                case_description.PipeDescription(
                    name="Pipe 1",
                    pvt_model=None,
                    source="in",
                    target="out",
                    segments=build_simple_segment(),
                    profile=case_description.ProfileDescription(
                        x_and_y=case_description.XAndYDescription(
                            x=Array([0], "m"), y=Array([0], "m")
                        )
                    ),
                )
            ],
            wells=[
                attr.evolve(
                    default_well,
                    pvt_model=None,
                    annulus=attr.evolve(default_well.annulus, pvt_model=None),
                )
            ],
        )
        # Check 1) If default_model assigned, elements that uses pvt_model can be None
        case.ensure_valid_references()
        assert case.pvt_models.default_model == "PVT2"
        assert case.nodes[0].pvt_model is None
        assert case.pipes[0].pvt_model is None
        assert case.wells[0].pvt_model is None
        assert case.wells[0].annulus.pvt_model is None

        # Check 2) default_model must be filled with a valid pvt_model
        case_with_invalid_default_pvt_model = attr.evolve(
            case, pvt_models=attr.evolve(case.pvt_models, default_model="Acme")
        )
        expected_msg = (
            "PVT model 'Acme' select on 'default_model' is not declared on 'pvt_models', "
            "available pvt_models are: PVT1, PVT2, PVT3"
        )

        with pytest.raises(
            InvalidReferenceError,
            match=re.escape(expected_msg),
        ):
            case_with_invalid_default_pvt_model.ensure_valid_references()

        # Check 3) If default_model is not assigned, all elements with pvt_models must be configured.
        case_with_invalid_default_pvt_model = attr.evolve(
            case, pvt_models=attr.evolve(case.pvt_models, default_model=None)
        )
        expected_msg = (
            "The following elements doesnt have a pvt_model assigned: Node 1, Pipe 1, Well 1, Annulus from Well 1.\n"
            "Either assign a valid pvt_model on the element, or fill the default_model parameter."
        )
        with pytest.raises(
            InvalidReferenceError,
            match=re.escape(expected_msg),
        ):
            case_with_invalid_default_pvt_model.ensure_valid_references()

    def test_pipe_pvt_model(self, default_case):
        """
        If a PipeDescription uses an invalid PvtModel, an InvalidReferenceError must be raised.
        """
        case = attr.evolve(
            default_case,
            pipes=[
                case_description.PipeDescription(
                    name="Pipe 1",
                    segments=build_simple_segment(),
                    pvt_model="Acme",
                    source="in",
                    target="out",
                    profile=_empty_profile(),
                )
            ],
        )
        expected_error = (
            "PVT model 'Acme' selected on 'Pipe 1' is not declared on 'pvt_models', "
            "available pvt_models are: PVT1, PVT2, PVT3"
        )
        with pytest.raises(
            InvalidReferenceError,
            match=re.escape(expected_error),
        ):
            case.ensure_valid_references()

    def test_node_pvt_model(self, default_case):
        """
        If a NodeDescription uses an invalid PvtModel, an InvalidReferenceError must be raised.
        """
        case = attr.evolve(
            default_case,
            nodes=[
                case_description.NodeDescription(
                    name="Node 1", node_type=NodeCellType.Pressure, pvt_model="Foo"
                )
            ],
        )
        expected_error = (
            "PVT model 'Foo' selected on 'Node 1' is not declared on 'pvt_models', "
            "available pvt_models are: PVT1, PVT2, PVT3"
        )
        with pytest.raises(
            InvalidReferenceError,
            match=re.escape(expected_error),
        ):
            case.ensure_valid_references()

    def test_well_pvt_model(self, default_case, default_well):
        """
        If a WellDescription uses an invalid PvtModel, an InvalidReferenceError must be raised.
        """
        case = attr.evolve(
            default_case, wells=[attr.evolve(default_well, pvt_model="Foo")]
        )
        expected_error = (
            "PVT model 'Foo' selected on 'Well 1' is not declared on 'pvt_models', "
            "available pvt_models are: PVT1, PVT2, PVT3"
        )
        with pytest.raises(
            InvalidReferenceError,
            match=re.escape(expected_error),
        ):
            case.ensure_valid_references()

    def test_annulus_description_pvt_model(self, default_case, default_well):
        """
        If a AnnulusDescription uses an invalid PvtModel, an InvalidReferenceError must be raised.
        """
        case = attr.evolve(
            default_case,
            wells=[
                attr.evolve(
                    default_well,
                    annulus=case_description.AnnulusDescription(
                        has_annulus_flow=False, pvt_model="Acme", top_node="Node 1"
                    ),
                )
            ],
        )
        expected_error = (
            "PVT model 'Acme' selected on 'Annulus from Well 1' is not declared on 'pvt_models', "
            "available pvt_models are: PVT1, PVT2, PVT3"
        )
        with pytest.raises(
            InvalidReferenceError,
            match=re.escape(expected_error),
        ):
            case.ensure_valid_references()


def test_pvt_model_table_parameters_description_equal(table_parameters_description):
    import numpy as np

    table_params_1 = table_parameters_description(
        np.array([0.0]),  # pressure values
        np.array([0.0]),  # temperature or enthalpy values
        table_variables=[],
        variable_names=[],
        number_of_phases=-1,
    )
    table_params_2 = table_parameters_description(
        np.array([0.0]),  # pressure values
        np.array([0.0]),  # temperature or enthalpy values
        table_variables=[np.array([1, 2])],
        variable_names=[],
        number_of_phases=-1,
    )
    table_params_3 = table_parameters_description(
        np.array([0.0]),  # pressure values
        np.array([0.0]),  # temperature or enthalpy values
        table_variables=[np.array([2, 3])],
        variable_names=[],
        number_of_phases=-1,
    )

    # To get coverage on check "if type(self) is not type(other)"
    assert table_params_1 != "s"

    # To get coverage on check "len(self.table_variables) != len(other.table_variables)"
    assert table_params_1 != table_params_2

    # To get coverage on check "if not np.array_equal(array1, array2)"
    assert table_params_3 != table_params_2


def test_pvt_model_table_parameters_description_post_init(table_parameters_description):
    """
    Check that standard properties that have not been informed (None) is converted to np.nan
    for more details about this, check the docstring from  PvtModelPtTableParametersDescription.__attrs_post_init__
    """
    import numpy as np

    table_params = table_parameters_description(
        # Required params
        np.ndarray([1]),  # pressure values
        np.ndarray([1]),  # temperature or enthalpy values
        table_variables=[np.ndarray([1])],
        variable_names=["str"],
        # Optional params
        pressure_std=None,
        temperature_std=None,
        gas_density_std=None,
        oil_density_std=None,
        water_density_std=None,
        gas_oil_ratio=None,
        gas_liquid_ratio=None,
        water_cut=None,
        total_water_fraction=None,
    )
    assert table_params.pressure_std.value is np.nan
    assert table_params.temperature_std.value is np.nan
    assert table_params.gas_density_std.value is np.nan
    assert table_params.oil_density_std.value is np.nan
    assert table_params.water_density_std.value is np.nan
    assert table_params.gas_oil_ratio.value is np.nan
    assert table_params.gas_liquid_ratio.value is np.nan
    assert table_params.water_cut.value is np.nan
    assert table_params.total_water_fraction.value is np.nan

    # The following check are only for coverage purpose
    assert table_params.pressure_unit == "Pa"

    if (
        table_parameters_description
        == case_description.PvtModelPtTableParametersDescription
    ):
        assert table_params.temperature_unit == "K"
    else:
        assert table_params.enthalpy_unit == "J/kg"


def test_numpy_array_validator():
    import numpy as np

    @attr.s()
    class Dummy:
        x = attr.ib(validator=numpy_array_validator(dimension=1))

    expected_error_msg = (
        "'x' must be <class 'numpy.ndarray'> (got 1 that is a <class 'int'>)."
    )

    with pytest.raises(TypeError, match=re.escape(expected_error_msg)):
        Dummy(x=1)

    expected_error_msg = (
        "attribute 'x' from class 'Dummy' only accepts ndarray with "
        "dimension equals to 1, got a ndarray with dimension 2."
    )
    with pytest.raises(ValueError, match=re.escape(expected_error_msg)):
        Dummy(x=np.array([[1, 2], [3, 4]]))

    @attr.s()
    class DummyWithList:
        x = attr.ib(validator=numpy_array_validator(dimension=1, is_list=True))

    expected_error_msg = (
        "'x' must be <class 'list'> (got array([[1, 2],\\n       "
        "[3, 4]]) that is a <class 'numpy.ndarray'>)."
    )
    with pytest.raises(TypeError, match=re.escape(expected_error_msg)):
        DummyWithList(x=np.array([[1, 2], [3, 4]]))

    expected_error_msg = (
        "attribute 'x' from class 'DummyWithList' only accepts ndarray "
        "with dimension equals to 1, got a ndarray with dimension 2 on position 1."
    )
    with pytest.raises(ValueError, match=re.escape(expected_error_msg)):
        DummyWithList(x=[np.array([1, 2]), np.array([[1, 2], [3, 4]])])


def test_pvt_model_table_parameters_description_create_constant():
    import numpy as np
    from pytest import approx

    pressure_values = np.linspace(0.5, 1e10, 4)
    temperature_values = np.linspace(250, 500, 30)
    t, p = np.meshgrid(temperature_values, pressure_values)
    r = 286.9  # Air individual gas constant [J/kg.K]

    # Check constant_gas_density_model
    rho_g_ref = 42.0
    gas_density_expected_values = rho_g_ref + 0 * p.flatten()

    pvt = case_description.PvtModelPtTableParametersDescription.create_constant(
        ideal_gas=False, rho_g_ref=rho_g_ref
    )
    # Check gas_density_derivative_respect_pressure
    gas_density_derivative_expected_values = 0.0 / (r * t.flatten())

    assert pvt.table_variables[0] == approx(gas_density_expected_values)
    assert pvt.table_variables[1] == approx(gas_density_derivative_expected_values)


def test_pvt_model_table_parameters_description_create_constant_ph_table():
    import numpy as np
    from pytest import approx

    pressure_values = np.linspace(0.5, 1e10, 4)
    enthalpy_values = np.linspace(2617360.0, 2869860, 30)
    h, p = np.meshgrid(enthalpy_values, pressure_values)
    r = 286.9  # Air individual gas constant [J/kg.K]

    # Check constant_gas_density_model
    rho_g_ref = 42.0
    gas_density_expected_values = rho_g_ref + 0 * p.flatten()

    cp_g_ref = 1010.0
    h_l_ref = 104.86e3

    pvt = case_description.PvtModelPhTableParametersDescription.create_constant(
        ideal_gas=False,
        rho_g_ref=rho_g_ref,
        cp_g_ref=cp_g_ref,
        h_l_ref=h_l_ref,
        has_water=True,
    )

    t = pvt.table_variables[-1]  # [K]

    # Check gas_density_derivative_respect_pressure
    gas_density_derivative_expected_values = 1 / (r * t.flatten())

    h_lg = 2.260e6
    temperature_expected_values = (h.flatten() - h_lg - h_l_ref) / cp_g_ref

    assert pvt.table_variables[0] == approx(gas_density_expected_values)
    assert pvt.table_variables[1] == approx(gas_density_derivative_expected_values)
    # Temperature must be at last position
    assert pvt.table_variables[-1] == approx(temperature_expected_values)


def test_pvt_model_table_parameters_description_create_ph_table_with_dummy_dict():
    """
    Ensure that the dummy dict can create a dummy PH table
    """
    import numpy as np

    dummy_dict = (
        case_description.PvtModelPhTableParametersDescription.dummy_parameters_dict()
    )

    ph_table_description = case_description.PvtModelPhTableParametersDescription(
        **dummy_dict
    )

    assert ph_table_description.enthalpy_values == np.array([0.0])
    assert ph_table_description.variable_names == []


def test_get_value_and_unit_from_length_and_elevation_description_and_xand_ydescription():
    """
    Ensure that GetValueAndUnit returns a pair of values along with their units.
    """
    length_and_elevation = case_description.LengthAndElevationDescription(
        length=Array([0.0, 5.0, 7.0], "m"), elevation=Array([1.0] * 3, "m")
    )
    assert list(length_and_elevation.iter_values_and_unit()) == [
        ((0.0, "m"), (1.0, "m")),
        ((5.0, "m"), (1.0, "m")),
        ((7.0, "m"), (1.0, "m")),
    ]
    x_and_y = case_description.XAndYDescription(
        x=Array([1.0, 10.0, 100.0], "m"), y=Array([42.0] * 3, "m")
    )
    assert list(x_and_y.iter_values_and_unit()) == [
        ((1.0, "m"), (42.0, "m")),
        ((10.0, "m"), (42.0, "m")),
        ((100.0, "m"), (42.0, "m")),
    ]


def test_check_profile_description(default_case):
    """
    Ensures that the ProfileDescription only accepts either XAndYDescription or a LengthAndElevationDescription

    Check 1: length_and_elevation and x_and_y are mutually exclusive
    """
    msg = (
        "length_and_elevation and x_and_y are mutually exclusive and you must configure only one of them, got "
        "length_and_elevation=LengthAndElevationDescription(length=Array(length, [0.0, 5.0, 7.0], m), elevation=Array(length, [1.0, 1.0, 1.0], m)) "
        "and x_and_y=XAndYDescription(x=Array(length, [1.0, 10.0, 100.0], m), y=Array(length, [42.0, 42.0, 42.0], m))"
    )
    with pytest.raises(ValueError, match=re.escape(msg)):
        case_description.ProfileDescription(
            length_and_elevation=case_description.LengthAndElevationDescription(
                length=Array([0.0, 5.0, 7.0], "m"), elevation=Array([1.0] * 3, "m")
            ),
            x_and_y=case_description.XAndYDescription(
                x=Array([1.0, 10.0, 100.0], "m"), y=Array([42.0] * 3, "m")
            ),
        )

    # Empty Profile is allowed.
    profile = case_description.ProfileDescription(
        length_and_elevation=None, x_and_y=None
    )
    assert profile.length_and_elevation is None
    assert profile.x_and_y is None

    # Empty Array is allowed
    profile_2 = case_description.ProfileDescription(
        length_and_elevation=case_description.LengthAndElevationDescription(
            length=Array([], "m"), elevation=Array([], "m")
        ),
        x_and_y=None,
    )
    assert profile_2.x_and_y is None
    assert profile_2.length_and_elevation is not None
    assert profile_2.length_and_elevation.length.GetValues("m") == []
    assert profile_2.length_and_elevation.elevation.GetValues("m") == []


def test_collapse_array_repr():
    assert collapse_array_repr("array([1, 2, 3])") == "'array([...])'"


def test_to_array():
    type_error_msg = r"Expected pair \(values, unit\) or Array"

    assert to_array(None, is_optional=True) is None
    with pytest.raises(TypeError, match=type_error_msg):
        to_array(None)

    assert to_array(([1, 2, 3], "m")) == Array("length", [1, 2, 3], "m")
    with pytest.raises(TypeError, match=type_error_msg):
        to_array(("foo", [1, 2, 3], "m"))
    with pytest.raises(TypeError, match=type_error_msg):
        to_array("foo")

    array = Array("time", [0, 1.1, 2.2], "s")
    assert to_array(array) is array


def test_to_curve():
    type_error_msg = r"Expected pair \(image_array, domain_array\) or Curve"

    assert to_curve(None, is_optional=True) is None
    with pytest.raises(TypeError, match=type_error_msg):
        to_curve(None)

    image = Array("length", [1, 2, 3], "m")
    domain = Array("time", [0, 1.1, 2.2], "s")
    curve = Curve(image, domain)
    assert to_curve((([1, 2, 3], "m"), domain)) == curve
    with pytest.raises(
        TypeError, match=r"Curve image: Expected pair \(values, unit\) or Array"
    ):
        to_curve((("foo", [1, 2, 3], "m"), domain))
    with pytest.raises(TypeError, match=type_error_msg):
        to_curve(("foo", [1, 2, 3], "m"))
    with pytest.raises(TypeError, match=type_error_msg):
        to_curve("foo")

    assert to_curve(curve) is curve


@pytest.mark.parametrize(
    "attrib_creator, default",
    [
        (attrib_scalar, Scalar(1, "m")),
        (attrib_array, Array([1, 2, 3], "m")),
        (attrib_curve, Curve(Array([1, 2, 3], "m"), Array([0, 1.1, 2.2], "s"))),
    ],
)
def test_attrib_category_miss_match(attrib_creator: Callable, default: Any) -> None:
    with pytest.raises(ValueError, match="category and `category` must match"):
        attrib_creator(default, category="time")

    assert isinstance(attrib_creator(default), _CountingAttr)
    assert isinstance(attrib_creator(default, category="length"), _CountingAttr)


def test_attrib_curve_domain_category_miss_match() -> None:
    default = Curve(Array([1, 2, 3], "m"), Array([0, 1.1, 2.2], "s"))
    with pytest.raises(ValueError, match="category and `domain_category` must match"):
        attrib_curve(default, domain_category="length")

    assert isinstance(attrib_curve(default), _CountingAttr)
    assert isinstance(attrib_curve(default, domain_category="time"), _CountingAttr)


@pytest.mark.parametrize(
    "attrib_creator, default",
    [
        (attrib_scalar, (1, "m")),
        (attrib_array, ([1, 2, 3], "m")),
    ],
)
def test_attrib_category_required(attrib_creator, default):
    assert isinstance(attrib_creator(default, category="length"), _CountingAttr)

    with pytest.raises(
        ValueError,
        match=r"If `default` is not an? \S+ then `category` is required to be not `None`",
    ):
        attrib_creator(default)


@pytest.mark.parametrize("none_arg", ["category", "domain_category"])
def test_curve_attrib_category_and_domain_required(none_arg):
    category_args: dict[str, Any] = dict(category="length", domain_category="time")
    non_curve_default = (Array([1, 2, 3], "m"), Array([0, 1.1, 2.2], "s"))
    assert isinstance(attrib_curve(non_curve_default, **category_args), _CountingAttr)

    category_args[none_arg] = None
    expected_msg = (
        f"If `default` is not a curve then `{none_arg}` is required to be not `None`"
    )
    with pytest.raises(ValueError, match=expected_msg):
        attrib_curve(non_curve_default, **category_args)


def test_generate_multi_input():
    obtained = generate_multi_input("foo", "length", 1.2, "m")
    assert obtained == textwrap.dedent(
        """\
        # fmt: off
        foo_input_type: constants.MultiInputType = attrib_enum(default=constants.MultiInputType.Constant)
        foo: Scalar = attrib_scalar(
            default=Scalar('length', 1.2, 'm')
        )
        foo_curve: Curve = attrib_curve(
            default=Curve(Array('length', [], 'm'), Array('time', [], 's'))
        )
        # fmt: on"""
    )


def test_generate_multi_input_dict():
    obtained = generate_multi_input_dict("foo", "length")
    assert obtained == textwrap.dedent(
        """\
        # fmt: off
        foo_input_type: constants.MultiInputType = attrib_enum(default=constants.MultiInputType.Constant)
        foo: dict[str, Scalar] = attr.ib(
            default=attr.Factory(dict), validator=dict_of(Scalar),
            metadata={"type": "scalar_dict", "category": 'length'},
        )
        foo_curve: dict[str, Curve] = attr.ib(
            default=attr.Factory(dict), validator=dict_of(Curve),
            metadata={"type": "curve_dict", "category": 'length'},
        )
        # fmt: on"""
    )


def test_material_description_as_dict():
    """
    Ensure that the helper function AsDict returns a diction where the Scalar are tuple with value and unit.
    """

    from alfasim_sdk._internal import constants

    assert MaterialDescription(name="Acme").as_dict() == {
        "density": (1.0, "kg/m3"),
        "expansion": (0.0, "1/K"),
        "heat_capacity": (0.0, "J/kg.degC"),
        "inner_emissivity": (0.0, "-"),
        "material_type": constants.MaterialType.Solid,
        "name": "Acme",
        "outer_emissivity": (0.0, "-"),
        "thermal_conductivity": (0.0, "W/m.degC"),
        "viscosity": (0.0, "cP"),
    }


def test_pvt_model_table_parameters_description_equality(table_parameters_description):
    """
    Ensure that the custom PvtModelPtTableParametersDescription equality functions works properly
    since it was customized to suport ndarrays.
    """
    assert (
        table_parameters_description.create_constant()
        == table_parameters_description.create_constant()
    )


def test_invalid_fluid_reference_on_nodes():
    """
    Ensure that only declared Fluids can be used on NodeDescription
    """
    case = case_description.CaseDescription(
        pvt_models=case_description.PvtModelsDescription(
            default_model="PVT",
            compositional={
                "PVT": case_description.PvtModelCompositionalDescription(
                    fluids={"Fluid 1": case_description.CompositionalFluidDescription()}
                )
            },
        ),
        nodes=[
            case_description.NodeDescription(
                name="Node 1",
                node_type=NodeCellType.Internal,
                internal_properties=case_description.InternalNodePropertiesDescription(
                    fluid="Acme2"
                ),
            ),
            case_description.NodeDescription(
                name="Node 2",
                node_type=NodeCellType.Pressure,
                pressure_properties=case_description.PressureNodePropertiesDescription(
                    fluid="Acme3"
                ),
            ),
            case_description.NodeDescription(
                name="Node 3",
                node_type=NodeCellType.MassSource,
                mass_source_properties=case_description.MassSourceNodePropertiesDescription(
                    fluid="Acme4"
                ),
            ),
        ],
    )

    expected_error = "The following elements have an invalid fluid assigned: 'Node 1', 'Node 2', 'Node 3'."
    with pytest.raises(InvalidReferenceError, match=re.escape(expected_error)):
        case.ensure_valid_references()

    case.reset_invalid_references()
    assert case.nodes[0].internal_properties.fluid is None
    assert case.nodes[1].pressure_properties.fluid is None
    assert case.nodes[2].mass_source_properties.fluid is None


def test_invalid_fluid_reference_on_pipes():
    """
    Ensure that only declared Fluids can be used on:
       PipeDescription, MassSourceEquipmentDescription, ReservoirInflowEquipmentDescription.
    """
    case = case_description.CaseDescription(
        pvt_models=case_description.PvtModelsDescription(
            default_model="PVT",
            compositional={
                "PVT": case_description.PvtModelCompositionalDescription(
                    fluids={"Fluid 1": case_description.CompositionalFluidDescription()}
                )
            },
        ),
        pipes=[
            case_description.PipeDescription(
                name="Pipe 1",
                source="",
                target="",
                segments=build_simple_segment(),
                initial_conditions=case_description.InitialConditionsDescription(
                    fluid="acme5"
                ),
                equipment=case_description.EquipmentDescription(
                    mass_sources={
                        "MassSource": case_description.MassSourceEquipmentDescription(
                            position=Scalar(1, "m"), fluid="a6"
                        )
                    },
                    reservoir_inflows={
                        "Reservoir": case_description.ReservoirInflowEquipmentDescription(
                            start=Scalar(1, "m"), length=Scalar(10, "m"), fluid="a7"
                        )
                    },
                ),
            )
        ],
    )
    expected_error = "The following elements have an invalid fluid assigned: 'MassSource from Pipe 1', 'Pipe 1', 'Reservoir from Pipe 1'."
    with pytest.raises(InvalidReferenceError, match=re.escape(expected_error)):
        case.ensure_valid_references()

    case.reset_invalid_references()
    pipe = case.pipes[0]
    assert pipe.initial_conditions.fluid is None
    assert pipe.equipment.mass_sources["MassSource"].fluid is None
    assert pipe.equipment.reservoir_inflows["Reservoir"].fluid is None


def test_invalid_fluid_reference_on_wells(default_well):
    """
    Ensure that only declared Fluids can be used on WellDescription and AnnulusDescription.
    """
    case = case_description.CaseDescription(
        pvt_models=case_description.PvtModelsDescription(
            default_model="PVT",
            compositional={
                "PVT": case_description.PvtModelCompositionalDescription(
                    fluids={"Fluid 1": case_description.CompositionalFluidDescription()}
                )
            },
        ),
        wells=[
            attr.evolve(
                default_well,
                initial_conditions=attr.evolve(
                    default_well.initial_conditions,
                    fluid="acme",
                ),
                annulus=attr.evolve(
                    default_well.annulus,
                    initial_conditions=attr.evolve(
                        default_well.annulus.initial_conditions,
                        fluid="acme",
                    ),
                ),
            )
        ],
    )
    expected_error = "The following elements have an invalid fluid assigned: 'Annulus from Well 1', 'Well 1'."
    with pytest.raises(InvalidReferenceError, match=re.escape(expected_error)):
        case.ensure_valid_references()

    case.reset_invalid_references()
    well = case.wells[0]
    assert well.initial_conditions.fluid is None
    assert well.annulus.initial_conditions.fluid is None


def test_case_description_duplicate_names(default_well):
    """
    Pipes because they are reference by OutputDescription
    Nodes because they are referenced by PipeDescription, WellDescription and OutputDescription
    PVTs names, because of default_model
    Wall Names because of PipeSegmentsDescription
    Material because of WellDescription(stagnant_fluid), CasingSectionDescription, TubingDescription
    """
    well_1 = attr.evolve(default_well, name="Well 1")
    well_2 = attr.evolve(default_well, name="Well 1")

    case = case_description.CaseDescription(
        materials=[
            case_description.MaterialDescription(name="Material"),
            case_description.MaterialDescription(name="Material"),
        ],
        walls=[
            case_description.WallDescription(name="Wall A"),
            case_description.WallDescription(name="Wall A"),
        ],
        pvt_models=case_description.PvtModelsDescription(
            default_model="PVT",
            correlations={
                "PVT1": case_description.PvtModelCorrelationDescription(),
            },
            compositional={
                "PVT1": case_description.PvtModelCompositionalDescription(
                    fluids={
                        "Fluid 0": case_description.CompositionalFluidDescription(),
                        "Fluid 1": case_description.CompositionalFluidDescription(),
                    },
                ),
                "PVT2": case_description.PvtModelCompositionalDescription(
                    fluids={
                        "Fluid 0": case_description.CompositionalFluidDescription(),
                        "Fluid 1": case_description.CompositionalFluidDescription(),
                    }
                ),
            },
        ),
        nodes=[
            case_description.NodeDescription(
                name="ACME", node_type=NodeCellType.Pressure
            ),
            case_description.NodeDescription(
                name="ACME", node_type=NodeCellType.Pressure
            ),
            case_description.NodeDescription(
                name="Node1", node_type=NodeCellType.Pressure
            ),
            case_description.NodeDescription(
                name="FOO", node_type=NodeCellType.Pressure
            ),
            case_description.NodeDescription(
                name="FOO", node_type=NodeCellType.Pressure
            ),
        ],
        pipes=[
            case_description.PipeDescription(
                name="Pipe 1",
                source="ACME",
                target="ACME",
                segments=build_simple_segment(),
            ),
            case_description.PipeDescription(
                name="Pipe 1",
                source="ACME",
                target="ACME",
                segments=build_simple_segment(),
            ),
        ],
        wells=[well_1, well_2],
    )

    expected_msg = dedent(
        """\
        Elements that can be referenced must have a unique name, found multiples definitions of the following items:
        Fluids:
            - Fluid 0
            - Fluid 1
        Materials:
            - Material
        Nodes:
            - ACME
            - FOO
        PVT:
            - PVT1
        Pipes:
            - Pipe 1
        Walls:
            - Wall A
        Wells:
            - Well 1"""
    )

    with pytest.raises(InvalidReferenceError, match=re.escape(expected_msg)):
        case.ensure_unique_names()


def test_case_description_duplicate_names_between_elements(default_well):
    """
    Ensure Pipes and Wells has unique names (because of OutputDefinition)
    Ensure Nodes and Wells has unique names (because of Edge source/target)
    """
    well_1 = attr.evolve(default_well, name="ACME Node <-> Well")
    well_2 = attr.evolve(default_well, name="ACME Pipe <-> Well")

    case = case_description.CaseDescription(
        nodes=[
            case_description.NodeDescription(
                name="ACME Node <-> Well", node_type=NodeCellType.Pressure
            ),
            case_description.NodeDescription(
                name="Node1", node_type=NodeCellType.Pressure
            ),
        ],
        pipes=[
            case_description.PipeDescription(
                name="ACME Pipe <-> Well",
                source="ACME",
                target="ACME",
                segments=build_simple_segment(),
            ),
            case_description.PipeDescription(
                name="Pipe 1",
                source="ACME",
                target="ACME",
                segments=build_simple_segment(),
            ),
        ],
        wells=[well_1, well_2],
    )

    expected_msg = dedent(
        """\
        Some different type of elements needs to have unique name between them, found duplicated names for the following items:
        Nodes and Wells:
            - ACME Node <-> Well
        Pipes and Wells:
            - ACME Pipe <-> Well"""
    )

    with pytest.raises(InvalidReferenceError, match=re.escape(expected_msg)):
        case.ensure_unique_names()


def test_check_fluid_references(default_well: case_description.WellDescription) -> None:
    """
    Test _check_fluid_references isn't yielding errors for a correct CaseDescription.
    """

    known_pvt_properties = set(
        attr.fields_dict(case_description.PvtModelsDescription).keys()
    )
    # Be sure to update the 'known_pvt_models' in CaseDescription._get_all_fluids
    # if this assert breaks because a new PVT Model was added.
    assert known_pvt_properties == {
        "combined",
        "compositional",
        "correlations",
        "default_model",
        "pt_table_parameters",
        "ph_table_parameters",
        "tables",
        "constant_properties",
    }

    case = case_description.CaseDescription(
        pvt_models=case_description.PvtModelsDescription(
            default_model="Default PVT",
            correlations={
                "Default PVT": case_description.PvtModelCorrelationDescription()
            },
            combined={
                "Test PVT Combined": case_description.PvtModelCombinedDescription(
                    fluids={
                        "Test Fluid Combined": case_description.CombinedFluidDescription(
                            "Default PVT"
                        )
                    }
                ),
            },
            compositional={
                "Test PVT Compositional": case_description.PvtModelCompositionalDescription(
                    fluids={
                        "Test Fluid Compositional": case_description.CompositionalFluidDescription()
                    }
                ),
            },
        )
    )

    pvt_models_and_fluids = [
        ("Test PVT Combined", "Test Fluid Combined"),
        ("Test PVT Compositional", "Test Fluid Compositional"),
    ]
    for pvt_model, fluid in pvt_models_and_fluids:
        well = attr.evolve(
            default_well,
            pvt_model=pvt_model,
            initial_conditions=case_description.InitialConditionsDescription(
                fluid=fluid
            ),
        )

        case = attr.evolve(
            case,
            wells=[well],
        )

        case.ensure_valid_references()
