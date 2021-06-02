.. _solver_hooks:

Solver Hooks
============

The present section describes all solver `Hooks` available on |alfasim| plugin infrastructure.
Solver `Hooks` are |alfasim|'s pre-defined functions that allows the plugin developer to modify/extend |alfasim|'s Solver.
As already informed in :ref:`Quick Start <quick-start-section>` section once created a plugin using ``template`` option
on |sdk|'s CLI a new file named ``plugin.c`` will be available to implement those `hooks`.

.. Note::
    There is no need to implement all solver `hooks` in the plugin. It depends on which functionality the developer wants
    to extend in the |alfasim| model.

In order to help the developer to decide which `hooks` to implement in the plugin, they are shown below according to their
classification which identifies what part of the solver workflow is related to.

To better visualize the interaction of the hooks with the solver, the :ref:`workflow_section` chapter has several graphs
illustrating the solver's walkthrough, showing where each hook will be called. The following graph is the same one
available at :ref:`main_overview` section from :ref:`workflow_section`. It illustrates where the :py:func:`HOOK_INITIALIZE<alfasim_sdk._internal.hook_specs.initialize>`
and the :py:func:`HOOK_FINALIZE<alfasim_sdk._internal.hook_specs.finalize>` will be called.

.. graphviz:: /_static/graphviz/main_flow.dot
    :align: center

.. contents::
    :depth: 3
    :local:

Initial configuration and plugin internal data
----------------------------------------------

In the :ref:`User Interface Hooks <user_interface_hooks-section>` section is explained that the plugins are allowed to
customize the |alfasim|'s user interface extending it in order to get some input data from the user. Using the solver
:py:func:`HOOK_INITIALIZE<alfasim_sdk._internal.hook_specs.initialize>` the developer can obtain the input data from user interface and use it to
initialize the plugin internal data.

As already mentioned, it is allowed that the plugins have internal data, in which can hold some important information that
will be used during the simulation, and also by other `hooks`.

.. warning::
    The plugin internal data will be hold by |alfasim|'s solver, however the plugin has full responsibility to allocate
    and deallocate its data from memory.

.. autofunction:: alfasim_sdk._internal.hook_specs.initialize

As can be seen in the example above the function :cpp:func:`set_plugin_data` is used to tell the |alfasim|'s solver to
hold the plugin internal data.

.. note::
    Since |alfasim|'s solver uses multi-threading to perform all possible parallelizable calculation, it is important that
    the plugins provide internal data to each `thread` to avoid data access concurrency problems. As can be seen the
    :py:func:`HOOK_INITIALIZE<alfasim_sdk._internal.hook_specs.initialize>` example above, a ``for-loop`` is performed over the `threads` to set the plugin internal data.
    The |sdk| API function :cpp:func:`get_number_of_threads` is used to do it properly. See
    :ref:`plugin_internal_data` section for more information.

.. autofunction:: alfasim_sdk._internal.hook_specs.finalize

As can be seen in the example above the function :cpp:func:`get_plugin_data` is used to retrieved the plugin internal
data for each `thread` identified as ``thread_id``.

.. note::
    In the examples of usage of both :py:func:`HOOK_INITIALIZE<alfasim_sdk._internal.hook_specs.initialize>` and :py:func:`HOOK_FINALIZE<alfasim_sdk._internal.hook_specs.finalize>`
    there are many times where an error code is returned (``return errcode;`` or ``return OK;``). As can be seen, it is
    possible to return error codes from |sdk| API functions, however the developer can intercept this error code and
    handle it instead of returning it to the |alfasim|'s Solver.

.. _update_secondary_variables:

Update plugin variables
-----------------------

The `hooks` described in this section are related to plugin secondary variables that were registered in the python config
file, as already explained in :ref:`solver_customization` section. They are called `secondary variables` because they
are not obtained from |alfasim|'s Solver, these ones are called primary variables and examples of those variables are `pressure`,
`temperature`, `volume fractions` and `velocities`.

