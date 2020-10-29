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
from barril.units import Array
from barril.units import Scalar
from strictyaml.utils import flatten
from typing_inspect import is_optional_type

from alfasim_sdk.alfacase.case_description import CaseDescription

INDENTANTION = "    "


def IsEnum(value):
    return isinstance(value, EnumMeta)


def EnumToAlfacaseSchema(type_, block_indentation):
    return f"Enum({[i.value for i in type_]})"


def IsNumpy1DArray(type_):
    return typing_inspect.is_new_type(type_) and type_.__name__ == "Numpy1DArray"


def Numpy1DArrayToAlfacaseSchema(type_, block_indentation):
    return "Seq(Float())"


def IsList(type_):
    return typing_inspect.get_origin(type_) in (typing.List, list)


def ListToAlfacaseSchema(type_, block_indentation):
    list_value = typing_inspect.get_args(type_)[0]
    return f"Seq({_GetAttrValue(list_value, block_indentation=block_indentation[:-len(INDENTANTION)])})"


def IsFloat(type_):
    return inspect.isclass(type_) and issubclass(type_, float)


def FloatToAlfacaseSchema(type_, block_indentation):
    return "Float()"


def IsBoolean(type_):
    return inspect.isclass(type_) and issubclass(type_, bool)


def BooleanToAlfacaseSchema(type_, block_indentation):
    return "Bool()"


def IsStr(type_):
    return inspect.isclass(type_) and issubclass(type_, str)


def StrToAlfacaseSchema(type_, block_indentation):
    return "Str()"


def IsAttrs(type_):
    return any((hasattr(i, "__attrs_attrs__") for i in flatten([type_])))


def AttrsToAlfacaseSchema(type_, block_indentation):
    return ObtainSchemaName(type_)


def IsDict(type_):
    return typing_inspect.get_origin(type_) in (typing.Dict, dict)


def DictToAlfacaseSchema(type_, block_indentation):
    key_type, value_type = (
        typing_inspect.get_last_args(type_)
        if sys.version_info.minor == 6
        else typing_inspect.get_args(type_)
    )
    return f"MapPattern(Str(), {_GetAttrValue(value_type)})"


def IsUnion(type_):
    return typing_inspect.is_union_type(type_)


@contextmanager
def _MapSection(lines, block_indentation=INDENTANTION):
    lines.append("Map(")
    lines.append(block_indentation + "{")
    yield lines
    lines.append(block_indentation + "}")
    lines.append(block_indentation[: -len(INDENTANTION)] + ")")


def UnionToAlfacaseSchema(type_, *, block_indentation=INDENTANTION):
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
    with _MapSection(lines, block_indentation=block_indentation):
        for arg in type_.__args__:
            key = ConvertToSnakeCase(arg.__name__.replace("Description", ""))
            value = ObtainSchemaName(arg)
            lines.append(
                block_indentation + INDENTANTION + f'Optional("{key}"): Seq({value}),'
            )

    return "\n".join(lines)


def IsScalar(type_):
    return inspect.isclass(type_) and issubclass(type_, Scalar)


def ScalarToAlfacaseSchema(type_, block_indentation):
    return 'Map({"value": Float(), "unit": Str()})'


def IsArray(type_):
    return inspect.isclass(type_) and issubclass(type_, Array)


def ArrayToAlfacaseSchema(type_, block_indentation):
    return 'Map({"values": Seq(Float()), "unit": Str()})'


def IsInt(type_):
    return inspect.isclass(type_) and issubclass(type_, int)


def IntToAlfacaseSchema(type_, block_indentation):
    return "Int()"


def IsPath(type_):
    return inspect.isclass(type_) and issubclass(type_, Path)


def PathToAlfacaseSchema(type_, block_indentation):
    return "Str()"


LIST_OF_IMPLEMENTATIONS = [
    (IsEnum, EnumToAlfacaseSchema),
    (IsAttrs, AttrsToAlfacaseSchema),
    (IsList, ListToAlfacaseSchema),
    (IsFloat, FloatToAlfacaseSchema),
    (IsStr, StrToAlfacaseSchema),
    (IsBoolean, BooleanToAlfacaseSchema),
    (IsNumpy1DArray, Numpy1DArrayToAlfacaseSchema),
    (IsDict, DictToAlfacaseSchema),
    (IsUnion, UnionToAlfacaseSchema),
    (IsScalar, ScalarToAlfacaseSchema),
    (IsArray, ArrayToAlfacaseSchema),
    (IsInt, IntToAlfacaseSchema),
    (IsPath, PathToAlfacaseSchema),
]


