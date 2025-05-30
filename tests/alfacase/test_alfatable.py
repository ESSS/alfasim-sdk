from textwrap import dedent

import numpy as np

from alfasim_sdk import (
    PvtModelPtTableParametersDescription,
    convert_alfacase_to_description,
    generate_alfacase_file,
    generate_alfatable_file,
)


def test_alfatable_has_flow_style_for_numpy_array(tmp_path):
    description = PvtModelPtTableParametersDescription(
        pressure_values=np.array([1, 2, 3]),
        temperature_values=np.array([4, 5, 6]),
        table_variables=[
            np.array([42, 42, 42]),
            np.array([20, 20, 20]),
            np.array([30, 30, 30]),
        ],
        variable_names=["a", "b", "c"],
    )
    generate_alfatable_file(tmp_path / "a.alfacase", "foo", description)
    assert (tmp_path / "a.foo.alfatable").read_text() == dedent(
        """\
        pressure_values: [1, 2, 3]
        temperature_values: [4, 5, 6]
        table_variables:
        - [42, 42, 42]
        - [20, 20, 20]
        - [30, 30, 30]
        variable_names:
        - a
        - b
        - c
        pressure_std:
          value: 1.0
          unit: bar
        temperature_std:
          value: 15.0
          unit: degC
        gas_density_std:
          value: 1.0
          unit: kg/m3
        oil_density_std:
          value: 800.0
          unit: kg/m3
        water_density_std:
          value: 1000.0
          unit: kg/m3
        gas_oil_ratio:
          value: 0.0
          unit: sm3/sm3
        gas_liquid_ratio:
          value: 0.0
          unit: sm3/sm3
        water_cut:
          value: 0.0
          unit: '-'
        total_water_fraction:
          value: 0.0
          unit: '-'
        number_of_phases: 2
        warn_when_outside: True
    """
    )


# TODO: ASIM-4980: test the export of a PH table alfacase file
def test_alfacase_file_export(tmp_path):
    """
    Check that GenerateAlfacaseFile creates a alfatable file with the content from PvtModelsDescription.table_parameters
    When exporting this alfatable should be placed on PvtModelDescription.tables
    """

    alfacase_file = tmp_path / "mycase.alfacase"
    alfatable_file = tmp_path / "mycase.fluid_a_1.alfatable"

    pvt_model_table_parameter = {
        "FLUID-A 1": PvtModelPtTableParametersDescription.create_constant()
    }
    from alfasim_sdk._internal.alfacase import case_description

    case_description = case_description.CaseDescription(
        pvt_models=case_description.PvtModelsDescription(
            pt_table_parameters=pvt_model_table_parameter
        )
    )

    generate_alfacase_file(case_description, alfacase_file)
    assert alfacase_file.is_file()
    assert alfatable_file.is_file()
    # Load
    case = convert_alfacase_to_description(alfacase_file)
    assert case.pvt_models.tables == {"FLUID-A 1": alfatable_file}


def test_alfacase_file_load(tmp_path):
    from alfasim_sdk._internal.alfacase import case_description

    alfacase_file = tmp_path / "mycase.alfacase"
    pvt_table_parameters_description = (
        case_description.PvtModelPtTableParametersDescription.create_constant()
    )
    alfatable_file = generate_alfatable_file(
        alfacase_file=alfacase_file,
        alfatable_filename="FLUID-A 1",
        description=pvt_table_parameters_description,
    )
    assert alfatable_file.is_file()

    from alfasim_sdk import load_pvt_model_table_parameters_description_from_alfatable

    assert (
        load_pvt_model_table_parameters_description_from_alfatable(alfatable_file)
        == pvt_table_parameters_description
    )
