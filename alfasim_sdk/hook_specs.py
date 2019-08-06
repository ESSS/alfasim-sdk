from hookman.hooks import HookSpecs


def initialize(ctx: "void*") -> "int":
    """
    This Hook can be used to initialize plugin internal data and also some
    simulator configurations available via API.

    :param ctx: ALFAsim's plugins context

    :returns: Return OK if successful or anything different if failed
    """


def finalize(ctx: "void*") -> "int":
    """
    This Hook must be used to delete all plugin internal data. Otherwise, a memory
    leak could occur in your plugin.

    :param ctx: ALFAsim's plugins context

    :returns: Return OK if successful or anything different if failed
    """


def compute_mass_source_term(
    ctx: "void*", mass_source: "void*", n_fields: "int", n_control_volumes: "int"
) -> "int":
    """
    Internal simulator hook to compute source terms of mass equation.
    This is called after all residual functions are evaluated.

    :param ctx: ALFAsim's plugins context
    :param mass_source: Source term of mass equation
    :param n_fields: Number of fields
    :param n_control_volumes: Number of control volumes

    :returns: Return OK if successful or anything different if failed
    """


def compute_momentum_source_term(
    ctx: "void*", momentum_source: "void*", n_layers: "int", n_faces: "int"
) -> "int":
    """
    Internal simulator hook to compute source terms of momentum equation.
    This is called after all residual functions are evaluated.

    :param ctx: ALFAsim's plugins context
    :param momentum_source: Source term of momentum equation
    :param n_layers: Number of layers
    :param n_faces: Number of faces (equal to n_control_volumes minus 1)

    :returns: Return OK if successful or anything different if failed
    """


def compute_energy_source_term(
    ctx: "void*", energy_source: "void*", n_layers: "int", n_control_volumes: "int"
) -> "int":
    """
    Internal simulator hook to compute source terms of energy equation
    This is called after all residual functions are evaluated.

    :param ctx: ALFAsim's plugins context
    :param energy_source: Source term of energy equation
    :param n_layers: Number of layers
    :param n_control_volumes: Number of control volumes

    :returns: Return OK if successful or anything different if failed
    """


def compute_tracer_source_term(
    ctx: "void*", phi_source: "void*", n_tracers: "int", n_control_volumes: "int"
) -> "int":
    """
    Internal simulator hook to compute source terms of tracer transport equation.
    This is called after all residual functions are evaluated.

    :param ctx: ALFAsim's plugins context
    :param phi_source: Source term of tracers mass equation
    :param n_tracers: Number of tracers
    :param n_control_volumes: Number of control volumes

    :returns: Return OK if successful or anything different if failed
    """


def calculate_slip_velocity(
    ctx: "void*",
    U_fields: "void*",
    alpha_f: "void*",
    d_disp_fields: "void*",
    P: "void*",
    rho_f: "void*",
    mu_f: "void*",
    sin_theta_f: "void*",
    delta_x_f: "void*",
) -> "int":
    """
    Internal simulator hook to calculate slip velocity between fluids
    and solid phase.

    :param ctx: ALFAsim's plugins context
    :param U_fields: Field velocities,
    :param alpha_f: Field Volume fractions on faces,
    :param d_disp_fields: Diameter of dispersed fields,
    :param P: Pressure,
    :param rho_f: Field densities on faces,
    :param mu_f: Field viscosities on faces,
    :param sin_theta_f: Sin of Theta on faces in which Theta is the angle between the Pipe and the Y-Axis,
    :param delta_x_f: The control volume lenght related to the faces,

    :returns: Return OK if successful or anything different if failed

    It is expected to be changed the U_fields of solid phase, whose index will be available via API.
    """


def calculate_slurry_viscosity(
    ctx: "void*", alpha_f: "void*", mu_f: "void*", mu_f_layer: "void*"
) -> "int":
    """
    Internal simulator hook to calculate slurry viscosity of layer(s).

    :param ctx: ALFAsim's plugins context
    :param alpha_f: Fields Volume fractions on faces,
    :param mu_f: Field viscosities on faces,
    :param mu_f_layer: Layer Viscosities on faces,

    :returns: Return OK if successful or anything different if failed

    It is expected to be changed the mu_f_layer of liquid layer(continuous liquid and dispersed solid),
    whose index will be available via API.
    """


def update_plugins_secondary_variables(ctx: "void*") -> "int":
    """
    Internal simulator hook to update plugin's secondary variables.
    This is called as the last step on ALFAsim's update internal variables workflow.

    :param ctx:

    :returns: Return OK if successful or anything different if failed
    """


