import functools
from typing import Callable

import attr

from alfasim_sdk._internal.alfasim_sdk_utils import get_attr_class
from alfasim_sdk._internal.types import Group
from alfasim_sdk._internal.types import Tab
from alfasim_sdk._internal.types import Tabs


def tabs() -> Callable:
    """
    Create a tab bar layout, to group multiples :func:"tab" instances.

    With the ``tabs``, you can split up complex dialog into "pages" using a :func:"tab" instance.

    Notice that only classes decorated with :func:"tab" can be placed inside a ``tab bar``.

    Example of usage:

    .. code-block:: python

        @data_model(icon="", caption="My Model")
        class MyModel:
            field = String(caption="String outside tabs", value="Default")

            @tabs()
            class MainPage:

                @tab(caption="Fist Tab")
                class Tab1:
                    field_1 = String(caption="First Tab", value="Default")

                @tab(caption="Second Tab")
                class Tab2:
                    field_2 = String(caption="Second Tab", value="Default")

    The image below shows the output from the command above.

    .. image:: /_static/images/api/tabs_layout_example_1.png
        :scale: 90%

    .. image:: /_static/images/api/tabs_layout_example_2.png
        :scale: 90%

    .. note::

        ``tabs`` is a layout component, and will not have an attribute to be accessed through context or API.

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
    The tab represents a single entry, on the :func:`~tabs` layout.

    Notice that only components available at the :ref:`types modules <api-types-section>` can be placed inside a tab.
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

    .. image:: /_static/images/api/group_layout_example.png


    .. note::

        ``group`` is a layout component, and will not have an attribute to be accessed through context or API.

    """

    def apply(class_: type):
        @functools.wraps(class_)
        def wrap_class(class_: type, caption: str):
            return get_attr_class(
                class_, caption, icon=None, model=None, bases=(Group,)
            )

        return wrap_class(class_, caption)

    return apply
