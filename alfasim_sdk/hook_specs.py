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


def compute_source_terms(
    ctx: "void*",
    mass_source: "void*",
    momentum_source: "void*",
    energy_source: "void*",
    phi_source: "void*",
) -> "int":
    """
    Internal simulator hook to compute source terms of mass, momentum and energy equations.
    This is called after all residual functions are evaluated.

    :param ctx: ALFAsim's plugins context
    :param mass_source: Source term of mass equation
    :param momentum_source: Source term of momentum equation
    :param energy_source: Source term of energy equation
    :param phi_source: Source term of tracers mass equation

    :returns: Return OK if successful or anything different if failed
    """


def calculate_slip_velocity(
    ctx: "void*",
    U_fields: "void*",
    α_f: "void*",
    d_disp_fields: "void*",
    P: "void*",
    ρ_f: "void*",
    μ_f: "void*",
    sinθ_f: "void*",
    Δx_f: "void*",
) -> "int":
    """
    Internal simulator hook to calculate slip velocity between fluids
    and solids.

    :param ctx: ALFAsim's plugins context
    :param U_fields: Field velocities,
    :param α_f: Field Volume fractions on faces,
    :param d_disp_fields: Diameter of dispersed fields,
    :param P: Pressure,
    :param ρ_f: Field densities on faces,
    :param μ_f: Field viscosities on faces,
    :param sinθ_f: Sin of θ on faces in which θ is the angle between the Pipe and the Y-Axis,
    :param Δx_f: The control volume lenght related to the faces,

    :returns: Return OK if successful or anything different if failed
    """


def calculate_slurry_viscosity(
    ctx: "void*",
    α_f: "void*",
    μ_f: "void*",
    μ_f_layer: "void*",
) -> "int":
    """
    Internal simulator hook to calculate slurry viscosity of layer(s).

    :param ctx: ALFAsim's plugins context
    :param α_f: Fields Volume fractions on faces,
    :param μ_f: Field viscosities on faces,
    :param μ_f_layer: Layer Viscosities on faces,

    :returns: Return OK if successful or anything different if failed
    """


def update_plugins_secondary_variables(ctx: "void*") -> "int":
    """
    Internal simulator hook to update plugin's secondary variables.
    This is called as the last step on ALFAsim's update internal variables workflow.

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


specs = HookSpecs(
    project_name="ALFAsim",
    version="1",
    pyd_name="_alfasim_hooks",
    hooks=[
        initialize,
        finalize,
        compute_source_terms,
        update_plugins_secondary_variables,
        friction_factor,
        env_temperature,
        calculate_entrained_liquid_fraction,
    ],
)
