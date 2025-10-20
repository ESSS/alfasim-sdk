import textwrap
from collections.abc import Callable, Sequence
from enum import EnumMeta
from functools import partial
from numbers import Number
from typing import (
    Any,
    NewType,
    TypeGuard,
    Union,
)

import attr
import attrs
import numpy as np
from attr.validators import deep_iterable, deep_mapping, in_, instance_of, optional
from barril.curve.curve import Curve
from barril.units import Array, Scalar

Numpy1DArray = NewType("Numpy1DArray", np.ndarray)
PhaseName = str
list_of_strings = deep_iterable(
    member_validator=optional(instance_of(str)), iterable_validator=instance_of(list)
)
list_of_optional_integers = deep_iterable(
    member_validator=optional(instance_of(int)), iterable_validator=instance_of(list)
)
ScalarLike = Union[tuple[Number, str], Scalar]
ArrayLike = Union[tuple[Sequence[Number], str], Array]
CurveLike = Union[tuple[ArrayLike, ArrayLike], Curve]


def generate_multi_input(
    prop_name: str, category: str, default_value: float, unit: str
) -> str:
    return textwrap.dedent(
        f"""\
        # fmt: off
        {prop_name}_input_type: constants.MultiInputType = attrib_enum(default=constants.MultiInputType.Constant)
        {prop_name}: Scalar = attrib_scalar(
            default=Scalar({category!r}, {default_value!r}, {unit!r})
        )
        {prop_name}_curve: Curve = attrib_curve(
            default=Curve(Array({category!r}, [], {unit!r}), Array({"time"!r}, [], {"s"!r}))
        )
        # fmt: on"""
    )


def generate_multi_input_dict(prop_name: str, category: str) -> str:
    return textwrap.dedent(
        f"""\
        # fmt: off
        {prop_name}_input_type: constants.MultiInputType = attrib_enum(default=constants.MultiInputType.Constant)
        {prop_name}: dict[str, Scalar] = attr.ib(
            default=attr.Factory(dict), validator=dict_of(Scalar),
            metadata={{"type": "scalar_dict", "category": {category!r}}},
        )
        {prop_name}_curve: dict[str, Curve] = attr.ib(
            default=attr.Factory(dict), validator=dict_of(Curve),
            metadata={{"type": "curve_dict", "category": {category!r}}},
        )
        # fmt: on"""
    )


def is_two_element_tuple(value: object) -> TypeGuard[tuple[Any, Any]]:
    """
    Check if `value` is a two element tuple.
    """
    return isinstance(value, tuple) and (len(value) == 2)


def prepare_error_message(message: str, error_context: str | None = None) -> str:
    """
    If `error_context` is not None prepend that to error message.
    """
    if error_context is not None:
        return error_context + ": " + message
    else:
        return message


def collapse_array_repr(value: Any) -> str:
    """
    The full repr representation of PVT model takes too much space to print all values inside a array.
    Making annoying to debug Subjects that has a PVT model on it, due to seventy-four lines with only numbers.
    """
    import re

    return re.sub(r"array\(\[.*?\]\)", "array([...])", repr(value), flags=re.DOTALL)


def to_scalar(
    value: ScalarLike, is_optional: bool = False, *, error_context: str | None = None
) -> Scalar:
    """
    Converter to be used with attr.ib, accepts tuples and Scalar as input, is used
    by `attrib_scalar`.
    If `is_optional` is defined, the converter will also accept None.
    If `error_context` is not `None` it is prepended to the type error message when `value` type
    is not respected.

    Ex.:
    @attr.s
    class PositionalOutputDescription:
        pos = attrib_scalar()
        temperature = attrib_scalar(is_optional=True))

    PositionalOutputDescription(position=Scalar(1,"m"))
    PositionalOutputDescription(position=(1,"m"))
    PositionalOutputDescription(temperature=None)
    """
    if is_optional and value is None:
        return value
    if is_two_element_tuple(value):
        return Scalar(value)
    elif isinstance(value, Scalar):
        return value

    message = prepare_error_message(
        f"Expected pair (value, unit) or Scalar, got {value!r} (type: {type(value)})",
        error_context,
    )
    raise TypeError(message)


