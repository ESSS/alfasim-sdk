from hookman.hooks import HookSpecs


def initialize(ctx: 'void*') -> 'int':
    """
    This Hook can be used to initialize plugin internal data and also some
    simulator configurations available via API.

    :param ctx: ALFASim's plugins context
    
    :returns: Error code: 0 for success initialization and -1 if something goes wrong.
    """


def finalize(ctx: 'void*') -> 'int':
    """
    This Hook must be used to delete all plugin internal data. Otherwise, a memory
    leak could occur in your plugin.

    :param ctx: ALFASim's plugins context
    
    :returns: Error code: 0 for success finalization and -1 if something goes wrong.
    """


def friction_factor(v1: 'int', v2: 'int') -> 'int':
    """
    Docs for Friction Factor
    """


def env_temperature(v3: 'float', v4: 'float') -> 'float':
    """
    Docs for Environment Temperature
    """


def calculate_entrained_liquid_fraction(
    U_S: 'const double[2]',
    rho: 'const double[2]',
    mu: 'const double[2]',
    sigma: 'double',
    D: 'double',
    ) -> 'double':
    """
    Hook for droplet entrainment model when in annular flow (in unit cell model)

    :param U_S: Gas and liquid superficial velocities [m/s]
    :param rho: Phase densities [kg/m3]
    :param mu: Phase viscosities [Pa.s]
    :param sigma: Surface tension [N.m]
    :param D: Pipe diameter [m]

    :returns:
        Entrainment fraction, defined as the ratio between the droplet mass flow rate and the total liquid
        mass flow rate (dimensionless)
    """


specs = HookSpecs(
    project_name='Alfasim',
    version='1',
    pyd_name='_alfasim_hooks',
    hooks=[
        initialize,
        finalize,
        friction_factor,
        env_temperature,
        calculate_entrained_liquid_fraction,
    ]
)
