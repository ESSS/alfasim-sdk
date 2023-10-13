=======
History
=======

0.18.0 (2023-10-13)
===================

* Added support for Python 3.10.
* Dropped support for EOL Python 3.6 and 3.7.
* Remove pins for ``strictyaml`` and no longer require ``ruamel.yaml``.


0.17.0 (2023-09-01)
===================

* Disable internal hdf file locks.

* Added ``esp_thermal_efficiency_model`` attribute to ``PumpEquipmentDescription``.

* Added ``esp_manufacturer`` and ``esp_model`` attributes to ``PumpEquipmentDescription``.

* Removed ``user_defined_esp_table`` and ``esp_parameters`` from ``PumpEquipmentDescription``.

* ``pyinvoke`` is now used to manage plugins tasks.


0.16.3 (2023-10-11)
===================

* Loose pinned requirements for ``barril``.

0.16.0 (2023-02-09)
===================

* Added support to export and import configuration data from plugins.

* Added a fixture ``alfasim_runner`` (add to pytest relevant configuration ``alfasim_sdk.testing.fixtures`` to use it) to allow plugin authors to run their plugin against an installed version of ALFAsim in a test environment.

* Added a helper to read ALFAsim simulation results (``alfasim_sdk.result_reader.reader.Results``).

* Added ``heads```, ``efficiencies``, and ``powers`` attributes to ``TablePumpDescription``.

* Added ``esp_viscosity_model`` attribute to ``PumpEquipmentDescription``.

* Added ``user_defined_esp_table`` and ``esp_parameters`` attributes to ``PumpEquipmentDescription``. Now, an ESP can be created as ``eps_parameters`` = [``user_defined`` or ``catalog``].  When it's created as ``user_defined``, the pump table is read from a ``user_defined_esp_table``. Otherwise, is read from a ``esp_table``.


0.15.0 (2022-11-29)
===================

* **Breaking Change**: Available units for category ``angle per time`` have been restricted to ``Hz``, ``rpm`` and ``rad/s`` only;


0.14.3 (2023-04-26)
===================

* Hot fix release, loosing pin requirements for `barril`.

0.14.2 (2023-04-26)
===================

* Problem during deploy.

0.14.1 (2023-04-26)
===================

* Problem during deploy.

0.14.0 (2022-07-19)
===================

* Add Electric Submersible Pump (ESP) input for ``PumpEquipmentDescription``. The new inputs are:

  - ``esp_table``: table created through ``TablePumpDescription``
  - ``esp_speed_input_type``: type of speed input ``Constant`` or ``Transient``
  - ``esp_speed``: constant speed value
  - ``esp_speed_curve``: curve defining time vs speed values
  - ``esp_number_of_stages``: number of stages for ESP
  - ``esp_reference_density``: rated density used to defined the ``esp_table``

* **Breaking Change**: Change in ``PhysicsDescription``: split emulsion model into relative viscosity, droplet size, and inversion point models and a flag to activate the emulsion models.

* Examples on how to update previous .alfacase files with emulsion model:

  - Relative viscosity model:

    * Before::

        emulsion_model: taylor1932

    * After::

        emulsion_model_enabled: True
        emulsion_relative_viscosity_model: taylor1932

  - Droplet size model:

    - Before::

        emulsion_model: hinze1955

    - After::

        emulsion_model_enabled: True
        emulsion_droplet_size_model: hinze1955

  - Inversion point model:

    - Before::

        emulsion_model: brinkman1952_and_yeh1964

    - After::

        emulsion_model_enabled: True
        emulsion_inversion_point_model: brinkman1952_and_yeh1964

* **Breaking Change**: change signature of hook ``calculate_relative_emulsion_viscosity``. This hook is also receiving the fluid temperature and a flag indicating whether the dispersion is water in oil or oil in water;

* Add new emulsion relative viscosity models:

  - ``pal_rhodes1989``;
  - ``ronningsen1995``;
  - ``volumetric_weight``;
  - ``woelflin_1942``;
  - ``barnea_mizrahi1976``;
  - ``table_based``;

* Add emulsion constant inversion point model;

* Add emulsion relative viscosity tuning factor;

* Fix ``automatic_profile_frequency`` and ``automatic_trend_frequency`` parameters being ignored in ``convert_alfacase_to_description``;


0.13.0 (2022-04-19)
===================

* Add black-oil properties to PVT Correlations case description ``PvtModelCorrelationDescription``

* **Breaking Change**: Change in ``PvtModelsDescription`` renamed experimental compositional models holder property from ``compositions`` to ``compositional``;

* Example on how to update previous .alfacase files with compositional PVT models:

  - Before::

      pvt_models:
        compositions:
          Compositional model 1:
            equation_of_state_type: pvt_compositional_peng_robinson
            ...  # Other properties

  - After::

      pvt_models:
        compositional:
          Compositional model 1:
            equation_of_state_type: pvt_compositional_peng_robinson
            ...  # Other properties

* **Breaking Change**:  Change signature of hook ``update_internal_deposition_layer``. Now, instead of the deposition thickness, it is returned the phase index of phase being deposited and the thickness variation rate.
* **Breaking Change**:  Change signature of hook ``calculate_relative_emulsion_viscosity`` and function ``get_relative_emulsion_viscosity``. Indices of continuous and dispersed fields were removed.
* Add ``ControllerTrendDescription``, a new type of trend available in ``TrendsOutputDescription``.
* Add method ``get_deposition_thickness`` to retrieve the current thickness of a phase deposited on pipe wall.
* Add ``flow_pattern_model`` and ``regime_capturing_mesh_treshold`` attributes to ``PipeDescription``.
* Add Combined PVT model description classes (``PvtModelCombinedDescription`` and ``CombinedFluidDescription``).


0.12.0 (2022-01-18)
===================

* **Breaking Change**: Change in ``AnnulusDescription`` to support different types of annulus equipment. Now ``AnnulusDescription`` has an attribute ``AnnulusEquipmentDescription``, which holds a dict that can contain multiple different equipment types, for which the current available options are:

  - ``LeakEquipmentDescription``;
  - ``GasLiftValveEquipmentDescription``;

* Example on how to update previous .alfacase files with annulus equipment:

  - Before::

      annulus:
        gas_lift_valve_equipment:
          Gas Lift Valve (Well 1 > Annulus) 1:
            position:
              value: 100.0
              unit: m
            ...  # Other properties

  - After::

      annulus:
        equipment:
          gas_lift_valves:
            Gas Lift Valve (Well 1 > Annulus) 1:
              position:
                value: 100.0
                unit: m
              ...  # Other properties

* Removed *force per square velocity* unit definition, it is present in the new barril version.


0.11.0 (2021-11-30)
===================

* **Breaking Change**: Change ``TrendOutputDescription`` to support different trends types. Now trends in ``CaseOutputDescription`` are an object of ``TrendsOutputDescription`` that contains a list for each trend type. The available trend types are:

  - ``PositionalPipeTrendDescription``;
  - ``GlobalTrendDescription``;
  - ``OverallPipeTrendDescription``;
  - ``EquipmentTrendDescription``;
  - ``SeparatorTrendDescription``;

* Add new API functions related to Multi-Field Description info: ``get_number_of_fields``, ``get_number_of_phases``, ``get_number_of_layers`` and ``get_number_of_phase_pairs``.
* Add new API functions related to Multi-Field Description phase and field ids: ``get_phase_id_of_fields``, ``get_field_ids_in_layer`` and ``get_phase_pair_id``.
* Add LeakEquipment equipment.
* Add SurgeVolumeOptionsDescription (optional, used by PositionalPipeTrendDescription to hold some input for surge volume curves calculation).


0.10.1 (2021-06-30)
===================

* Temporarily pin ``strictyaml`` dependency due to conflicts.


0.10.0 (2021-06-29)
===================

* Add a new category ``gas standard volume`` from quantity ``standard volume``.
* Add transient input for:
    - ``MassSourceNode`` and ``MassSourceEquipment``: ``temperature``, ``volumetric_flow_rates_std``, ``mass_flow_rates``, ``total_mass_flow_rate``, ``water_cut``, ``gas_oil_ratio``;
    - ``PressureNode`` and ``ReservoirInflowEquipment``: ``pressure``, ``temperature``, ``mass_fractions``, ``volume_fractions``, ``gas_liquid_ratio``, ``gas_oil_ratio``, ``water_cut``;
    - ``LinearIPR``: ``well_index``;
    - ``HeatSourceEquipment``: ``power``;
* Add two new hooks to calculate solids model (for slurry viscosity and slip velocity).
* **Breaking Change**: Change ``OpeningCurveDescription`` (``opening_curve`` attribute) for ``Curve`` from barril.
* **Breaking Change**: Change signature of ``HOOK_INITIALIZE_STATE_VARIABLES_CALCULATOR``.
* **Breaking Change**: Change signature of ``HOOK_CALCULATE_RELATIVE_EMULSION_VISCOSITY``.
* Add new API function ``get_relative_emulsion_viscosity`` which is a helper function that can be used in the Hooks of Liquid-Liquid Mechanistic Model.


0.9.0 (2021-05-04)
==================

* Add new CLI command called ``update``. It updates files automatically generated by alfasim-sdk.
* Add gas and liquid separation efficiency to ``Separator`` model.
* **Breaking Change**: Replaced radius from ``Separator`` geometry definition by diameter.
* Add new hook to calculate relative emulsion viscosity and also add the possibility of choosing it in the ``PhysicsDescription``.


0.8.0 (2021-04-12)
==================

* Add context support on ``alfasim_configure_fields``, ``alfasim_configure_layers`` and ``alfasim_configure_phases``.
* Change category for ``volumetric_flow_rates_std` from ``volume flow rate`` to ``standard volume per time``.
* Rename ``convert_alfacase_to_case`` to ``convert_alfacase_to_description``.
* Add new category: ``gas standard volume per time``, with same units as ``standard volume per time``.
* Drop ``B_parameter`` as Lee-Chien method for surface tension is not supported anymore.
* Add option to set the category for ``SecondaryVariable`` object
* Add ``WallsWithoutEnvironment`` to ``PipeEnvironmentHeatTransferCoefficientModelType`` enum.
* Add properties that control automatic definition of restart autosave, trend and profile saving frequency to ``TimeOptionsDescription`` and ``CaseOutputDescription``.
* Update documentation of ``get_simulation_array``, the wetted perimeters of layers are available.
* Add new API functions related Liquid-Liquid Mechanistic Model Hooks.
* Add four new hooks to calculate the Liquid-Liquid Mechanistic Model.

0.7.0 (2020-11-20)
==================

* Add support for alfacase.
* Released with ALFAsim 1.8.0.


0.6.1 (2020-10-30)
==================

* Internal release only.


0.6.0 (2020-10-29)
=================

* Invalid release due to packaging error.

0.5.0
======

* Remove api functions `get_wall_layer_id` and `set_wall_layer_property`.
* Add `thickness`, `density`, `heat_capacity`, `thermal_conductivity` parameters on `update_internal_deposition_layer`

0.4.0
======

* Add new API functions related unit cell model friction factor hooks.

* Add two new hooks to calculate the unit cell model friction factor for stratified and annular flows.

0.3.0
======

* Adopt terminology gas-oil-water

* Add a new hook to evaluate the thickness of the deposited layer at the inside of the pipeline walls and it accounts for the diameter reduction.

* Rename HydrodynamicModelType items from snake_case to CamelCase, a backward compatibility option is kept.

0.2.0
======

* Add "required-alfasim-sdk" key on plugin.yaml to identify the required version of alfasim-sdk.

0.1.0
======

* First release.
