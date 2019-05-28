import functools
from typing import Callable

import attr
from alfasim_sdk._alfasim_sdk_utils import get_attr_class
from alfasim_sdk.types import Group, Tab, Tabs


def tabs() -> Callable:
    """
    tabs is a container that only holds alfasim_sdk.layout.tab.


    Note.: tabs is considered a layout component, therefore, the final model will have any attribute related with the tabs
    """

    def apply(class_: type):
        @functools.wraps(class_)
        def wrap_class(class_: type):
            attr_class = get_attr_class(
                class_, caption="", icon=None, model=None, bases=(Tabs,)
            )

            for value in attr.fields(attr_class):
                if not (
                    isinstance(value.default, type) and issubclass(value.default, Tab)
                ):
                    raise TypeError(
                        f"Error on attribute '{value.name}' expecting a class decorated with @tab but received a {value.default.__class__.__name__} type"
                    )

            return attr_class

        return wrap_class(class_)

    return apply


def tab(*, caption: str) -> Callable:
    """
    tab is a container for other attributes, only BaseField can be defined inside a tab.

    Note.: tab is considered a layout component, therefore, the final model will have any attribute related with the tabs
    """

    def apply(class_: type):
        @functools.wraps(class_)
        def wrap_class(class_: type, caption: str):
            return get_attr_class(class_, caption, icon=None, model=None, bases=(Tab,))

        return wrap_class(class_, caption)

    return apply


def group(*, caption: str) -> Callable:
    """
    group is a container for other attributes, only BaseField can be defined inside a group.

    Note.: group is considered a layout component, therefore, the final model will have any attribute related with the group
    """

    def apply(class_: type):
        @functools.wraps(class_)
        def wrap_class(class_: type, caption: str):
            return get_attr_class(
                class_, caption, icon=None, model=None, bases=(Group,)
            )

        return wrap_class(class_, caption)

    return apply
