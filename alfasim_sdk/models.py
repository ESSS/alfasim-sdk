import functools
from typing import Callable, Optional

from alfasim_sdk._alfasim_sdk_utils import get_attr_class


def container_model(*, model: type, caption: str, icon: Optional[str]) -> Callable:
    """
    Container model is a container object that keeps together many different properties.
    Similar to "data_model", the "container_model" can hold properties that are required
    from the application and user properties.

    The difference here is that the "container_model" can also hold a reference to a user-declared
    "data_model", turning this container a parent over the Pool structure TreeStructure
    for this user-declared model.

    1) Application Required:
    All properties that are required from the application can be accessed from _alfasim_metadata.

    Currently the following options are available:
        - caption: A text to be displayed
        - icon: Name of the icon available at resource folder to be used over the TreeStructure
        - model: A reference for a user-declared class that has the @data_model decorator.

    2) User described:
        All properties defined from the user can be accessed by attrs fields.
        Check the module alfasim_sdk.data_types to verify all properties that the user can describe.
    """

    def apply(class_):

        @functools.wraps(class_)
        def wrap_class(class_, caption, icon):
            return get_attr_class(class_, caption, icon, model)

        return wrap_class(class_, caption, icon)

    return apply


def data_model(*, caption: str, icon: Optional[str]=None) -> Callable:
    """
    Data model is a container object that keeps together many different properties.
    There are two kinds of properties that could be used with the "data_model" object:
        1) Application required
        2) User described.

    1) Application Required:
    All properties that are required from the application can be accessed from _alfasim_metadata.

    Currently the following options are available:
        - caption: A text to be displayed
        - icon: Name of the icon available at resource folder to be used over the TreeStructure
        - model: None (data_model cannot reference another model).

    2) User described:
        All properties defined from the user can be accessed by attrs fields.
        Check the module alfasim_sdk.data_types to verify all properties that the user can describe.
    """

    def apply(class_: type):

        @functools.wraps(class_)
        def wrap_class(class_: type, caption: str, icon: Optional[str]):
            return get_attr_class(class_, caption, icon, model=None)

        return wrap_class(class_, caption, icon)

    return apply
