import re
from textwrap import dedent

import attr
import pytest
from barril.units import Array
from barril.units import Scalar

from alfasim_sdk import constants
from alfasim_sdk.alfacase import case_description
from alfasim_sdk.alfacase.case_description import attrib_enum
from alfasim_sdk.alfacase.case_description import attrib_instance
from alfasim_sdk.alfacase.case_description import attrib_instance_list
from alfasim_sdk.alfacase.case_description import attrib_scalar
from alfasim_sdk.alfacase.case_description import collapse_array_repr
from alfasim_sdk.alfacase.case_description import MaterialDescription
from alfasim_sdk.alfacase.case_description import numpy_array_validator
from alfasim_sdk.alfacase.case_description import PvtModelTableParametersDescription
from alfasim_sdk.common_testing.case_builders import build_simple_segment
from alfasim_sdk.constants import NodeCellType


def test_physics_description_path_validator(tmp_path):
    """
    Ensure PhysicsDescription.restart_filepath only accepts created files
    """
    from pathlib import Path
    import re

    expected_error = re.escape(
        f"'restart_filepath' must be {Path} (got '' that is a {str})."
    )
    with pytest.raises(TypeError, match=expected_error):
        case_description.PhysicsDescription(restart_filepath="")

    tmp_file = tmp_path / "tmp.txt"
    tmp_file.touch()
    assert case_description.PhysicsDescription(restart_filepath=tmp_file)
    assert case_description.PhysicsDescription(restart_filepath=None)


