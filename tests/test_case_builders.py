import pytest
from barril.units import Array

from .common_testing.alfasim_sdk_common_testing.case_builders import (
    build_compressor_pressure_table_description,
)
from .common_testing.alfasim_sdk_common_testing.case_builders import (
    build_constant_initial_pressure_description,
)
from .common_testing.alfasim_sdk_common_testing.case_builders import (
    build_constant_initial_temperatures_description,
)
from .common_testing.alfasim_sdk_common_testing.case_builders import (
    build_constant_pvt_table,
)
from .common_testing.alfasim_sdk_common_testing.case_builders import (
    build_linear_initial_pressure_description,
)
from .common_testing.alfasim_sdk_common_testing.case_builders import (
    build_linear_initial_temperatures_description,
)
from alfasim_sdk._internal import constants


def test_build_constant_initial_temperatures_description():
    description = build_constant_initial_temperatures_description(1.1, "K")
    assert description.position_input_type == constants.TableInputType.length
    assert len(description.table_length.positions) == 1
    assert len(description.table_length.temperatures) == 1
    assert description.table_length.positions[0] == 0.0
    assert description.table_length.temperatures[0] == 1.1


def test_build_constant_initial_pressure_description():
    description = build_constant_initial_pressure_description(1.1, "bar")
    assert description.position_input_type == constants.TableInputType.length
    assert len(description.table_length.positions) == 1
    assert len(description.table_length.pressures) == 1
    assert description.table_length.positions[0] == 0.0
    assert description.table_length.pressures[0] == 1.1


def test_build_linear_initial_temperatures_description():
    description = build_linear_initial_temperatures_description(
        1.1, 2.2, "K", 10.1, "m", start_position=20.2
    )
    assert description.position_input_type == constants.TableInputType.length
    assert len(description.table_length.positions) == 2
    assert len(description.table_length.temperatures) == 2
    assert description.table_length.positions[0] == 20.2
    assert description.table_length.positions[1] == 10.1
    assert description.table_length.temperatures[0] == 1.1
    assert description.table_length.temperatures[1] == 2.2


def test_build_linear_initial_pressure_description():
    description = build_linear_initial_pressure_description(
        1.1, 2.2, "bar", 10.1, "m", start_position=20.2
    )
    assert description.position_input_type == constants.TableInputType.length
    assert len(description.table_length.positions) == 2
    assert len(description.table_length.pressures) == 2
    assert description.table_length.positions[0] == 20.2
    assert description.table_length.positions[1] == 10.1
    assert description.table_length.pressures[0] == 1.1
    assert description.table_length.pressures[1] == 2.2


def test_build_compressor_pressure_table_description_valid():
    description = build_compressor_pressure_table_description(
        speed_entries=Array([0, 1000], "rpm"),
        corrected_mass_flow_rate_entries=Array([1, 2, 3], "kg/s"),
        pressure_ratio_table=Array([1, 2, 3, 4, 5, 6], "-"),
        isentropic_efficiency_table=Array([0.4, 0.5, 0.6, 0.7, 0.8, 0.9], "-"),
    )
    assert description.speed_entries == Array([0, 0, 0, 1000, 1000, 1000], "rpm")
    assert description.corrected_mass_flow_rate_entries == Array(
        [1, 2, 3, 1, 2, 3], "kg/s"
    )
    assert description.pressure_ratio_table == Array([1, 2, 3, 4, 5, 6], "-")
    assert description.isentropic_efficiency_table == Array(
        [0.4, 0.5, 0.6, 0.7, 0.8, 0.9], "-"
    )


@pytest.mark.parametrize(
    "pressure_ratios, isentropic_efficiencies, error_msg",
    [
        # Size checks
        (
            [1, 2],
            [0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            "Missing pressure entries. Expected 6 but got 2",
        ),
        (
            [1, 2, 3, 4, 5, 6],
            [0.4],
            "Missing isentropic efficiency entries. Expected 6 but got 1",
        ),
        # Value checks
        (
            [0, 1, 2, 3, 4, 5],
            [0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            "Pressure Ratio must be greater than 0",
        ),
        (
            [1, 2, 3, 4, 5, 6],
            [0, 0.5, 0.6, 0.7, 0.8, 0.9],
            "Isentropic efficiency must be greater than 0 and lower or equal to 1",
        ),
        (
            [1, 2, 3, 4, 5, 6],
            [0.4, 0.5, 0.6, 0.7, 0.8, 1.1],
            "Isentropic efficiency must be greater than 0 and lower or equal to 1",
        ),
    ],
)
def test_build_compressor_pressure_table_description_invalid(
    pressure_ratios, isentropic_efficiencies, error_msg
):
    with pytest.raises(AssertionError, match=error_msg):
        build_compressor_pressure_table_description(
            speed_entries=Array([0, 1000], "rpm"),
            corrected_mass_flow_rate_entries=Array([1, 2, 3], "kg/s"),
            pressure_ratio_table=Array(pressure_ratios, "-"),
            isentropic_efficiency_table=Array(isentropic_efficiencies, "-"),
        )


@pytest.mark.parametrize(
    "energy_model_primary_variable, table_name",
    [
        (
            constants.EnergyModelPrimaryVariable.Temperature,
            "constant pt table",
        ),
        (constants.EnergyModelPrimaryVariable.Enthalpy, "constant ph table"),
    ],
)
def test_build_constant_pvt_table(energy_model_primary_variable, table_name):
    pvt_model_description = build_constant_pvt_table(energy_model_primary_variable)

    assert pvt_model_description.default_model == table_name
