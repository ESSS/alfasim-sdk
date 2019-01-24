import alfasim_sdk


def string_is_not_empty(instance, attribute, value):
    """
    A validator that raises a ValueError if the initializer is called with a empty string '' or '  '
    """
    if not value or value.isspace():
        if type(instance) is alfasim_sdk.types.Enum:
            raise ValueError(f'Enum type cannot have an empty string on field "{attribute.name}"')

        raise ValueError(f'The field "{attribute.name}" cannot be empty')