def test_opening_curve_description():
    expected_msg = "Time and Opening must have the same size, got 2 items for time and 3 for opening"
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        case_description.OpeningCurveDescription(
            time=Array([0.0, 0.5], "s"), opening=Array([0.1, 0.2, 0.2], "-")
        )


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
    speeds, void_fractions, flow_rates and pressure_boosts must have the same size, got :
        - 2 items for speeds
        - 2 items for void_fractions
        - 2 items for flow_rates
        - 1 items for pressure_boosts
    """
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        case_description.TablePumpDescription(
            speeds=Array([1, 2], "rpm"),
            void_fractions=Array([1, 2], "-"),
            flow_rates=Array([1, 2], "m3/s"),
            pressure_boosts=Array([1], "bar"),
        )

    # Check if the defaults values works well
    case_description.TablePumpDescription()


def test_instance_attribute_list():
    @attr.s
    class X:
        pass

    @attr.s
    class Y:
        pass

    @attr.s(kw_only=True)
    class Foo:
        attr_1 = attrib_instance_list(X)
        attr_1_validator_type = attrib_instance_list(X, validator_type=(X, Y))

    # Check validator of attrib_instance_list
    expected_msg = f"'attr_1' must be {list} (got X() that is a {X})."
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(attr_1=X())

    expected_msg = f"'attr_1' must be {X} (got Y() that is a {Y})."
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(attr_1=[Y()])

    expected_msg = f"'attr_1' must be {list} (got None that is a {type(None)})."
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(attr_1=None)

    # Smoke check
    assert Foo(attr_1=[X()])
    assert Foo(attr_1_validator_type=[Y()])


def test_instance_attribute():
    @attr.s
    class X:
        pass

    @attr.s
    class Y:
        pass

    @attr.s(kw_only=True)
    class Foo:
        attr_1 = attrib_instance(X)
        attr_2 = attrib_instance_list(X)
        attr_2_validator_type = attrib_instance_list(X, validator_type=(X, Y))

    # Check validator of attrib_instance
    expected_msg = f"'attr_1' must be {X} (got Y() that is a {Y})."
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(attr_1=Y())

    # Smoke check
    assert Foo(attr_1=X())


def test_scalar_attribute():
    @attr.s(kw_only=True)
    class Foo:
        position = attrib_scalar(default=Scalar(1, "m"))
        position_2 = attrib_scalar(default=None)

    # Check position
    instance_with_scalar = Foo(position=Scalar(1, "m"))
    assert isinstance(instance_with_scalar.position, Scalar)

    instance_with_tuple = Foo(position=(1, "m"))
    assert isinstance(instance_with_tuple.position, Scalar)

    expected_msg = (
        "Expected pair (value, unit) or Scalar, got None (type: <class 'NoneType'>)"
    )
    with pytest.raises(TypeError, match=re.escape(expected_msg)):
        Foo(position=None)

    # Check position_1 (accepts None)
    instance_with_scalar = Foo(position_2=Scalar(1, "m"))
    assert isinstance(instance_with_scalar.position, Scalar)

    instance_with_tuple = Foo(position_2=(1, "m"))
    assert isinstance(instance_with_tuple.position, Scalar)

    assert Foo(position_2=None).position_2 is None


def test_enum_attribute():
    from enum import Enum

    class X(Enum):
        A = "A"
        B = "B"

    @attr.s(kw_only=True)
    class Foo:
        attr_1 = attrib_enum(default=X.A)

    # Check validator of Enum
    expected_msg_for_enum = "'attr_1' must be in <enum 'X'> (got 's')"
    with pytest.raises(ValueError, match=re.escape(expected_msg_for_enum)):
        Foo(attr_1="s")

    # Type_ is mandatory when default is not provided
    expected_msg = "Default or type_ parameter must be provided"
    with pytest.raises(RuntimeError, match=re.escape(expected_msg)):
        attrib_enum()

    # When informing default, the type_ is optional
    assert attrib_enum(default=X.A).type is X

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
            compositions={"PVT3": case_description.PvtModelCompositionalDescription()},
            table_parameters={
                "PVT4": case_description.PvtModelTableParametersDescription.create_empty()
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
    """ Helper function to get a empty profile for tests. """
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
    """ Ensure that the method EnsureValidReferences from CaseDescription catches errors with invalid restart files. """
    restart_file = tmp_path / "dummy.restart"
    case = attr.evolve(
        default_case,
        physics=case_description.PhysicsDescription(
            initial_condition_strategy=constants.InitialConditionStrategyType.Restart,
            restart_filepath=restart_file,
        ),
    )
    expected_error = re.escape(f"Restart file '{restart_file}' is not a valid file")
    with pytest.raises(case_description.InvalidReferenceError, match=expected_error):
        case.ensure_valid_references()

    restart_file.write_text("Restart file contents")
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
                default_model="PVT1", tables={"PVT1": f"{tmp_path/'dummy.tab'}|INVALID"}
            ),
        )
        case.reset_invalid_references()
        assert case.pvt_models.tables == {}
        assert case.pvt_models.default_model is None
        case = case_description.CaseDescription(
            pvt_models=case_description.PvtModelsDescription(
                default_model="PVT2", tables={"PVT2": f"{tmp_path/'dummy.tab'}|PVT2"}
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

    def test_pvt_model_are_valid(self, default_case):
        """
        Check that the validation for invalid references works for all types of PvtModel. (Composition, Correlation, Tables and TableParameters).
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
            ],
        )
        expect_message = "PVT model 'PVT5' select on 'Pipe 5' is not declared on 'pvt_models', available pvt_models are: PVT1, PVT2, PVT3, PVT4"
        with pytest.raises(
            case_description.InvalidReferenceError, match=re.escape(expect_message)
        ):
            case.ensure_valid_references()

    def test_pvt_model_from_file_is_in_valid(self, default_case, tmp_path):
        """
        When a PVTModel informed from the user on a file doesn't exist,
        a InvalidReferenceError must be raised when case.EnsureValidReferences is called.
        """
        case = attr.evolve(
            default_case,
            pvt_models=case_description.PvtModelsDescription(
                default_model="PVT1", tables={"PVT1": f"{tmp_path/'dummy.tab'}|INVALID"}
            ),
        )
        expect_message = "'INVALID' could not be found on 'dummy.tab', available models are: 'PVT1, PVT2'"
        with pytest.raises(
            case_description.InvalidReferenceError, match=re.escape(expect_message)
        ):
            case.ensure_valid_references()

        # Ensure the test finishes in a valid state
        case = case_description.CaseDescription(
            pvt_models=case_description.PvtModelsDescription(
                default_model="PVT2", tables={"PVT2": f"{tmp_path/'dummy.tab'}|PVT2"}
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
            case_description.InvalidReferenceError, match=re.escape(expect_message)
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
        from alfasim_sdk.constants import NodeCellType

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
            case_description.InvalidReferenceError, match=re.escape(expected_msg)
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
            case_description.InvalidReferenceError, match=re.escape(expected_msg)
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
            "PVT model 'Acme' select on 'Pipe 1' is not declared on 'pvt_models', "
            "available pvt_models are: PVT1, PVT2, PVT3"
        )
        with pytest.raises(
            case_description.InvalidReferenceError, match=re.escape(expected_error)
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
            "PVT model 'Foo' select on 'Node 1' is not declared on 'pvt_models', "
            "available pvt_models are: PVT1, PVT2, PVT3"
        )
        with pytest.raises(
            case_description.InvalidReferenceError, match=re.escape(expected_error)
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
            "PVT model 'Foo' select on 'Well 1' is not declared on 'pvt_models', "
            "available pvt_models are: PVT1, PVT2, PVT3"
        )
        with pytest.raises(
            case_description.InvalidReferenceError, match=re.escape(expected_error)
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
            "PVT model 'Acme' select on 'Annulus from Well 1' is not declared on 'pvt_models', "
            "available pvt_models are: PVT1, PVT2, PVT3"
        )
        with pytest.raises(
            case_description.InvalidReferenceError, match=re.escape(expected_error)
        ):
            case.ensure_valid_references()


def test_pvt_model_table_parameters_description_equal():
    import numpy as np

    table_params_1 = case_description.PvtModelTableParametersDescription(
        pressure_values=np.array([0.0]),
        temperature_values=np.array([0.0]),
        table_variables=[],
        variable_names=[],
        number_of_phases=-1,
    )
    table_params_2 = case_description.PvtModelTableParametersDescription(
        pressure_values=np.array([0.0]),
        temperature_values=np.array([0.0]),
        table_variables=[np.array([1, 2])],
        variable_names=[],
        number_of_phases=-1,
    )
    table_params_3 = case_description.PvtModelTableParametersDescription(
        pressure_values=np.array([0.0]),
        temperature_values=np.array([0.0]),
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


def test_pvt_model_table_parameters_description_post_init():
    """
    Check that standard properties that have not been informed (None) is converted to np.nan
    for more details about this, check the docstring from  PvtModelTableParametersDescription.__attrs_post_init__
    """
    import numpy as np

    table_params = case_description.PvtModelTableParametersDescription(
        pressure_std=None,
        temperature_std=None,
        gas_density_std=None,
        oil_density_std=None,
        water_density_std=None,
        gas_oil_ratio=None,
        gas_liquid_ratio=None,
        water_cut=None,
        total_water_fraction=None,
        # Required params
        pressure_values=np.ndarray([1]),
        temperature_values=np.ndarray([1]),
        table_variables=[np.ndarray([1])],
        variable_names=["str"],
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
    assert table_params.temperature_unit == "K"


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

    pressure_values = np.linspace(0.5, 1e10, 4)
    temperature_values = np.linspace(250, 500, 30)
    t, p = np.meshgrid(temperature_values, pressure_values)
    r = 286.9  # Air individual gas constant [J/kg K]

    # Check constant_gas_density_model
    rho_g_ref = 42.0
    expected_value = rho_g_ref + 0 * p

    pvt = case_description.PvtModelTableParametersDescription.create_constant(
        ideal_gas=False, rho_g_ref=rho_g_ref
    )
    np.array_equal(pvt.table_variables[0], expected_value.flatten())

    # Check gas_density_derivative_respect_pressure
    expected_value = 1 / (r * t)
    np.array_equal(pvt.table_variables[1], expected_value.flatten())


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
    assert profile_2.length_and_elevation.length.GetValues("m") == []
    assert profile_2.length_and_elevation.elevation.GetValues("m") == []


def test_collapse_array_repr():
    assert collapse_array_repr("array([1, 2, 3])") == "'array([...])'"


def test_material_description_as_dict():
    """
    Ensure that the helper function AsDict returns a diction where the Scalar are tuple with value and unit.
    """

    from alfasim_sdk import constants

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


def test_pvt_model_table_parameters_description_equality():
    """
    Ensure that the custom PvtModelTableParametersDescription equality functions works properly
    since it was customized to suport ndarrays.
    """
    assert (
        PvtModelTableParametersDescription.create_constant()
        == PvtModelTableParametersDescription.create_constant()
    )
