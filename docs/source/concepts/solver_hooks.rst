Solver Hooks
============

The present section describes all solver `Hooks` available on ALFAsim plugin infrastructure.
Solver `Hooks` are ALFAsim's pre-defined functions that allows the plugin developer to add/update ALFAsim Solver.
As already informed in :ref:`Quick Start <quick-start-section>` section once created a plugin using ``template`` option
on ALFAsim-SDK's CLI a new file named ``plugin.c`` will be available to implement those `hooks`.

.. Note::
    There is no need to implement all solver `hooks` in the plugin. It depends on which functionality the developer wants
    to extend in the ALFAsim model.

In order to help the developer to decide which `hooks` to implement in the plugin, they are shown below according to their
classification which identifies what part of the solver workflow is related to.

Initial configuration and plugin internal data
----------------------------------------------

In the :ref:`User Interface Hooks <user_interface_hooks-section>` section is explained that the plugins are allowed to
customize the ALFAsim's user interface extending it in order to get some input data from the user. Using the solver `hook`
:py:func:`alfasim_sdk.hook_specs.initialize` the developer can obtain the input data from user interface and use it to
initialize the plugin internal data.

As already mentioned, it is allowed that the plugins have internal data, in which can hold some important information that
will be used during the simulation, and also by other `hooks`.

.. warning::
    The plugin internal data will be hold by ALFAsim's solver, however the plugin has full responsibility to allocate
    and deallocate its data from memory.

.. autofunction:: alfasim_sdk.hook_specs.initialize

    example:

    .. code-block::

        initialize()
        {

        }

.. autofunction:: alfasim_sdk.hook_specs.finalize

    For example:

    .. code-block::

        finalize()
        {

        }

Source Terms
------------

.. autofunction:: alfasim_sdk.hook_specs.calculate_mass_source_term

    For example:

    .. code-block::

        calculate_mass_source_term(ctx, mass_source, n_fields, n_control_volumes)
        {

        }

.. autofunction:: alfasim_sdk.hook_specs.calculate_momentum_source_term

    For example:

    .. code-block::

        calculate_momentum_source_term(ctx, momentum_source, n_layers, n_faces)
        {

        }

.. autofunction:: alfasim_sdk.hook_specs.calculate_energy_source_term

    For example:

    .. code-block::

        calculate_energy_source_term(ctx, energy_source, n_layers, n_control_volumes)
        {

        }

.. autofunction:: alfasim_sdk.hook_specs.calculate_tracer_source_term

    For example:

    .. code-block::

        calculate_tracer_source_term(ctx, phi_source, n_tracers, n_control_volumes)
        {

        }

Update plugin variables
-----------------------

.. autofunction:: alfasim_sdk.hook_specs.update_plugins_secondary_variables_on_first_timestep

    For example:

    .. code-block::

        update_plugins_secondary_variables_on_first_timestep(ctx)
        {

        }

.. autofunction:: alfasim_sdk.hook_specs.update_plugins_secondary_variables

    For example:

    .. code-block::

        update_plugins_secondary_variables(ctx)
        {

        }

.. autofunction:: alfasim_sdk.hook_specs.update_plugins_secondary_variables_on_tracer_solver

    For example:

    .. code-block::

        update_plugins_secondary_variables_on_tracer_solver(ctx)
        {

        }

State Variables for additional phases
-------------------------------------

.. autofunction:: alfasim_sdk.hook_specs.initialize_state_variables_calculator

    For example:

    .. code-block::

        initialize_state_variables_calculator(ctx, P, T, T_mix, n_control_volumes, n_layers)
        {

        }

.. autofunction:: alfasim_sdk.hook_specs.calculate_state_variable

    For example:

    .. code-block::

        calculate_state_variable(ctx, P, T, n_control_volumes, phase_id, property_id, output)
        {

        }

.. autofunction:: alfasim_sdk.hook_specs.calculate_phase_pair_state_variable

    For example:

    .. code-block::

        calculate_phase_pair_state_variable(ctx, P, T, T_mix, n_control_volumes, phase1_id, phase2_id, property_id, output)
        {

        }

.. autofunction:: alfasim_sdk.hook_specs.finalize_state_variables_calculator

    For example:

    .. code-block::

        finalize_state_variables_calculator(ctx)
        {

        }


Additional solid phase
----------------------

.. autofunction:: alfasim_sdk.hook_specs.initialize_particle_diameter_of_solids_fields

    For example:

    .. code-block::

        initialize_particle_diameter_of_solids_fields(ctx, particle_diameter, n_control_volumes, solid_field_id)
        {

        }

.. autofunction:: alfasim_sdk.hook_specs.update_particle_diameter_of_solids_fields

    For example:

    .. code-block::

        update_particle_diameter_of_solids_fields(ctx, particle_diameter, n_control_volumes, solid_field_id)
        {

        }