def _GetAttrValue(
    type_: type, block_indentation: str = INDENTANTION, key: str = "<Unknown>"
) -> str:
    """
    Indentation is a parameter used for Union and Dict

    If the type parameter is a "Optional" type, only the args are used (without the NoneType)
    """
    if is_optional_type(type_):
        referred_type = typing_inspect.get_args(type_, evaluate=True)[0]
        type_ = referred_type

    for predicate_function, handle_function in LIST_OF_IMPLEMENTATIONS:
        if predicate_function(type_):
            return handle_function(
                type_, block_indentation=block_indentation + INDENTANTION
            )

    raise RuntimeError(
        f"Alfacase Schema does not know how to handle {type_}.\n"
        f"Perhaps you forgot to add the type hint to attribute named '{key}'?"
    )


def ConvertToSnakeCase(value: str) -> str:
    """
    Convert the value from CamelCase to snake_case
    """
    import re

    return re.sub("(?!^)([A-Z]+)", r"_\1", value).lower()


def ObtainSchemaName(class_: type) -> str:
    """Obtains a schema name from TestCase class"""
    return ConvertToSnakeCase(class_.__name__) + "_schema"


def _GetAttrName(key: str, value: attr.ib) -> str:
    """
    Note: for stricyyaml schema, an Optional type means that the user don't need
    to inform a value. While for type hint, an Optional type means that the attribute accepts None.

    Therefore, if the given value has a default, it means a "Optional" type for strictyaml
    """
    return f'"{key}"' if value.default is attr.NOTHING else f'Optional("{key}")'


# plugins:
#   For now, Plugins inputs (GUI) will not be able to be customizable by YAML

# initial_condition_arrays:
#   Only used for tests, doesnt make sense to allows YAML to configure this (for now).

IGNORED_PROPERTIES = (
    "plugins",
    "initial_condition_arrays",
    "nonsplit_equipment",
    "table_parameters",
)


def _GetAttributeSchema(key: str, value: attr.ib, indentation=INDENTANTION * 2) -> str:
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
    attribute_name = _GetAttrName(key, value)
    attribute_value = _GetAttrValue(value.type, block_indentation=indentation, key=key)

    return indentation + f"{attribute_name}: {attribute_value}" + ","


def GenerateAlfacaseSchema(class_: type) -> str:
    """
    Return a schema for the given `class_` that is decorated with @attr and has type hints
    """
    lines = [f"{ObtainSchemaName(class_)} = Map(", f"{INDENTANTION}{{"]
    lines.extend(
        _GetAttributeSchema(key, value)
        for key, value in attr.fields_dict(class_).items()
        if key not in IGNORED_PROPERTIES
    )
    lines.extend([f"{INDENTANTION}}}", ")", ""])

    return "\n".join(lines)


def _IsFromTypingModule(type_: type) -> bool:
    """Helper method to verify if the given `type_` is instance of List/Dict/Union"""
    return IsList(type_) or IsDict(type_) or typing_inspect.is_union_type(type_)


def _ObtainReferredType(type_) -> List[type]:
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

    if IsList(type_):
        type_ = typing_inspect.get_args(type_)[0]
        return _ObtainReferredType(type_) if _IsFromTypingModule(type_) else [type_]

    if typing_inspect.is_union_type(type_):
        return [i for i in type_.__args__ if i is not None.__class__]

    if IsDict(type_):
        return type_.__args__[1]

    raise TypeError(f"type_ must be a List or Union referring other types, got {type_}")


def _GetClasses(class_: type) -> Set[type]:
    """
    Helper function to return a set of attr classes that needs schema
    """

    def NeedsSchema(type_):
        """Helper function to ensure that the given attribute (type_) needs a strict yaml schema"""
        return (
            IsAttrs(type_)
            or _IsFromTypingModule(type_)
            and IsAttrs(_ObtainReferredType(type_))
        )

    def GetAttrClassType(type_):
        """Helper function to retrieve the attr type being referred by the type hint"""
        return type_ if IsAttrs(type_) else _ObtainReferredType(type_)

    classes = []
    for key, value in attr.fields_dict(class_).items():
        if NeedsSchema(value.type) and not key in IGNORED_PROPERTIES:
            classes.append(GetAttrClassType(value.type))

    return set(sorted(flatten(classes), key=operator.attrgetter("__name__")))


def GetAllClassesThatNeedsSchema(class_: type) -> List[type]:
    """
    Iterates over the "class_"  attributes searching for objects that needs schema (attr classes)

    :param type class_:
        Target class to return all elements that needs schema.
    """
    graph = {}
    search_queue = deque()

    graph[CaseDescription] = _GetClasses(class_)
    search_queue += graph[CaseDescription]
    while search_queue:
        attr_class = search_queue.popleft()
        attr_classes = _GetClasses(attr_class)
        graph[attr_class] = attr_classes
        search_queue += graph[attr_class]

    # Topological Sorting to keep dependencies correct
    from toposort import toposort

    result = []
    for dependencies in toposort(graph):
        # Items are sorted to make the results deterministic
        result.extend(sorted(dependencies, key=operator.attrgetter("__name__")))

    return result
