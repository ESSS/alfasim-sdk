from pluggy import HookspecMarker

hookspec = HookspecMarker("alfasim")


@hookspec
def alfasim_get_data_model_type():
    """
    Entry point for the creation of models in Alfasim
    """
