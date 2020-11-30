from enum import EnumMeta
from functools import partial
from numbers import Number
from typing import Any
from typing import Dict
from typing import List
from typing import NewType
from typing import Optional
from typing import Tuple
from typing import Union

import attr
import numpy as np
from attr.validators import deep_iterable
from attr.validators import deep_mapping
from attr.validators import in_
from attr.validators import instance_of
from attr.validators import optional
from barril.units import Array
from barril.units import Scalar


Numpy1DArray = NewType("Numpy1DArray", np.ndarray)
PhaseName = str
list_of_strings = deep_iterable(
    member_validator=optional(instance_of(str)), iterable_validator=instance_of(list)
)


def collapse_array_repr(value):
    """
    The full repr representation of PVT model takes too much space to print all values inside a array.
    Making annoying to debug Subjects that has a PVT model on it, due to seventy-four lines with only numbers.
    """
    import re

    return re.sub(r"array\(\[.*?\]\)", "array([...])", repr(value), flags=re.DOTALL)


def to_scalar(
    value: Union[Tuple[Number, str], Scalar], is_optional: bool = False
) -> Scalar:
    """
    Converter to be used with attr.ib, accepts tuples and Scalar as input
    If `is_optional` is defined, the converter will also accept None.

    Ex.:
    @attr.s
    class TrendOutputDescription:
        pos = attrib_scalar()
        temperature = attrib_scalar(converter=partial(ToScalar, is_optional=True))

    TrendOutputDescription(position=Scalar(1,"m")
    TrendOutputDescription(position=(1,"m")
    TrendOutputDescription(temperature=None)
    """
    if is_optional and value is None:
        return value
    if isinstance(value, tuple) and (len(value) == 2):
        return Scalar(value)
    elif isinstance(value, Scalar):
        return value

    raise TypeError(
        f"Expected pair (value, unit) or Scalar, got {value!r} (type: {type(value)})"
    )


attr_nothing_type = object


def attrib_scalar(
    default: Optional[
        Union[Tuple[Number, str], Scalar, attr_nothing_type]
    ] = attr.NOTHING,
    is_optional: bool = False,
) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with a converter to Scalar accepting also tuple(value, unit).

    :param default:
        Value to be used as default when instantiating a class with this attr.ib

        If a default is not set (``attr.NOTHING``), a value must be supplied when instantiating;
        otherwise, a `TypeError` will be raised.
    """
    return attr.ib(
        default=default,
        converter=partial(to_scalar, is_optional=is_optional or not default),
        type=Optional[Scalar] if is_optional or not default else Scalar,
    )


def attrib_instance(type_) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with validator for the given type_
    """
    return attr.ib(
        default=attr.Factory(type_), validator=instance_of(type_), type=type_
    )


def attrib_instance_list(
    type_, *, validator_type: Optional[Tuple[Any, ...]] = None
) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with validator for the given type_
    All attributes created are expected to be List of the given type_

    :param validator_type:
        Inform which type(s) the List should validate.
        When not defined the param type_ will be used the type to be validated.

    """
    # Config validator
    _validator_type = validator_type or type_
    _validator = deep_iterable(
        member_validator=instance_of(_validator_type),
        iterable_validator=instance_of(list),
    )

    return attr.ib(default=attr.Factory(list), validator=_validator, type=List[type_])


def attrib_enum(
    type_: Optional[EnumMeta] = None, default: Any = attr.NOTHING
) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with validator for enums
    When a default value is provided the type_ is automatically computed

    Ex.:
    class Foo(Enum):
        A = 'first'

    Valid calls:
        attrib_enum(type_=Foo)      # Default is attr.NOTHING, a value must be supplied when instantiating;
        attrib_enum(default=Foo.a)  # Default is Foo.a and type_ is Foo
        attrib_enum(type_=Foo, default=Foo.a)
    """
    if default is attr.NOTHING and not type_:
        raise RuntimeError("Default or type_ parameter must be provided")

    if default is not attr.NOTHING:
        type_ = type(default)

    if isinstance(default, EnumMeta):
        raise ValueError(
            f"Default must be a member of Enum and not the Enum class itself, got {default} while expecting"
            f" some of the following members {', '.join([str(i) for i in default])}"
        )
    return attr.ib(default=default, validator=in_(type_), type=type_)


def dict_of(type_):
    """
    An attr validator that performs validation of dictionary values.

    :param type_: The type to check for, can be a type or tuple of types

    :raises TypeError:
        raises a `TypeError` if the initializer is called with a wrong type for this particular attribute

    :return: An attr validator that performs validation of dictionary values.
    """
    return deep_mapping(
        key_validator=instance_of(str),
        value_validator=instance_of(type_),
        mapping_validator=instance_of(dict),
    )


def attrib_dict_of(type_) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with validator for an atribute that is a dictionary with keys as str (to represent
    the name) and the content of an instance of type_
    """
    return attr.ib(
        default=attr.Factory(dict), validator=dict_of(type_), type=Dict[str, type_]
    )


dict_of_array = deep_mapping(
    key_validator=instance_of(str),
    value_validator=instance_of(Array),
    mapping_validator=instance_of(dict),
)
dict_with_scalar = deep_mapping(
    key_validator=instance_of(str),
    value_validator=instance_of(Scalar),
    mapping_validator=instance_of(dict),
)
list_of_numbers = deep_iterable(
    member_validator=instance_of(Number), iterable_validator=instance_of((list, range))
)
dict_with_a_list_of_numbers = deep_mapping(
    key_validator=instance_of(str),
    value_validator=list_of_numbers,
    mapping_validator=instance_of(dict),
)


def list_of(type_):
    """
    An attr validator that performs validation of list values.

    :param type_: The type to check for, can be a type or tuple of types

    :raises TypeError:
        raises a `TypeError` if the initializer is called with a wrong type for this particular attribute

    :return: An attr validator that performs validation of values of a list.
    """
    return deep_iterable(
        member_validator=instance_of(type_), iterable_validator=instance_of(list)
    )


def numpy_array_validator(dimension: int, is_list: bool = False):
    """
     An attr validator that performs validation of numpy arrays
    :param dimension:
        The number of array dimensions accepts.
    :param is_list:
        A flag to indicate if the attribute is a container of ndarray

    :return: An attr validator that performs validation of instances of ndarray and their dimensions.
    """

    def _numpy_array_validator(instance, attribute, value):
        def _check_dimension(value, *, position=None):
            """Helper method to check the dimension from ndarray"""
            if value.ndim != dimension:
                raise ValueError(
                    f"attribute '{attribute.name}' from class '{instance.__class__.__name__}' only accepts ndarray "
                    f"with dimension equals to {dimension}, got a ndarray with dimension {value.ndim}"
                    f"{' on position ' + str(position) + '.' if position is not None else '.'}"
                )

        if is_list:
            list_of(np.ndarray)(instance, attribute, value)
            for index, value_from_list in enumerate(value):
                _check_dimension(value=value_from_list, position=index)
        else:
            instance_of(np.ndarray)(instance, attribute, value)
            _check_dimension(value)

    return _numpy_array_validator


class DescriptionError(Exception):
    """
    Base exception for exceptions in case description.
    """


class InvalidReferenceError(DescriptionError):
    """
    Error raised when an attribute has a reference for an element that doesn't exist.
    """


class InvalidYamlData(DescriptionError):
    """
    Error raised when some data in the YAML file is not properly configured.
    """
