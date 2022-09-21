from barril.units import Array
from barril.units import Scalar

from alfasim_sdk._internal import constants
from alfasim_sdk._internal.alfacase import case_description


def build_simple_segment():
    """
    Return an instance of PipeSegmentsDescription with a pre-populated value.

    The pre-filled value was the default value used by all tests before refactoring,
    which removed `diameter` and `absolute_roughness` from PipeDescription.
    """
    return case_description.PipeSegmentsDescription(
        start_positions=Array([0.0], "m"),
        diameters=Array([0.1], "m"),
        roughnesses=Array([1e-5], "m"),
    )


def build_constant_initial_pressure_description(value, unit):
    return case_description.InitialPressuresDescription(
        position_input_type=constants.TableInputType.length,
        table_length=case_description.PressureContainerDescription(
            positions=Array([0.0], "m"), pressures=Array([value], unit)
        ),
    )


def build_constant_initial_volume_fractions_description(values):
    return case_description.InitialVolumeFractionsDescription(
        position_input_type=constants.TableInputType.length,
        table_length=case_description.VolumeFractionsContainerDescription(
            positions=Array([0.0], "m"),
            fractions={k: Array([v.value], v.unit) for k, v in values.items()},
        ),
    )


def build_constant_initial_tracers_mass_fractions_description(values, unit):
    return case_description.InitialTracersMassFractionsDescription(
        position_input_type=constants.TableInputType.length,
        table_length=case_description.TracersMassFractionsContainerDescription(
            positions=Array([0.0], "m"), tracers_mass_fractions=[Array(values, unit)]
        ),
    )


def build_constant_initial_velocities_description(values):
    return case_description.InitialVelocitiesDescription(
        position_input_type=constants.TableInputType.length,
        table_length=case_description.VelocitiesContainerDescription(
            positions=Array([0.0], "m"),
            velocities={key: Array([v.value], v.unit) for key, v in values.items()},
        ),
    )


def build_constant_initial_temperatures_description(value, unit):
    return case_description.InitialTemperaturesDescription(
        position_input_type=constants.TableInputType.length,
        table_length=case_description.TemperaturesContainerDescription(
            positions=Array([0.0], "m"), temperatures=Array([value], unit)
        ),
    )


def build_linear_initial_temperatures_description(
    from_temperature,
    to_temperature,
    unit,
    final_position,
    position_unit,
    start_position=0.0,
):
    return case_description.InitialTemperaturesDescription(
        position_input_type=constants.TableInputType.length,
        table_length=case_description.TemperaturesContainerDescription(
            positions=Array(
                [
                    Scalar(start_position, position_unit).GetValue("m"),
                    Scalar(final_position, position_unit).GetValue("m"),
                ],
                "m",
            ),
            temperatures=Array([from_temperature, to_temperature], unit),
        ),
    )


def build_linear_initial_pressure_description(
    from_pressure,
    to_pressure,
    unit,
    final_position,
    position_unit,
    start_position=0.0,
):
    return case_description.InitialPressuresDescription(
        position_input_type=constants.TableInputType.length,
        table_length=case_description.PressureContainerDescription(
            positions=Array(
                [
                    Scalar(start_position, position_unit).GetValue("m"),
                    Scalar(final_position, position_unit).GetValue("m"),
                ],
                "m",
            ),
            pressures=Array([from_pressure, to_pressure], unit),
        ),
    )


def build_compressor_pressure_table_description(
    speed_entries,
    corrected_mass_flow_rate_entries,
    pressure_ratio_table,
    isentropic_efficiency_table,
):
    """
    Helper to build a table for CompressorPressureTable from a parametrized input of `speed_entries`
    and `corrected_mass_flow_rate_entries`, correcting it so len(pressure_ratio_table) and
    len(isentropic_efficiency_table) have elements = len(speed_entries) * len(corrected_mass_flow_rate_entries),
    making it a explicit table with all combinations.
    """
    expected_size = len(speed_entries) * len(corrected_mass_flow_rate_entries)
    assert expected_size == len(
        pressure_ratio_table
    ), f"Missing pressure entries. Expected {expected_size} but got {len(pressure_ratio_table)}"
    assert expected_size == len(
        isentropic_efficiency_table
    ), f"Missing isentropic efficiency entries. Expected {expected_size} but got {len(isentropic_efficiency_table)}"

    adjusted_speeds = []
    adjusted_flow_rates = []
    for speed in speed_entries:
        for flow_rate in corrected_mass_flow_rate_entries:
            adjusted_speeds.append(speed)
            adjusted_flow_rates.append(flow_rate)

    return case_description.CompressorPressureTableDescription(
        speed_entries=Array(adjusted_speeds, speed_entries.unit),
        corrected_mass_flow_rate_entries=Array(
            adjusted_flow_rates, corrected_mass_flow_rate_entries.unit
        ),
        pressure_ratio_table=pressure_ratio_table,
        isentropic_efficiency_table=isentropic_efficiency_table,
    )


def build_constant_pvt_table(
    energy_model_primary_variable: constants.EnergyModelPrimaryVariable,
):
    if (
        energy_model_primary_variable
        == constants.EnergyModelPrimaryVariable.Temperature
    ):
        return case_description.PvtModelsDescription(
            default_model='constant pt table',
            pt_table_parameters={
                'constant pt table': case_description.PvtModelTableParametersDescription.create_constant()
            },
        )
    elif energy_model_primary_variable == constants.EnergyModelPrimaryVariable.Enthalpy:
        return case_description.PvtModelsDescription(
            default_model='constant ph table',
            ph_table_parameters={
                'constant ph table': case_description.PhPvtModelTableParametersDescription.create_constant()
            },
        )
    else:  # pragma no cover
        assert False, f"{energy_model_primary_variable} not supported."
