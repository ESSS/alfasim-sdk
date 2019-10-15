import functools
from typing import Callable

import attr

from alfasim_sdk._alfasim_sdk_utils import get_attr_class
from alfasim_sdk.types import Group
from alfasim_sdk.types import Tab
from alfasim_sdk.types import Tabs


def tabs() -> Callable:
    """
    The tab layout allows the model explore to have a tab bar, which contains can have as many tabs as desired.
    Each tab will have it's one "page" which will displayed all related fields.

    Example of usage:

    .. code-block:: python



    .. note::

        tab is a layout component, therefore, the final model will not have a attribute that can be accessed
        trough context or API.
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
    The tab layout allows the model explore to have a tab bar, which contains can have as many tabs as desired.
    Each tab will have it's one "page" which will displayed all related fields.


    .. note::

        tab is a layout component, therefore, the final model will not have a attribute that can be accessed
        trough context or API.
    """

    def apply(class_: type):
        @functools.wraps(class_)
        def wrap_class(class_: type, caption: str):
            return get_attr_class(class_, caption, icon=None, model=None, bases=(Tab,))

        return wrap_class(class_, caption)

    return apply


def group(*, caption: str) -> Callable:
    """
    The group layout is a container to organize ALFAsim types, only fields that derives from BaseField can be defined inside a group.

    Example.:

    .. code-block:: python

        @data_model(icon="", caption="My Model")
        class MyModel:
            string_field_1 = String(caption="Outside", value="Default")

            @group(caption="Group Container")
            class GroupMain:
                string_field_2 = String(value="Group 1", caption="Inside")
                bool_field = Boolean(value=True, caption="Boolean Field")

    The image below shows the output from the example above.

    .. image:: _static/group_layout_example.png


    .. note::

        group is a layout component, therefore, the final model will not have a attribute that can be accessed
        trough context or API.

    """

    def apply(class_: type):
        @functools.wraps(class_)
        def wrap_class(class_: type, caption: str):
            return get_attr_class(
                class_, caption, icon=None, model=None, bases=(Group,)
            )

        return wrap_class(class_, caption)

    return apply
