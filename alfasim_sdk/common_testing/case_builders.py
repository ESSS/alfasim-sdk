from barril.units import Array
from barril.units import Scalar

from alfasim_sdk.alfacase import case_description


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

    from alfasim_sdk import constants

    return case_description.InitialPressuresDescription(
        position_input_type=constants.TableInputType.length,
        table_length=case_description.PressureContainerDescription(
            positions=Array([0.0], "m"), pressures=Array([value], unit)
        ),
    )


def build_constant_initial_volume_fractions_description(values):

    from alfasim_sdk import constants

    return case_description.InitialVolumeFractionsDescription(
        position_input_type=constants.TableInputType.length,
        table_length=case_description.VolumeFractionsContainerDescription(
            positions=Array([0.0], "m"),
            fractions={k: Array([v.value], v.unit) for k, v in values.items()},
        ),
    )


def build_constant_initial_tracers_mass_fractions_description(values, unit):
    from alfasim_sdk import constants

    return case_description.InitialTracersMassFractionsDescription(
        position_input_type=constants.TableInputType.length,
        table_length=case_description.TracersMassFractionsContainerDescription(
            positions=Array([0.0], "m"), tracers_mass_fractions=[Array(values, unit)]
        ),
    )


def build_constant_initial_velocities_description(values):
    from alfasim_sdk import constants

    return case_description.InitialVelocitiesDescription(
        position_input_type=constants.TableInputType.length,
        table_length=case_description.VelocitiesContainerDescription(
            positions=Array([0.0], "m"),
            velocities={key: Array([v.value], v.unit) for key, v in values.items()},
        ),
    )


def build_constant_initial_temperatures_description(value, unit):
    from alfasim_sdk import constants

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

    from alfasim_sdk import constants

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
