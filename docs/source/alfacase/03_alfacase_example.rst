.. _alfacase-example:

ALFAcase Example
================

In this section, we will create a project from scratch with a simple network and insert it on the ALFAsim application.


The root level of our :program:`ALFAcase` file is always a :class:`CaseDescription` which has the following attributes:
For the full reference check the :ref:`alfacase-reference-section`

.. code-block:: yaml

    name: string    # optional
    physics: physics_description_schema⠀
    time_options: time_options_description_schema⠀
    numerical_options: numerical_options_description_schema⠀
    ipr_models: ipr_models_description_schema⠀
    pvt_models: pvt_models_description_schema⠀
    tracers: tracers_description_schema⠀
    outputs: case_output_description_schema⠀

    ....

We are going to create a simple case with a PVT model, two nodes and one pipe displaying their output.
Each section can be inspect over the :ref:`alfacase-reference-section`

.. code-block:: yaml

    name: basic_case
    physics:
    correlations_package: correlation_package_alfasim
    hydrodynamic_model: hydrodynamic_model_4_fields

    pvt_models:
    default_model: 'Pvt1'
    tables:
      'Pvt1': my_pvt_file.tab

    numerical_options:
    tolerance: 0.0001

    time_options:
    minimum_timestep:
      value: 0.0001
      unit: s
    maximum_timestep:
      value: 0.5
      unit: s
    final_time:
      value: 1.0
      unit: s

    outputs:
    trends:
      - curve_names:
          - oil mass flow rate
        element_name: pipe
        position:
          value: 100.0
          unit: m
        location: main
    trend_frequency:
      value: 0.1
      unit: s
    profiles:
      - curve_names:
          - pressure
        element_name: pipe
        location: main
    profile_frequency:
      value: 0.1
      unit: s

    pipes:
    - name: pipe
      source: Inlet
      target: Outlet
      profile:
        length_and_elevation:
          length:
            values: [ 0.0, 15.0, 30.0, 30.0, 15.0 ]
            unit: m
          elevation:
            values: [ 0.0, 15.0, 30.0, 30.0, 15.0 ]
            unit: m
      segments:
        start_positions:
          values: [ 0.0 ]
          unit: m
        diameters:
          values: [ 0.1 ]
          unit: m
        roughnesses:
          values: [ 5e-05 ]
          unit: m

    nodes:
    - name: Inlet
      node_type: mass_source_boundary
      mass_source_properties:
        mass_flow_rates:
          gas:
            value: 0.0
            unit: kg/s
          oil:
            value: 0.0
            unit: kg/s
    - name: Outlet
      node_type: pressure_boundary
      pressure_properties:
        volume_fractions:
          gas:
            value: 1.0
            unit: '-'
          oil:
            value: 0.0
            unit: '-'
        pressure:
          value: 50.0
          unit: bar
