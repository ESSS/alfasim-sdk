# mypy: disallow-untyped-defs
import textwrap
from enum import EnumMeta
from functools import partial
from numbers import Number
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import NewType
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

import attr
import numpy as np
from attr.validators import deep_iterable
from attr.validators import deep_mapping
from attr.validators import in_
from attr.validators import instance_of
from attr.validators import optional
from barril.curve.curve import Curve
from barril.units import Array
from barril.units import Scalar


Numpy1DArray = NewType("Numpy1DArray", np.ndarray)
PhaseName = str
list_of_strings = deep_iterable(
    member_validator=optional(instance_of(str)), iterable_validator=instance_of(list)
)
AttrNothingType = type(attr.NOTHING)
ScalarLike = Union[Tuple[Number, str], Scalar]
ArrayLike = Union[Tuple[Sequence[Number], str], Array]
CurveLike = Union[Tuple[ArrayLike, ArrayLike], Curve]


def generate_multi_input(
    prop_name: str, category: str, default_value: float, unit: str
) -> str:
    return textwrap.dedent(
        f"""\
        # fmt: off
        {prop_name}_input_type = attrib_enum(default=constants.MultiInputType.Constant)
        {prop_name} = attrib_scalar(
            default=Scalar({category!r}, {default_value!r}, {unit!r})
        )
        {prop_name}_curve = attrib_curve(
            default=Curve(Array({category!r}, [], {unit!r}), Array({"time"!r}, [], {"s"!r}))
        )
        # fmt: on"""
    )


def generate_multi_input_dict(prop_name: str, category: str) -> str:
    return textwrap.dedent(
        f"""\
        # fmt: off
        {prop_name}_input_type = attrib_enum(default=constants.MultiInputType.Constant)
        {prop_name}: Dict[str, Scalar] = attr.ib(
            default=attr.Factory(dict), validator=dict_of(Scalar),
            metadata={{"type": "scalar_dict", "category": {category!r}}},
        )
        {prop_name}_curve: Dict[str, Curve] = attr.ib(
            default=attr.Factory(dict), validator=dict_of(Curve),
            metadata={{"type": "curve_dict", "category": {category!r}}},
        )
        # fmt: on"""
    )


def is_two_element_tuple(value: object) -> bool:
    """
    Check if `value` is a two element tuple.
    """
    return isinstance(value, tuple) and (len(value) == 2)


def prepare_error_message(message: str, error_context: Optional[str] = None) -> str:
    """
    If `error_context` is not None prepend that to error message.
    """
    if error_context is not None:
        return error_context + ": " + message
    else:
        return message


def collapse_array_repr(value: np.ndarray) -> str:
    """
    The full repr representation of PVT model takes too much space to print all values inside a array.
    Making annoying to debug Subjects that has a PVT model on it, due to seventy-four lines with only numbers.
    """
    import re

    return re.sub(r"array\(\[.*?\]\)", "array([...])", repr(value), flags=re.DOTALL)


def to_scalar(
    value: ScalarLike, is_optional: bool = False, *, error_context: Optional[str] = None
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
    value: ArrayLike, is_optional: bool = False, *, error_context: Optional[str] = None
) -> Array:
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
    value: CurveLike, is_optional: bool = False, *, error_context: Optional[str] = None
) -> Curve:
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
        return Curve(image, domain)
    elif isinstance(value, Curve):
        return value

    message = prepare_error_message(
        f"Expected pair (image_array, domain_array) or Curve, got {value!r} (type: {type(value)})",
        error_context,
    )
    raise TypeError(message)


def attrib_scalar(
    default: Union[ScalarLike, AttrNothingType] = attr.NOTHING,
    is_optional: bool = False,
    category: Optional[str] = None,
) -> attr._make._CountingAttr:
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
        type=Optional[Scalar] if is_optional else Scalar,
        metadata=metadata,
    )


def attrib_array(
    default: Union[ArrayLike, AttrNothingType] = attr.NOTHING,
    is_optional: bool = False,
    category: Optional[str] = None,
) -> attr._make._CountingAttr:
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
    return attr.ib(default=default, converter=to_array, type=Array, metadata=metadata)


def attrib_curve(
    default: Union[CurveLike, AttrNothingType] = attr.NOTHING,
    is_optional: bool = False,
    category: Optional[str] = None,
) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with a converter to Curve accepting also tuple(image, domain).

    :param default:
        Value to be used as default when instantiating a class with this attr.ib

        If a default is not set (``attr.NOTHING``), a value must be supplied when instantiating;
        otherwise, a `TypeError` will be raised.

    :param category:
        Category of the curve image array.

    """
    if isinstance(default, Curve):
        if category is None:
            category = default.image.category
        elif category != default.image.category:
            raise ValueError("`default` image's category and `category` must match")

    else:
        if category is None:
            raise ValueError(
                "If `default` is not a curve then `category` is required to be not `None`"
            )

    is_optional = is_optional or (default is None)
    metadata = {"type": "curve", "category": category}
    return attr.ib(
        default=default,
        converter=partial(to_curve, is_optional=is_optional),
        type=Optional[Curve] if is_optional else Curve,
        metadata=metadata,
    )


def attrib_instance(type_: type) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with validator for the given type_
    """
    metadata = {"type": "instance", "class_": type_}
    return attr.ib(
        default=attr.Factory(type_),
        validator=instance_of(type_),
        type=type_,
        metadata=metadata,
    )


def attrib_instance_list(type_: type) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with validator for the given type_
    All attributes created are expected to be List of the given type_

    :param validator_type:
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
        type=List[type_],
        metadata=metadata,
    )


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

    metadata = {"type": "enum", "enum_class": type_}
    return attr.ib(default=default, validator=in_(type_), type=type_, metadata=metadata)


def dict_of(type_: type) -> Callable:
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


def attrib_dict_of(type_: type) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with validator for an atribute that is a dictionary with keys as str (to represent
    the name) and the content of an instance of type_
    """
    metadata = {"type": "dict_of_instance", "class_": type_}
    return attr.ib(
        default=attr.Factory(dict),
        validator=dict_of(type_),
        type=Dict[str, type_],
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
    member_validator=instance_of(Number), iterable_validator=instance_of((list, range))
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
