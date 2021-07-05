import inspect
import operator
import sys
import typing
from collections import deque
from contextlib import contextmanager
from enum import EnumMeta
from pathlib import Path
from typing import List
from typing import Set

import attr
import typing_inspect
from barril.curve.curve import Curve
from barril.units import Array
from barril.units import Scalar
from strictyaml.utils import flatten
from typing_inspect import is_optional_type

from alfasim_sdk import CaseDescription

INDENTANTION = "    "


def is_enum(value: typing.Any):
    return isinstance(value, EnumMeta)


def enum_to_alfacase_schema(type_: type, indent: int) -> str:
    return f"Enum({[i.value for i in type_]})"


def is_numpy_1_darray(type_: type) -> bool:
    return typing_inspect.is_new_type(type_) and type_.__name__ == "Numpy1DArray"


def numpy_1_darray_to_alfacase_schema(type_: type, indent: int) -> str:
    return "Seq(Float())"


def is_list(type_: type) -> bool:
    return typing_inspect.get_origin(type_) in (typing.List, list)


def list_to_alfacase_schema(type_: type, indent: int) -> str:
    list_value = typing_inspect.get_args(type_)[0]
    return f"Seq({_get_attr_value(list_value, indent=indent+1)})"


def is_float(type_: type) -> bool:
    return inspect.isclass(type_) and issubclass(type_, float)


def float_to_alfacase_schema(type_: type, indent: int) -> str:
    return "Float()"


def is_boolean(type_: type) -> bool:
    return inspect.isclass(type_) and issubclass(type_, bool)


def boolean_to_alfacase_schema(type_: type, indent: int) -> str:
    return "Bool()"


def is_str(type_: type) -> bool:
    return inspect.isclass(type_) and issubclass(type_, str)


def str_to_alfacase_schema(type_: type, indent: int) -> str:
    return "Str()"


def is_attrs(type_: type) -> bool:
    return any((hasattr(i, "__attrs_attrs__") for i in flatten([type_])))


def attrs_to_alfacase_schema(type_: type, indent: int) -> str:
    return obtain_schema_name(type_)


def is_dict(type_: type) -> bool:
    return typing_inspect.get_origin(type_) in (typing.Dict, dict)


def dict_to_alfacase_schema(type_: type, indent: int) -> str:
    key_type, value_type = (
        typing_inspect.get_last_args(type_)
        if sys.version_info.minor == 6
        else typing_inspect.get_args(type_)
    )
    body_indent = indent + 1
    value_schema = _get_attr_value(value_type, indent=body_indent)
    if "\n" in value_schema:
        lines = [
            "MapPattern(",
            f"{INDENTANTION * body_indent}Str(),",
            f"{INDENTANTION * body_indent}{value_schema},",
            f"{INDENTANTION * indent})",
        ]
        return "\n".join(lines)
    else:
        return f"MapPattern(Str(), {value_schema})"


def is_union(type_: type) -> bool:
    return typing_inspect.is_union_type(type_)


@contextmanager
def _map_section(lines: List[str], indent=0) -> List[str]:
    body_indent = indent + 1
    lines.append("Map(")
    lines.append(f"{INDENTANTION * body_indent}{{")
    yield lines
    lines.append(f"{INDENTANTION * body_indent}}}")
    lines.append(f"{INDENTANTION * indent})")


def union_to_alfacase_schema(type_: type, *, indent=0) -> str:
    """
    Creates a structure that allows multiples types for the same key.

    There is a validator for this kind of situation within strictyaml but does not work
    with Maps/Seqs as discussed in https://github.com/crdoconnor/strictyaml/issues/51
    The alternative presented from the maintainer was to use the `revalidate` method after the load.

    To avoid that much workaround with this kind of validation,
    I'm letting the YAML writers to correctly identify the type through the keys.

    Note that the current implementation only works for attr classes and file paths,
    which can be a string or path (such as PvtModel tables)

    The current implementation doesn't work in cases where multiple types are required for the same attribute.
    Ex.: like str | float or List[float] | float
    """
    # PvtModel Tables
    if set(type_.__args__) == {str, Path}:
        return "Str()"

    # Attrs classes
    lines = []
    map_items_indent = indent + 2
    with _map_section(lines, indent=indent):
        for arg in type_.__args__:
            key = convert_to_snake_case(arg.__name__.replace("Description", ""))
            value = obtain_schema_name(arg)
            lines.append(
                f'{INDENTANTION * map_items_indent}Optional("{key}"): Seq({value}),'
            )

    return "\n".join(lines)