def to_array(
    value: Any, is_optional: bool = False, *, error_context: str | None = None
) -> Array | None:
    """
    Converter to be used with attr.ib, accepts tuples and Array as input.
    If `is_optional` is defined, the converter will also accept None, same as `to_scalar`.
    The `error_context` has the same behavior as in `to_scalar`.

    Ex.:
    @attr.s
    class Foo:
        bar = attr.id(converter=to_array)

    Foo(bar=Array([1,2,3],"m"))
    Foo(bar=([1,2,3],"m"))
    Foo(bar=((1,2,3),"m"))
    """
    if is_optional and value is None:
        return value
    if is_two_element_tuple(value):
        return Array(*value)
    elif isinstance(value, Array):
        return value

    message = prepare_error_message(
        f"Expected pair (values, unit) or Array, got {value!r} (type: {type(value)})",
        error_context,
    )
    raise TypeError(message)


def to_curve(
    value: Any, is_optional: bool = False, *, error_context: str | None = None
) -> Curve | None:
    """
    Converter to be used with attr.ib, accepts tuples and Scalar as input, is used
    by `attrib_curve`.
    If `is_optional` is defined, the converter will also accept None, same as `to_scalar`.
    The `error_context` has the same behavior as in `to_scalar`.

    Ex.:
    @attr.s
    class Foo:
        bar = attrib_curve()

    Foo(bar=Curve(Array([1,2,3],"m"), Array([0,10,20],"s")))
    Foo(bar=(Array([1,2,3],"m"), Array([0,10,20],"s")))
    Foo(bar=(([1,2,3],"m"), ([0,10,20],"s")))
    Foo(bar=(([1,2,3],"m"), Array([0,10,20],"s")))
    """
    if is_optional and value is None:
        return value
    if is_two_element_tuple(value):
        image = to_array(
            value[0], error_context=prepare_error_message("Curve image", error_context)
        )
        domain = to_array(
            value[1], error_context=prepare_error_message("Curve domain", error_context)
        )
        assert image is not None and domain is not None, (
            "Cannot fail, to_array receiving a float"
        )
        return Curve(image, domain)
    elif isinstance(value, Curve):
        return value

    message = prepare_error_message(
        f"Expected pair (image_array, domain_array) or Curve, got {value!r} (type: {type(value)})",
        error_context,
    )
    raise TypeError(message)


def attrib_scalar(
    default: ScalarLike | attrs.NothingType | None = attr.NOTHING,
    is_optional: bool = False,
    category: str | None = None,
) -> Any:
    """
    Create a new attr attribute with a converter to Scalar accepting also tuple(value, unit).

    :param default:
        Value to be used as default when instantiating a class with this attr.ib

        If a default is not set (``attr.NOTHING``), a value must be supplied when instantiating;
        otherwise, a `TypeError` will be raised.
    """
    if isinstance(default, Scalar):
        if category is None:
            category = default.category
        elif category != default.category:
            raise ValueError("`default`'s category and `category` must match")

    else:
        if category is None:
            raise ValueError(
                "If `default` is not a scalar then `category` is required to be not `None`"
            )
    is_optional = is_optional or (default is None)
    metadata = {"type": "scalar", "category": category}
    return attr.ib(
        default=default,
        converter=partial(to_scalar, is_optional=is_optional),
        metadata=metadata,
    )


def attrib_array(
    default: ArrayLike | attrs.NothingType = attr.NOTHING,
    category: str | None = None,
) -> Any:
    """
    Create a new attr attribute with a converter to Array accepting also tuple(values, unit).

    :param default:
        Value to be used as default when instantiating a class with this attr.ib

        If a default is not set (``attr.NOTHING``), a value must be supplied when instantiating;
        otherwise, a `TypeError` will be raised.

    :param category:
        Name of the array category.

    """
    if isinstance(default, Array):
        if category is None:
            category = default.category
        elif category != default.category:
            raise ValueError("`default`'s category and `category` must match")

    else:
        if category is None:
            raise ValueError(
                "If `default` is not an array then `category` is required to be not `None`"
            )

    metadata = {"type": "array", "category": category}
    return attr.ib(
        default=default,
        converter=to_array,
        metadata=metadata,
    )