Using the following `hooks` the plugin is able to calculate/update those variables in three different moments of the
simulation step. Two of them are called in the `Hydrodynamic Solver` scope and the last one is called in the
`Tracers Solver` scope as illustrated on :ref:`hyd_solver` and :ref:`tracer_solver` workflow section. Once the solver obtain results for primary variables, it updates all secondary variables in which
depend on primary variables. After that, :py:func:`HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES<alfasim_sdk._internal.hook_specs.update_plugins_secondary_variables>`
is called, but if it is running the `first time step`
:py:func:`HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES_ON_FIRST_TIMESTEP<alfasim_sdk._internal.hook_specs.update_plugins_secondary_variables_on_first_timestep>`
is called before. It is necessary because usually during the `first time step` some initialization tasks are needed. Then,
if the plugin needs to initialize with some value that is different from the initial ``nan`` value, this hook is the place to do that.

.. note::
    Different from plugin internal data, the secondary variables registered by plugins are allocated, deallocated and
    held by |alfasim|'s Solver. It is necessary because the variables arrays are dependent on `network` with its
    discretization and on `hydrodynamic model`, which defines the fluid flow's `phases`, `fields` and `layers`.

.. autofunction:: alfasim_sdk._internal.hook_specs.update_plugins_secondary_variables

.. autofunction:: alfasim_sdk._internal.hook_specs.update_plugins_secondary_variables_on_first_timestep

The |alfasim|'s Solver is divided in two *non-linear solvers* solvers that will solve different group of equations. The first one is
the `hydrodynamic solver` which solves the Mass Conservation of fields, Momentum Conservation of layers and Energy Conservation
equations all together for all elements in the network. The second one is the `Tracer Solver` which solves the Mass Conservation
Equation for each added tracer. Since the tracers mass conservation is a transport equation it is solved after `hydrodynamic solver`
and using its results (such as `velocities`) as input data in the `Tracer Solver`. See the |alfasim|'s Technical Report
for more information.

To complete the group of `hooks` related to the plugins secondary variables there is the :py:func:`HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES_ON_TRACER_SOLVER<alfasim_sdk._internal.hook_specs.update_plugins_secondary_variables_on_tracer_solver>`.
This `hook` is used to update plugin's variables that depends on Tracer's mass fractions and has to be updated in the
`Tracer Solver` scope.

.. autofunction:: alfasim_sdk._internal.hook_specs.update_plugins_secondary_variables_on_tracer_solver

.. warning::
    It is important that the plugin developer take care of registered plugin's secondary variables, since their values
    will be set equal to ``nan`` at first place and it will not be changed by |alfasim|'s Solver at any time during
    the simulation.

Source Terms
------------

The `hooks` showed in this section can be considered as the most important. Since they allow the plugin to change the
conservation equations. This is achieved by adding source terms in the residual function of mass, momentum and energy conservation
equations. Since the equations are in residual form, the negative values of source terms indicate that mass, momentum and
energy will be consumed. Otherwise, some amount of mass, momentum, and energy will be generated.

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_mass_source_term

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_momentum_source_term

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_energy_source_term

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_tracer_source_term

State Variables for additional phases
-------------------------------------

