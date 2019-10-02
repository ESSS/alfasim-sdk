Solver Hooks
============

The present section describes all solver `Hooks` available to be implemented by a plugin.
`Hooks` are ALFAsim's pre-defined functions that allows the plugin developer to add/update models used by ALFAsim Solver.
As already informed in **XX Quick-Start XX** section once created a plugin using ``template`` option on CLI a new file
named `plugin.c` will be available to implement the new solver functionalities.
For that, pre-defined functions are available to change/update specific points of ALFAsim's solver workflow.


Plugin internal data
--------------------

.. autofunction:: alfasim_sdk.hook_specs.initialize

    For example:

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

Plugin variables
----------------

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


Solid phase
-----------

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
