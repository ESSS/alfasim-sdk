Solver Hooks
============

.. |alfasim| replace:: **ALFAsim**
.. |sdk| replace:: ``ALFAsim-SDK``

The present section describes all solver `Hooks` available on |alfasim| plugin infrastructure.
Solver `Hooks` are |alfasim|'s pre-defined functions that allows the plugin developer to add/update |alfasim|'s Solver.
As already informed in :ref:`Quick Start <quick-start-section>` section once created a plugin using ``template`` option
on |sdk|'s CLI a new file named ``plugin.c`` will be available to implement those `hooks`.

.. Note::
    There is no need to implement all solver `hooks` in the plugin. It depends on which functionality the developer wants
    to extend in the |alfasim| model.

In order to help the developer to decide which `hooks` to implement in the plugin, they are shown below according to their
classification which identifies what part of the solver workflow is related to.

Initial configuration and plugin internal data
----------------------------------------------

In the :ref:`User Interface Hooks <user_interface_hooks-section>` section is explained that the plugins are allowed to
customize the |alfasim|'s user interface extending it in order to get some input data from the user. Using the solver
:py:func:`HOOK_INITIALIZE<alfasim_sdk.hook_specs.initialize>` the developer can obtain the input data from user interface and use it to
initialize the plugin internal data.

As already mentioned, it is allowed that the plugins have internal data, in which can hold some important information that
will be used during the simulation, and also by other `hooks`.

.. warning::
    The plugin internal data will be hold by |alfasim|'s solver, however the plugin has full responsibility to allocate
    and deallocate its data from memory.

.. autofunction:: alfasim_sdk.hook_specs.initialize

As can be seen in the example above the function :cpp:func:`set_plugin_data` is used to tell the |alfasim|'s solver to
hold the plugin internal data.

.. note::
    Since |alfasim|'s solver uses multi-threads to perform all possible parallelizable calculation, it is important that
    the plugins provide internal data to each `thread` to avoid data access concurrency problems. As can be seen the
    ``HOOK_INITIALIZE`` example above, a ``for-loop`` is performed over the `threads` to set the plugin internal data.
    The ``ALFAsim-SDK`` API function :cpp:func:`get_number_of_threads` is used to do it properly. See
    :ref:`plugin_internal_data` section for more information.

.. autofunction:: alfasim_sdk.hook_specs.finalize

As can be seen in the example above the function :cpp:func:`get_plugin_data` is used to retrieved the plugin internal
data for each `thread` identified as ``thread_id``.

.. note::
    In the examples of usage of both :py:func:`HOOK_INITIALIZE<alfasim_sdk.hook_specs.initialize>` and :py:func:`HOOK_FINALIZE<alfasim_sdk.hook_specs.finalize>`
    there are many times where an error code is returned (``return errcode;`` or ``return OK;``). As can be seen, it is
    possible to return error codes from |sdk| API functions, however the developer can intercept this error code and
    handle it instead of returning it to the |alfasim|'s Solver.

Update plugin variables
-----------------------

The `hooks` described in this section are related to plugin secondary variables that were registered in the python config
file, as already explained in :ref:`pre_solver_customization` section. They are called `secondary variables` because they
are not obtained from |alfasim|'s Solver, these ones are called primary variables and examples of those variables are `pressure`,
`temperature`, `volume fractions` and `velocities`.

Using the following `hooks` the plugin is able to calculate/update those variables in three different moments of the
simulation step. Two of them are called in the `Hydrodynamic Solver` scope and the last one is called in the
`Tracers Solver` scope. Once the solver obtain results for primary variables, it updates all secondary variables in which
depend on primary variables. After that, :py:func:`HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES<alfasim_sdk.hook_specs.update_plugins_secondary_variables>`
is called, but if it is running the `first time step`
:py:func:`HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES_ON_FIRST_TIMESTEP<alfasim_sdk.hook_specs.update_plugins_secondary_variables_on_first_timestep>`
is called before. It is necessary because usually during the `first time step` some initialization tasks are needed. Then,
if the plugin needs to initialize with some value different from ``nan``, this hook is the place to do that.

.. note::
    Different from plugin internal data, the secondary variables registered by plugins are allocated, deallocated and
    held by |alfasim|'s Solver. It is necessary because the variables arrays are dependent on `network` with its
    discretization and on `hydrodynamic model`, which defines the fluid flow's `phases`, `fields` and `layers`.

.. autofunction:: alfasim_sdk.hook_specs.update_plugins_secondary_variables

.. autofunction:: alfasim_sdk.hook_specs.update_plugins_secondary_variables_on_first_timestep

The |alfasim|'s Solver is divided in two *Newton* solvers that will solve different group of equations. The first one is
the `hydrodynamic solver` which solves the Mass Conservation of fields, Momentum Conservation of layers and Energy Conservation
equations all together for all elements in the network. The second one is the `Tracer Solver` which solves the Mass Conservation
Equation for each added tracer. Since the tracers mass conservation is a transport equation it is solved after `hydrodynamic solver`
and using its results (such as `velocities`) as input data in the `Tracer Solver`. See the |alfasim|'s Technical Report
for more information.

To complete the group of `hooks` related to the plugins secondary variables there is the :py:func:`HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES_ON_TRACER_SOLVER<alfasim_sdk.hook_specs.update_plugins_secondary_variables_on_tracer_solver>`.
This `hook` is used to update plugin's variables that depends on Tracer's mass fractions and has to be updated in the
`Tracer Solver` scope.

.. autofunction:: alfasim_sdk.hook_specs.update_plugins_secondary_variables_on_tracer_solver

.. warning::
    It is important that the plugin developer take care of registered plugin's secondary variables, since their values
    will be set equal to ``nan`` at first place and it will not be changed by |alfasim|'s Solver at any time during
    the simulation.

Source Terms
------------

The `hooks` showed in this section can be considered as the most important. Since they allow the plugin to change the
conservation equations. It is made adding source terms in the residual function of mass, momentum and energy conservation
equations. Since the equations are in residual form, the negative values of source terms indicate that mass, momentum and
energy will be consumed. Otherwise, some amount of mass, momentum, and energy will be generated.

.. autofunction:: alfasim_sdk.hook_specs.calculate_mass_source_term

.. autofunction:: alfasim_sdk.hook_specs.calculate_momentum_source_term

.. autofunction:: alfasim_sdk.hook_specs.calculate_energy_source_term

.. autofunction:: alfasim_sdk.hook_specs.calculate_tracer_source_term

State Variables for additional phases
-------------------------------------

.. autofunction:: alfasim_sdk.hook_specs.initialize_state_variables_calculator

.. autofunction:: alfasim_sdk.hook_specs.calculate_state_variable

.. autofunction:: alfasim_sdk.hook_specs.calculate_phase_pair_state_variable

.. autofunction:: alfasim_sdk.hook_specs.finalize_state_variables_calculator

Additional solid phase
----------------------

.. autofunction:: alfasim_sdk.hook_specs.initialize_particle_diameter_of_solids_fields

.. autofunction:: alfasim_sdk.hook_specs.update_particle_diameter_of_solids_fields