def is_scalar(type_: type) -> bool:
    return inspect.isclass(type_) and issubclass(type_, Scalar)


def scalar_to_alfacase_schema(type_: type, indent: int) -> str:
    return 'Map({"value": Float(), "unit": Str()})'


def is_array(type_: type) -> bool:
    return inspect.isclass(type_) and issubclass(type_, Array)


def array_to_alfacase_schema(type_: type, indent: int) -> str:
    return 'Map({"values": Seq(Float()), "unit": Str()})'


def is_curve(type_: type) -> bool:
    return inspect.isclass(type_) and issubclass(type_, Curve)


def curve_to_alfacase_schema(type_: type, indent: int) -> str:
    map_items_indent = indent + 2
    array_schema = array_to_alfacase_schema(float, indent=map_items_indent)

    with _map_section([], indent=indent) as lines:
        lines.append(f'{INDENTANTION * map_items_indent}"image": {array_schema},')
        lines.append(f'{INDENTANTION * map_items_indent}"domain": {array_schema},')

    return "\n".join(lines)


def is_int(type_: type) -> bool:
    # bool is a subclass of int, but we are not intersted in matching that here.
    return inspect.isclass(type_) and issubclass(type_, int) and not is_boolean(type_)


def int_to_alfacase_schema(type_: type, indent: int) -> str:
    return "Int()"


def is_path(type_: type) -> bool:
    return inspect.isclass(type_) and issubclass(type_, Path)


def path_to_alfacase_schema(type_: type, indent: int) -> str:
    return "Str()"


LIST_OF_IMPLEMENTATIONS: List[typing.Tuple[type, typing.Callable]] = [
    (is_enum, enum_to_alfacase_schema),
    (is_attrs, attrs_to_alfacase_schema),
    (is_list, list_to_alfacase_schema),
    (is_float, float_to_alfacase_schema),
    (is_str, str_to_alfacase_schema),
    (is_boolean, boolean_to_alfacase_schema),
    (is_numpy_1_darray, numpy_1_darray_to_alfacase_schema),
    (is_dict, dict_to_alfacase_schema),
    (is_union, union_to_alfacase_schema),
    (is_scalar, scalar_to_alfacase_schema),
    (is_array, array_to_alfacase_schema),
    (is_curve, curve_to_alfacase_schema),
    (is_int, int_to_alfacase_schema),
    (is_path, path_to_alfacase_schema),
]


def _get_attr_value(type_: type, indent: int, key: str = "<Unknown>") -> str:
    """
    Indentation is a parameter used for Union and Dict.
    If the type parameter is a "Optional" type, only the args are used (without the NoneType)
    """
    if is_optional_type(type_):
        referred_type = typing_inspect.get_args(type_, evaluate=True)[0]
        type_ = referred_type

    for predicate_function, handle_function in LIST_OF_IMPLEMENTATIONS:
        if predicate_function(type_):
            return handle_function(type_, indent=indent)

    raise RuntimeError(
        f"Alfacase Schema does not know how to handle {type_}.\n"
        f"Perhaps you forgot to add the type hint to attribute named '{key}'?"
    )


def convert_to_snake_case(value: str) -> str:
    """
    Convert the value from CamelCase to snake_case.
    Regex from: https://github.com/jpvanhal/inflection/blob/0.5.1/inflection/__init__.py#L397
    """
    import re

    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", value)
    value = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", value)
    value = value.replace("-", "_")
    return value.lower()


def obtain_schema_name(class_: type) -> str:
    """Obtains a schema name from TestCase class"""
    return convert_to_snake_case(class_.__name__) + "_schema"


def _get_attr_name(key: str, value: attr.ib) -> str:
    """
    Note: for stricyyaml schema, an Optional type means that the user don't need
    to inform a value. While for type hint, an Optional type means that the attribute accepts None.

    Therefore, if the given value has a default, it means a "Optional" type for strictyaml
    """
    return f'"{key}"' if value.default is attr.NOTHING else f'Optional("{key}")'


# plugins:
#   For now, Plugins inputs (GUI) will not be able to be customizable by YAML

