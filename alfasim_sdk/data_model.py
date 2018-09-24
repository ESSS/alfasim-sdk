import functools
from typing import Optional

import attr

from alfasim_sdk.data_types import BaseField


def container_model(*, model: type, caption: str, icon: Optional[str]):
    """
    Container model is a container object that keeps together many different properties.
    Similar to "data_model", the "container_model" can hold properties that are required
    from the application and user properties.

    The difference here is that the "container_model" can also hold a reference to a user-declared
    "data_model", turning this container a parent over the Pool structure TreeStructure
    for this user-declared model.

    1) Application Required:
        - caption: A text to be displayed
        - icon: Name of the icon available at resource folder to be used over the TreeStructure
        - model: A reference for a user-declared class that has the @data_model decorator.

    2) User described:
       Check the module alfasim_sdk.data_types to verify all properties that the user can describe
    """

    def apply(class_):
        setattr(class_, 'model', attr.ib(default=model))

        @functools.wraps(class_)
        def wrap_class(class_, caption, icon):
            return _wrap(caption, icon, class_)

        return wrap_class(class_, caption, icon)

    return apply


def data_model(*, caption: str, icon: Optional[str]=None):
    """
    Data model is a container object that keeps together many different properties.
    There are two kinds of properties that could be used with the "data_model" object:
        1) Application required
        2) User described.

    1) Application Required:
        - caption: A text to be displayed
        - icon: Name of the icon available at resource folder to be used over the TreeStructure

    2) User described:
       Check the module alfasim_sdk.data_types to verify all properties that the user can describe
    """

    def apply(class_: type):
        setattr(class_, 'model', attr.ib(default=None))

        @functools.wraps(class_)
        def wrap_class(class_: type, caption: str, icon: Optional[str]):
            return _wrap(caption, icon, class_)

        return wrap_class(class_, caption, icon)

    return apply


def _wrap(caption: str, icon: Optional[str], class_: type):
    for name in dir(class_):
        value = getattr(class_, name)

        if isinstance(value, BaseField):
            if name.startswith('_'):
                continue
            new_value = attr.ib(default=value)
            setattr(class_, name, new_value)
    setattr(class_, 'caption', attr.ib(default=caption))
    setattr(class_, 'icon', attr.ib(default=icon))
    return attr.s(class_)