def update_plugins_secondary_variables_extra(ctx: "void*") -> "int":
    """
    Internal simulator hook to update plugin's secondary variables in the ExtraVarSolver scope.
    ExtraVarSolver is used to solve the tracer transport equation.
    This is called as the last step on ALFAsim's ExtraVarSolver update variables workflow.

    :param ctx:

    :returns: Return OK if successful or anything different if failed
    """


def update_plugins_secondary_variables_on_first_timestep(ctx: "void*") -> "int":
    """
    Internal simulator hook to update plugin's secondary variables on the first timestep.
    This is called as the first step on ALFAsim's update internal variables workflow.
    This method is specially important when you have a plugin which the secondary variables depend
    on `old` values. In the first timestep, there is no `old` values, so you may use this hook
    to initialize your variables contents.

    :param ctx:

    :returns: Return OK if successful or anything different if failed
    """


def friction_factor(v1: "int", v2: "int") -> "int":
    """
    Docs for Friction Factor
    """


def env_temperature(v3: "float", v4: "float") -> "float":
    """
    Docs for Environment Temperature
    """


def calculate_entrained_liquid_fraction(
    U_S: "const double[2]",
    rho: "const double[2]",
    mu: "const double[2]",
    sigma: "double",
    D: "double",
    theta: "double",
) -> "double":
    """
    Hook for droplet entrainment model when in annular flow (in unit cell model)

    :param U_S: Gas and liquid superficial velocities [m/s]
    :param rho: Phase densities [kg/m3]
    :param mu: Phase viscosities [Pa.s]
    :param sigma: Surface tension [N.m]
    :param D: Pipe diameter [m]
    :param theta: Pipe inclination [rad]

    :returns:
        Entrainment fraction, defined as the ratio between the droplet mass flow rate and the total liquid
        mass flow rate (dimensionless)
    """


def initialize_state_variables_calculator(
    ctx: "void*",
    P: "void*",
    T: "void*",
    T_mix: "void*",
    n_control_volumes: "int",
    n_layers: "int",
) -> "int":
    """
    Hook for the state variables calculator initialization.
    To define a function that'll calculate the state variables for a given phase on ALFAsim,
    two main steps must be performed:

    1) In the plugin python configuration file, define the
       alfasim_get_phase_properties_calculated_from_plugin function to set which phases
       the current plugin is able to calculate state variables.

    2) The plugin must, then, implement three hooks:
    - HOOK_INITIALIZE_STATE_VARIABLE_CALCULATOR
    - HOOK_CALCULATE_STATE_VARIABLE
    - HOOK_CALCULATE_PHASE_PAIR_STATE_VARIABLE
    - HOOK_FINALIZE_STATE_VARIABLE_CALCULATOR

    The first and last hooks are called immediately before and after the state variables are
    calculated, respectively.
    At this point, it is possible to pre-calculate and cache any relevant information.
    Then, for each state variable of the phases in the python configuration file, the hook
    HOOK_CALCULATE_STATE_VARIABLE is called.
    """


def calculate_state_variable(
    ctx: "void*",
    P: "void*",
    T: "void*",
    n_control_volumes: "int",
    phase_id: "int",
    property_id: "int",
    output: "void*",
) -> "int":
    """
    Hook to calculate the state variable given by the `property_id` (See alfasim_sdk_api common
    headers to retrieve the available property ids), for the phase `phase_id` (Note that the phase
    id is the same as the one retrieved from the `get_phase_id()` API function - It is not advisable
    to use hardcoded numbers).

    List of affected variables:
    - sigma

    The output parameter must be filled with the calculated property for each control volume. The
    pressure 'P' and layer or mixture temperature 'T' (Depending on the energy model being used)
    are given in order to perform the calculation. The number of control volumes is also given for
    convenience.

    The programmer must NOT change any variable other than the output. The output size is
    n_control_volumes.
    """


def calculate_phase_pair_state_variable(
    ctx: "void*",
    P: "void*",
    T_mix: "void*",
    n_control_volumes: "int",
    phase1_id: "int",
    phase2_id: "int",
    property_id: "int",
    output: "void*",
) -> "int":
    """
    Hook to calculate the state variable given by the `property_id` (See alfasim_sdk_api common
    headers to retrieve the available property ids), for the phase pair `(phase1_id, phase2_id)`
    (Note that the phase id is the same as the one retrieved from the `get_phase_id()` API function
    - It is not advisable to use hardcoded numbers).

    The output parameter must be filled with the calculated property for each control volume. The
    pressure 'P' and mixture temperature 'T_mix' are given in order to perform the calculation.
    The number of control volumes is also given for convenience.

    The programmer must NOT change any variable other than the output. The output size is
    n_control_volumes.
    """


