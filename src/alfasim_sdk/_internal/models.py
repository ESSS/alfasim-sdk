import functools
from typing import Callable
from typing import Optional

from alfasim_sdk._internal.alfasim_sdk_utils import get_attr_class


def container_model(*, model: type, caption: str, icon: Optional[str]) -> Callable:
    """
    ``container_model`` is an object that keeps together many different properties defined by the plugin and allows developers
    to build user interfaces in a declarative way similar to :func:`data_model`.

    ``container_model`` can also hold a reference to a :func:`data_model`
    declared from the plugin, making this object a parent for all new :func:`data_model` created.

    .. rubric:: **Application Required**:

    The following options are required when declaring a ``container_model``.

    :param caption:   A text to be displayed over the Tree.
    :param icon:      Name of the icon to be used over the Tree.
    :param model:     A reference to a class decorated with :func:`data_model`.

    .. note::

        Even though the icon parameter is required, it's not currently being used.


    .. rubric:: **Plugin defined**:

    Visual elements that allow the user to input information into the application, or to arrange better the user interface.

    :Input Fields:  Visual elements that allow the user to provide input information into the application.
    :Layout:        Elements that assist the developer to arrange input fields in meaningfully way.

    Check the section :ref:`visual elements <api-types-section>` to see all inputs available, and
    :ref:`layout elements<api-layout-section>` to see all layouts available.

    .. rubric:: Example myplugin.py

    .. code-block:: python

        @data_model(icon="", caption="My Child")
        class ChildModel:
            distance = Quantity(value=1, unit="m", caption="Distance")


        @container_model(icon='', caption='My Container', model=ChildModel)
        class MyModelContainer:
            my_string = String(value='Initial Value', caption='My String')


        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
            return [MyModelContainer]

    .. image:: /_static/images/api/container_model_example_1_1.png
        :scale: 70%

    .. image:: /_static/images/api/container_model_example_1_2.png
        :scale: 70%

    .. image:: /_static/images/api/container_model_example_1_3.png
        :scale: 70%


    Container data also includes automatically two actions for the model:

    .. rubric:: Action: Create new Model

    An action that creates a new model inside the container selected, you can activate this action
    by right-clicking in the container over the Tree, or by clicking on the "Plus" icon available at the ``Model Explorer``.

    .. image:: /_static/images/api/container_model_new_model_1.png
        :scale: 80%

    .. image:: /_static/images/api/container_model_new_model_2.png
        :scale: 80%

    .. rubric:: Action: Remove

    An action that remove the selected model, only available for models inside a container, you can activate this action by
    right-clicking the model over the Tree, or by clicking on the "Trash" icon available at the ``Model Explorer``.

    .. image:: /_static/images/api/container_model_remove_1.png
        :scale: 80%

    .. image:: /_static/images/api/container_model_remove_2.png
        :scale: 80%

    """

    def apply(class_):
        @functools.wraps(class_)
        def wrap_class(class_, caption, icon):
            return get_attr_class(class_, caption, icon, model)

        return wrap_class(class_, caption, icon)

    return apply


def data_model(*, caption: str, icon: Optional[str] = None) -> Callable:
    """
    ``data_model`` is an object that keeps together many different properties defined by the plugin and allows developers
    to build user interfaces in a declarative way.

    .. rubric:: **Application Required**:

    The following options are required when declaring a data_model and are used into the user interface

    :param caption:   A text to be displayed over the Tree.
    :param icon:      Name of the icon to be used over the Tree.

    .. note::

        Even though the icon parameter is required, it's not currently being used.


    .. rubric:: **Plugin Defined**:

    Visual elements that allow the user to input information into the application, or to arrange better the user interface.

    :Input Fields: Visual elements that allow the user to provide input information into the application.
    :Layout: Elements that assist the developer to arrange input fields in a meaningful way.

    Check the section :ref:`visual elements <api-types-section>` to see all inputs available, and
    :ref:`layout elements<api-layout-section>` to see all layouts available.

    Example:

    .. code-block:: python

        @data_model(icon='', caption='My Plugin')
        class MyModel:
                distance = Quantity(value=1, unit='m', caption='Distance')


        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
                return [MyModel]

    .. image:: /_static/images/api/data_model_example_1_1.png
        :scale: 90%

    .. image:: /_static/images/api/data_model_example_1_2.png
        :scale: 90%


    """

    def apply(class_: type):
        @functools.wraps(class_)
        def wrap_class(class_: type, caption: str, icon: Optional[str]):
            return get_attr_class(class_, caption, icon, model=None)

        return wrap_class(class_, caption, icon)

    return apply
