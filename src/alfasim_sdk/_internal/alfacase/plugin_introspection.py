import attr

from alfasim_sdk._internal.types import BaseField, Group, Tab, Tabs


def _is_tab(value: BaseField) -> bool:
    """
    Return either the given value is a Tab/Tabs or not
    """
    return isinstance(value, type) and issubclass(value, (Tab, Tabs))


def _is_group(value: BaseField) -> bool:
    """
    Return either the given value is a Group or not
    """
    return isinstance(value, type) and issubclass(value, Group)


def get_attributes(user_model_class) -> list[attr.Attribute]:
    """
    Return only the attribute for the given class, fields related with layout (such as Tabs) are ignored.
    """
    attributes = []
    for attribute in attr.fields(user_model_class):
        if _is_tab(attribute.default) or _is_group(attribute.default):
            attributes.extend(get_attributes(attribute.default))
        else:
            attributes.append(attribute)

    return attributes