def finalize_state_variables_calculator(ctx: "void*") -> "int":
    """
    Hook for the state variables calculator finalization.
    The programmer should free/delete any allocated data from the initialization hook.
    """


def compute_mass_fraction_of_tracer_in_phase(
    ctx: "void*",
    phi: "void*",
    phi_phase: "void*",
    tracer_index: "int",
    phase_index: "int",
    n_control_volumes: "int",
) -> "int":
    """
    Internal tracer model Hook to compute the mass fraction of tracer, given by `tracer_id`, in phase,
    given by `phase_id`. The input variable `phi` is the mass fraction of the given tracer in respect to
    the mass of the mixture. The output variable `phi_phase` is the mass fraction of the given tracer in
    respect to the mass of the given phase.

    The programmer must NOT change `phi` variable, only the output variable `phi_phase`. Both `phi` and
    `phi_phase` have size equal to `n_control_volumes`.

    :returns: Return OK if successful or anything different if failed
    """


def compute_mass_fraction_of_tracer_in_field(
    ctx: "void*",
    phi_phase: "void*",
    phi_field: "void*",
    tracer_index: "int",
    field_index: "int",
    phase_index_of_field: "int",
    n_control_volumes: "int",
) -> "int":
    """
    Internal tracer model Hook to compute the mass fraction of tracer, given by `tracer_id`, in field,
    given by `field_id`. The input variable `phi_phase` is the mass fraction of the given tracer in
    respect to the mass of the given phase, in which the id is `phase_id_of_field`. The output variable
    `phi_field` is the mass fraction of the given tracer in respect to the mass of the given field.

    The programmer must NOT change `phi_phase` variable, only the output variable `phi_field`. Both
    `phi_phase` and `phi_field` have size equal to `n_control_volumes`.

    :returns: Return OK if successful or anything different if failed
    """


def update_boundary_condition_of_mass_fraction_of_tracer(
    ctx: "void*", phi_presc: "void*", tracer_index: "int"
) -> "int":
    """
    Internal tracer model Hook to compute the update of the prescribed mass fraction of tracer, given by
    `tracer_id`. The output variable `phi_presc` is the prescribed mass fraction of the given tracer
    in respect to the mass of the mixture.

    :returns: Return OK if successful or anything different if failed
    """


def initialize_mass_fraction_of_tracer(
    ctx: "void*", phi_initial: "void*", tracer_index: "int"
) -> "int":
    """
    Internal tracer model Hook to initialize the mass fraction of tracer, given by `tracer_id`, in the entire
    network. The output variable `phi_initial` is the initial mass fraction of the given tracer in respect
    to the mass of the mixture.

    :returns: Return OK if successful or anything different if failed
    """


def set_prescribed_boundary_condition_of_mass_fraction_of_tracer(
    ctx: "void*", phi_presc: "void*", tracer_index: "int"
) -> "int":
    """
    Internal tracer model Hook to set the initial prescribed bondary condition of mass fraction of tracer,
    given by `tracer_id`. The output variable `phi_presc` is the prescribed mass fraction of the given tracer
    in respect to the mass of the mixture.

    It's important to note that all boundary nodes will be populated with `phi_presc` value set by this hook.

    Another important information is that this hook doesn't have a plugin context, since it is the first value
    that should be set in the boundary condition of mass fraction related to the user defined tracer. Any kind
    of simulator data is not available at this time, however the hook "update_boundary_condition_of_mass_
    fraction_of_tracer" allows the programmer to update this value.

    :returns: Return OK if successful or anything different if failed
    """


specs = HookSpecs(
    project_name="ALFAsim",
    version="1",
    pyd_name="_alfasim_hooks",
    hooks=[
        initialize,
        finalize,
        compute_mass_source_term,
        compute_momentum_source_term,
        compute_energy_source_term,
        compute_tracer_source_term,
        calculate_slip_velocity,
        calculate_slurry_viscosity,
        update_plugins_secondary_variables,
        update_plugins_secondary_variables_extra,
        friction_factor,
        env_temperature,
        calculate_entrained_liquid_fraction,
        update_plugins_secondary_variables_on_first_timestep,
        initialize_state_variables_calculator,
        calculate_state_variable,
        calculate_phase_pair_state_variable,
        finalize_state_variables_calculator,
        compute_mass_fraction_of_tracer_in_phase,
        compute_mass_fraction_of_tracer_in_field,
        update_boundary_condition_of_mass_fraction_of_tracer,
        initialize_mass_fraction_of_tracer,
        set_prescribed_boundary_condition_of_mass_fraction_of_tracer,
    ],
)
