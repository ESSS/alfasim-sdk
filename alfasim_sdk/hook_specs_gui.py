from pluggy import HookspecMarker

hookspec = HookspecMarker("ALFAsim")


@hookspec
def alfasim_get_data_model_type():
    """
    Entry point for the creation of models in ALFAsim
    """


@hookspec
def alfasim_get_additional_variables():
    """
    Allows plugins to register new additional variables on ALFAsim.
    This variable can be used to store internal data from the plugin,
    or it can be used to expose data to the user in the plot window.
    """


@hookspec
def alfasim_get_status(ctx):
    """
    Allows plugins to execute custom checks on ALFAsim.
    This checks can be used to guarantee the consistency of the data,
    or compatibility with some configuration made on ALFAsim.
    """