As can be seen in :ref:`multi-field-description` section the plugins can add new `fields`, `phases` and `layers`. Also,
it is possible to indicate if a phase will have its state variables calculated from plugin implementing the
:py:func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_get_phase_properties_calculated_from_plugin`.

.. autofunction:: alfasim_sdk._internal.hook_specs.initialize_state_variables_calculator

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_state_variable

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_phase_pair_state_variable

.. autofunction:: alfasim_sdk._internal.hook_specs.finalize_state_variables_calculator

Additional solid phase
----------------------

When a new phase is added to the hydrodynamic model using the :class:`~alfasim_sdk.AddPhase` type, it is possible
to set as a `solid phase`. In this case, the particle size of `fields` that are `solid phase` can be calculated by
implementing the following Solver `Hooks`. Otherwise, the particle size will be considered constant and equal to
:math:`1\times10^{-4}` meters.

.. autofunction:: alfasim_sdk._internal.hook_specs.initialize_particle_diameter_of_solids_fields

.. autofunction:: alfasim_sdk._internal.hook_specs.update_particle_diameter_of_solids_fields

Solids Model
------------

When a new solid phase is added to the hydrodynamic model using the :class:`~alfasim_sdk.AddPhase` type, it is
possible simulate a case with solid phase dispersed in fluids. In this kind of simulation a solids model can be
chosen by the user through |alfasim|'s GUI. Those models are able to calculate the slurry viscosity of the layer
and the slip velocity of the dispersed solid phase. Currently, there are only three solids model available, however
any plugin can add its own solids model. For that, it is necessary to implement the following hooks.

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_relative_slurry_viscosity

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_slip_velocity

Internal deposit layer
----------------------

When a new phase is added to the hydrodynamic model using the :class:`~alfasim_sdk.AddPhase` type, it is possible
to consider the deposition inside the pipeline walls. If so, calculate the thickness of the deposited layer on a given
phase through the usage of :py:func:`~alfasim_sdk._internal.hook_specs.update_internal_deposition_layer`. By default, the layer
thickness will be considered equal to zero meters.

.. autofunction:: alfasim_sdk._internal.hook_specs.update_internal_deposition_layer

Unit Cell Model (UCM) Friction Factor
-------------------------------------

When the Unit Cell Model is used in |alfasim| simulation any plugin can implement your own friction factor
correlation. For that, two hooks MUST be implemented, one for stratified flow and one for annular flow. Both of
them must be implemented because the |alfasim|'s Solver will call them depending on which flow pattern the fluid
flow is in the control volume.

.. note::
    It is important to know that the main input variables needed to compute the friction factor is available in
    the API function :cpp:func:`get_ucm_friction_factor_input_variable`. Note that, the variables listed in the
    documentation of the cited function are related to one control volume, in which the Unit Cell Model is applied.

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_ucm_friction_factor_stratified

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_ucm_friction_factor_annular

.. note::
    Another important API function for UCM is :cpp:func:`get_ucm_fluid_geometrical_properties`. This function computes
    the geometrical properties properly in each previous presented `hooks` depending on the flow pattern.

Liquid-Liquid Mechanistic Model
-------------------------------

|alfasim|'s resulting multiphase model is a one-dimensional system of nonlinear equations, which is a result of some
averaging steps that transforms a local instantaneous three-dimensional model into a one-dimensional multiphase (and
multi-field) model. The derived variables that form the nonlinear differential equations represent average values at
a given point in time and space. It is clear that in this averaging process there are important phenomena that will
non longer be naturally captured from the equations and therefore one of the strategies is to incorporate all the
physics that have been lost in the averaging process in the shear stress term in order to accurately represent the
physical behavior. Hence the shear stress is one of the most important parameters for characterizing the quality of a
one-dimensional multiphase model.

The main goal of the mechanistic model is to calculate the friction pressure drop as well as the steady-state volume
fractions and velocities.  |alfasim| supports two-phase (gas-liquid) and three-phase (gas-oil-water) flows, but for
three-phase flow it is required a plugin that handles the oil-water system.

.. note ::
    Note that the two phase (Gas-Liquid) system of Mechanistic Model can be used for both two and three-phase flows,
    in which is done in case of a liquid-liquid system is not available via plugin.

In the gas-liquid system the liquid phase is considered as a sum of all liquid phases, and the model take into account
only the interaction behavior between these two phases (Gas and Liquid). Of course, this kind of approach brings some
limitations, since the behavior of the oil and water in the liquid phase is considered nearly homogeneous (mixture).
On the other hand, if the liquid-liquid system considers the interaction between oil and water, it introduces a better
modeling and representation of the tree-phase system. In fact, considering the interaction between the oil and water
phases, behaviors such as emulsion formation (oil dominated or water dominated) and stratified flow can be taken into
account together with the gas-liquid system.

The |alfasim|'s Mechanistic Model of three-phase system is divided into two steps, one for gas-liquid system and
one for liquid-liquid system in which the complete representation uses an incremental approach. The two phase systems
(Gas-Liquid and Liquid-Liquid) model different behaviors and are coupled in the three-phase system algorithm. First the
Mechanistic Model for gas-liquid system is solved, considering a single liquid phase (Oil and Water mixture), after
that the Mechanistic Model for liquid-liquid system is solved, considering independent oil and water phases.  Finally,
the properties of liquid phase are updated taking into account the solution of Mechanistic model for liquid-liquid system.

To make possible the liquid-liquid system modeling via plugin, four Hooks are available in the |sdk|, three of them to
estimate/compute properties that depends on Oil-Water interaction (Flow Pattern, Viscosity and surface tension) and one
to properly compute the shear force of each liquid phase and between them. Other associated variables are required in
each Liquid-Liquid system plugin hooks. In the sequence, they are presented

.. warning::
    The hooks described in this section must be implemented all of them or none of them. If just part of four hooks
    are implemented, the |alfasim| will show an error of configuration.

.. note ::
    Note that the all of the hooks related to the liquid-liquid system of Mechanistic Model can use same emulsion
    viscosity model used internally by |alfasim|. It is made by helper function :cpp:func:`get_relative_emulsion_viscosity`.
    Since the liquid-liquid system is an emulsion, this helper function is important to keep the consistency between
    |alfasim| and its plugins that implement the following hooks.


.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_liq_liq_flow_pattern

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_liquid_effective_viscosity

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_gas_liq_surface_tension

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_liq_liq_shear_force_per_volume

Emulsion Model
--------------

When a simulation case uses a three-phase flow model, |alfasim| allows to select an emulsion model that will update
the layer viscosity related to the emulsion. In that case, a relative emulsion viscosity correlation is used to
calculate it. In order to allow the emulsion model customization, the plugin structure has a hook that accept
the implementation of a relative emulsion viscosity correlation.

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_relative_emulsion_viscosity

.. warning::
    The emulsion viscosity hook must be implemented as a simple correlation, in which all data is available as
    parameters (Dispersed and continuous viscosities, for example). For this hook only the API functions
    :cpp:func:`get_field_id`, :cpp:func:`get_phase_id` and :cpp:func:`get_layer_id` are available, any other API
    function will return an error code different from ``OK`` (:cpp:enum:`error_code` values) if called from this hook.


User Defined Tracers
--------------------

The `hooks` described in this section must be implemented when at least one `user defined tracer` is added via
:py:func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_get_user_defined_tracers_from_plugin` `hook`.

.. warning::
    |tracer_warn|

These `hooks` can modify the tracer transport equation from the initialization to configuration of boundary conditions.
The plugin developer has complete freedom to change the equations, however it is important to be aware that it can be
made manipulating the transport equation terms inside the `hooks`. For that, it is important to read the `Tracers`
Chapter at |alfasim|'s Technical Manual.

.. autofunction:: alfasim_sdk._internal.hook_specs.initialize_mass_fraction_of_tracer

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_mass_fraction_of_tracer_in_phase

.. autofunction:: alfasim_sdk._internal.hook_specs.calculate_mass_fraction_of_tracer_in_field

.. autofunction:: alfasim_sdk._internal.hook_specs.set_prescribed_boundary_condition_of_mass_fraction_of_tracer

.. autofunction:: alfasim_sdk._internal.hook_specs.update_boundary_condition_of_mass_fraction_of_tracer