IGNORED_PROPERTIES = (
    "plugins",
    "table_parameters",
    "emulsion_model_plugin_id",
)


def _get_attribute_schema(key: str, value: attr.ib, indent: int = 2) -> str:
    """
    Helper method that return the equivalent schema for the given key and value.

    Keep in mind that for stricyyaml schema, an Optional type means that the user don't need
    to inform a value. While for type hint, an Optional type means that the attribute accepts None.
    """
    if value.default is attr.NOTHING and is_optional_type(value.type):
        msg = (
            "StrictYAML doesn't support None value (only missing keys denote a value), "
            "therefore Optional type are only allowed when the case has a default value."
        )
        raise TypeError(msg)
    attribute_name = _get_attr_name(key, value)
    attribute_value = _get_attr_value(value.type, indent=indent, key=key)

    return f"{INDENTANTION * indent}{attribute_name}: {attribute_value}" + ","


def generate_alfacase_schema(class_: type) -> str:
    """
    Return a schema for the given `class_` that is decorated with @attr and has type hints.
    """
    lines = [f"{obtain_schema_name(class_)} = Map(", f"{INDENTANTION}{{"]
    lines.extend(
        _get_attribute_schema(key, value)
        for key, value in attr.fields_dict(class_).items()
        if key not in IGNORED_PROPERTIES
    )
    lines.extend([f"{INDENTANTION}}}", ")", ""])

    return "\n".join(lines)


def _is_from_typing_module(type_: type) -> bool:
    """
    Helper method to verify if the given `type_` is instance of List/Dict/Union.
    """
    return is_list(type_) or is_dict(type_) or typing_inspect.is_union_type(type_)


def _obtain_referred_type(type_) -> List[type]:
    """
    Obtain the type referred by the type hint.

    Example.:
        class A()
            first: List[str]
            second: List[Foo]
            third: Union[Foo, Bar]
            fourth: List[Union[Foo, Bar]]
            fifth: Union[str, int]

    Running `_ObtainReferredType` on each field will return:
        first => [str]
        second => [Foo]
        third => [Foo, Bar]
        fourth => [Foo, Bar]
        fifth => [str, int]

    If type_ is not either a List or Union, an TypeError exception will be raised.
    """

    if is_list(type_):
        type_ = typing_inspect.get_args(type_)[0]
        return (
            _obtain_referred_type(type_) if _is_from_typing_module(type_) else [type_]
        )

    if typing_inspect.is_union_type(type_):
        return [i for i in type_.__args__ if i is not None.__class__]

    if is_dict(type_):
        return type_.__args__[1]

    raise TypeError(f"type_ must be a List or Union referring other types, got {type_}")


def _get_classes(class_: type) -> Set[type]:
    """
    Helper function to return a set of attr classes that needs schema.
    """

    def needs_schema(type_):
        """Helper function to ensure that the given attribute (type_) needs a strict yaml schema"""
        return is_attrs(type_) or (
            _is_from_typing_module(type_) and is_attrs(_obtain_referred_type(type_))
        )

    def get_attr_class_type(type_):
        """Helper function to retrieve the attr type being referred by the type hint"""
        return type_ if is_attrs(type_) else _obtain_referred_type(type_)

    classes = []
    for key, value in attr.fields_dict(class_).items():
        if needs_schema(value.type) and not key in IGNORED_PROPERTIES:
            classes.append(get_attr_class_type(value.type))

    return set(flatten(classes))


def get_all_classes_that_needs_schema(class_: type) -> List[type]:
    """
    Iterates over the "class_"  attributes searching for objects that needs schema (attr classes)

    :param type class_:
        Target class to return all elements that needs schema.
    """
    graph = {}
    search_queue = deque()

    graph[CaseDescription] = _get_classes(class_)
    search_queue += graph[CaseDescription]
    while search_queue:
        attr_class = search_queue.popleft()
        attr_classes = _get_classes(attr_class)
        graph[attr_class] = attr_classes
        search_queue += graph[attr_class]

    # Topological Sorting to keep dependencies correct
    from toposort import toposort

    result = []
    for dependencies in toposort(graph):
        # Items are sorted to make the results deterministic
        result.extend(sorted(dependencies, key=operator.attrgetter("__name__")))

    return result