def attrib_curve(
    default: CurveLike | attrs.NothingType = attr.NOTHING,
    is_optional: bool = False,
    category: str | None = None,
    domain_category: str | None = None,
) -> Any:
    """
    Create a new attr attribute with a converter to Curve accepting also tuple(image, domain).

    :param default:
        Value to be used as default when instantiating a class with this attr.ib

        If a default is not set (``attr.NOTHING``), a value must be supplied when instantiating;
        otherwise, a `TypeError` will be raised.

    :param category:
        Category of the curve image array.

    :param domain_category:
        Category of the curve domain array.

    """
    if isinstance(default, Curve):
        if category is None:
            category = default.image.category
        elif category != default.image.category:
            raise ValueError("`default` image's category and `category` must match")
        if domain_category is None:
            domain_category = default.domain.category
        elif domain_category != default.domain.category:
            raise ValueError(
                "`default` domain's category and `domain_category` must match"
            )

    else:
        if category is None:
            raise ValueError(
                "If `default` is not a curve then `category` is required to be not `None`"
            )
        if domain_category is None:
            raise ValueError(
                "If `default` is not a curve then `domain_category` is required to be not `None`"
            )

    is_optional = is_optional or (default is None)
    metadata = {
        "type": "curve",
        "category": category,
        "domain_category": domain_category,
    }
    return attr.ib(
        default=default,
        converter=partial(to_curve, is_optional=is_optional),
        metadata=metadata,
    )


def attrib_instance(type_: type, is_optional: bool = False) -> Any:
    """
    Create a new attr attribute with validator for the given type_
    """
    validator: Callable = instance_of(type_)
    metadata = {"type": "instance", "class_": type_}

    if is_optional:
        default = None
        validator = optional(validator)
    else:
        default = attr.Factory(type_)

    return attr.ib(
        default=default,
        validator=validator,
        metadata=metadata,
    )


def attrib_instance_list(type_: type) -> Any:
    """
    Create a new attr attribute with validator for the given type_
    All attributes created are expected to be List of the given type_

    :param type_:
        Inform which type(s) the List should validate.
        When not defined the param type_ will be used the type to be validated.

    """
    # Config validator
    _validator = deep_iterable(
        member_validator=instance_of(type_),
        iterable_validator=instance_of(list),
    )
    metadata = {"type": "instance_list", "class_": type_}
    return attr.ib(
        default=attr.Factory(list),
        validator=_validator,
        metadata=metadata,
    )


def attrib_enum(type_: EnumMeta | None = None, default: Any = attr.NOTHING) -> Any:
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
        type_ = type(default)  # type:ignore[assignment]

    if isinstance(default, EnumMeta):
        raise ValueError(
            f"Default must be a member of Enum and not the Enum class itself, got {default} while expecting"
            f" some of the following members {', '.join([str(i) for i in default])}"  # type:ignore[var-annotated]
        )

    metadata = {"type": "enum", "enum_class": type_}
    return attr.ib(
        default=default,
        validator=in_(type_),  # type:ignore[arg-type]
        metadata=metadata,
    )


def dict_of(type_: type | tuple[type, ...]) -> Callable:
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


def attrib_dict_of(type_: type) -> Any:
    """
    Create a new attr attribute with validator for an atribute that is a dictionary with keys as str (to represent
    the name) and the content of an instance of type_
    """
    metadata = {"type": "dict_of_instance", "class_": type_}
    return attr.ib(
        default=attr.Factory(dict),
        validator=dict_of(type_),
        metadata=metadata,
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
    member_validator=instance_of(float | int),
    iterable_validator=instance_of((list, range)),
)
dict_with_a_list_of_numbers = deep_mapping(
    key_validator=instance_of(str),
    value_validator=list_of_numbers,
    mapping_validator=instance_of(dict),
)


def list_of(type_: type) -> Callable:
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


def numpy_array_validator(dimension: int, is_list: bool = False) -> Callable:
    """
     An attr validator that performs validation of numpy arrays
    :param dimension:
        The number of array dimensions accepts.
    :param is_list:
        A flag to indicate if the attribute is a container of ndarray

    :return: An attr validator that performs validation of instances of ndarray and their dimensions.
    """

    def _numpy_array_validator(instance, attribute, value) -> None:
        def _check_dimension(value, *, position=None) -> None:
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


class InvalidYamlDataError(DescriptionError):
    """
    Error raised when some data in the YAML file is not properly configured.
    """


class InvalidPluginDataError(DescriptionError):
    """
    Error raised when some plugin input data is not in the expected format.
    """
