import enum
from pathlib import Path
from typing import List

import attr
from barril.units import Array

from _alfasim_sdk.alfacase.generate_schema import IGNORED_PROPERTIES
from _alfasim_sdk.alfacase.generate_schema import is_array
from _alfasim_sdk.alfacase.generate_schema import is_attrs
from _alfasim_sdk.alfacase.generate_schema import is_boolean
from _alfasim_sdk.alfacase.generate_schema import is_dict
from _alfasim_sdk.alfacase.generate_schema import is_enum
from _alfasim_sdk.alfacase.generate_schema import is_float
from _alfasim_sdk.alfacase.generate_schema import is_int
from _alfasim_sdk.alfacase.generate_schema import is_list
from _alfasim_sdk.alfacase.generate_schema import is_path
from _alfasim_sdk.alfacase.generate_schema import is_scalar
from _alfasim_sdk.alfacase.generate_schema import is_str
from _alfasim_sdk.alfacase.generate_schema import is_union
from _alfasim_sdk.alfacase.generate_schema import obtain_schema_name

INDENT = "    "

""" Space needed to reach the root of the literal block. """
BASE_INDENT = " " * 12


def generate_definition(class_name: str) -> str:
    """
    Return a "definition block" for the given class_name showing the declaration of CaseDescription and ALFAcase
    """
    lines = [
        ".. rubric:: Definitions",
        "",
        ".. tab:: CaseDescription",
        "",
        "    .. parsed-literal::",
        "",
    ]
    lines.extend(_generate_declaration_for_class(class_name))
    lines.append("")
    lines.append(".. tab:: Schema")
    lines.append("")
    lines.append("    .. parsed-literal::")
    lines.append("")
    lines.extend(_generate_declaration_for_schema(class_name))
    lines.append("")
    return "\n".join(lines)


def _generate_declaration_for_class(class_) -> List[str]:
    """ Return all attributes for the given Class with CaseDescription definition. """
    class_fields = attr.fields_dict(class_)
    lines = [f"{INDENT*2}class {class_.__name__}"]
    lines.extend(_get_declaration(class_fields, LIST_OF_CASE_ATTRIBUTES))
    return lines


def _generate_declaration_for_schema(class_) -> List[str]:
    """ Return all attributes for the given Class using ALFACase schema definition. """
    class_fields = attr.fields_dict(class_)
    lines = _get_declaration(class_fields, LIST_OF_CASE_SCHEMAS)
    return lines


def _get_declaration(class_, list_of_predicate_and_handles):
    """ Helper class to extract the logic to iterate over the attributes from the given class. """
    lines = []
    for attribute_name, value in class_.items():
        if attribute_name not in IGNORED_PROPERTIES:
            for predicate_function, handle_function in list_of_predicate_and_handles:
                if predicate_function(value.type):
                    attribute_value = handle_function(value.type)
                    lines.append(f"{BASE_INDENT}{attribute_name}: {attribute_value}")
    return lines


def _get_class_with_reference(visible_name, ref, *, add_space=True):
    """
    Return the name of the class with a valid reference to be used by sphinx.

    :param bool add_space:
        inform if the name generated will need to have a unicode space at end (generate by |space|),
        this is necessary when the class is the only reference of an attribute causing this line
        to be mixed with the next line over the documentation.

    """
    reference = f"\\ :class:`{visible_name} <{ref}>`\\"
    if add_space:
        reference += " |space|"
    return reference


def _get_scalar_reference(add_space=True) -> str:
    """ Return a string with a cross-reference to Scalar documentation. """
    return _get_class_with_reference(
        visible_name="Scalar", ref="barril.units.Scalar", add_space=add_space
    )


def _get_array_reference(add_space=True) -> str:
    """ Return a string with a cross-reference to Array documentation. """
    return _get_class_with_reference(
        visible_name="Array", ref="barril.units.Array", add_space=add_space
    )


def _get_list_reference() -> str:
    """ Return a string with a cross-reference to List documentation. """
    return _get_class_with_reference(
        visible_name="List", ref="typing.List", add_space=False
    )


def _get_dict_reference() -> str:
    """ Return a string with a cross-reference to Dict documentation. """
    return _get_class_with_reference(
        visible_name="Dict", ref="typing.Dict", add_space=False
    )


def _get_optional_reference() -> str:
    """ Return a string with a cross-reference to Optional documentation. """
    return _get_class_with_reference(
        visible_name="Optional", ref="typing.Optional", add_space=False
    )


def attrs_formatted(value, *, add_space=True):
    """
    Return the attr class name with a cross-referencing link for the class.

    :param bool add_space:
        inform if the name generated will need to have a unicode space at end (generate by |space|),
        this is necessary when the class is the only reference of an attribute causing this line
        to be mixed with the next line over the documentation.
    """
    name = value.__name__
    return _get_class_with_reference(visible_name=name, ref=name, add_space=add_space)


def list_formatted(value):
    """
    Return a string with a cross-referencing link for the List class and to the refer type.
    """
    name = value.__args__[0].__name__
    list_with_ref = _get_list_reference()
    if is_attrs(value.__args__[0]):
        name = attrs_formatted(value.__args__[0], add_space=False)

    return f"{list_with_ref}[{name}]"


def dict_formatted(value):
    """
    Return a string with a cross-referencing link for the Dict class and to the refer type.
    """
    dict_with_reference = _get_dict_reference()
    referenced_value = value.__args__[1]
    if is_attrs(referenced_value):
        name = attrs_formatted(referenced_value, add_space=False)
    elif is_scalar(referenced_value):
        name = _get_scalar_reference(add_space=False)
    elif is_array(referenced_value):
        name = _get_array_reference(add_space=False)
    else:
        name = str(referenced_value).replace("typing.", "")

    return f"{dict_with_reference}[str, {name}]"


def union_formatted(value):
    """
    Return a string with a cross-referencing link for the Optional module.
    Note that all usages of union on CaseDescription are from the Optional module.
    """
    optional_with_reference = _get_optional_reference()
    ref_value = value.__args__[0]

    if isinstance(ref_value, enum.EnumMeta):
        name = enum_formatted(ref_value)
    elif is_array(ref_value):
        name = _get_array_reference(add_space=False)
    elif is_list(ref_value):
        name = f"{_get_list_reference()}[{ref_value.__args__[0].__name__}]"
    else:
        name = ref_value.__name__

    return f"{optional_with_reference}[{name}]"


def enum_formatted(value):
    """ Return the name of the Enum a cross-referencing link for the constants section. """
    name = value.__name__
    ref_name = f"{value.__module__}.{name}"
    return _get_class_with_reference(visible_name=name, ref=ref_name)


def attrs_formatted_for_schema(value):
    """ Return the name of the schema with a reference for the API reference section. """
    return _get_class_with_reference(
        visible_name=obtain_schema_name(value), ref=value.__name__
    )


def enum_formatted_for_schema(value):
    """ Return the name of the schema with a reference for the API reference section. """
    return _get_class_with_reference(
        visible_name=obtain_schema_name(value),
        ref=f"{value.__module__}.{value.__name__}",
    )


def list_formatted_for_schema(value):
    """
    Return a string showing a list with the parameters used, if the parameter is an attrs class,
    a cross-referencing link will be added.
    """
    block_indentation = BASE_INDENT + INDENT
    argument = value.__args__[0]
    if is_attrs(argument):
        return f"\n{block_indentation}- {attrs_formatted_for_schema(argument)}"

    return f"\n{block_indentation}- {argument.__name__}"


def dict_formatted_for_schema(value):
    """
    Return a string showing a dict with the parameters used, if the parameter is class
    that has a sphinx reference (attr, Scalar, Array) a cross-referencing link will be added.
    """
    lines = f"\n{BASE_INDENT + INDENT}"
    lines += "string: "
    argument = value.__args__[1]

    if is_attrs(argument):
        lines += attrs_formatted_for_schema(argument)
    elif is_union(argument):
        lines += f"{' | '.join(i.__name__.replace('str', 'string') for i in argument.__args__)}"
    elif is_scalar(argument):
        lines += scalar_formatted_for_schema(argument, number_of_indent=2)
    elif is_array(argument):
        lines += array_formatted_for_schema(argument, number_of_indent=2)
    else:
        lines += argument.__name__
    return lines


def union_formatted_for_schema(value):
    """
    All usages of union on CaseDescription are from the Optional module, so this function will
    return a string showing parameters with a label '# optional' indicating that this field could be
    is not mandatory.
    """
    parameter = value.__args__[0]
    if value.__args__ in ((str, type(None)), (Path, type(None))):
        name = "string    # optional"
    elif value.__args__ == (Array, type(None)):
        name = f"{INDENT}# optional"
        name += array_formatted_for_schema(value)
    elif isinstance(parameter, enum.EnumMeta):
        name = f"{enum_formatted_for_schema(parameter)}  # optional"
    elif is_attrs(parameter):
        name = f"{attrs_formatted_for_schema(parameter)}  # optional"
    elif is_list(parameter):
        name = f"{INDENT}# optional"
        name += list_formatted_for_schema(parameter)
    else:
        name = str(value).replace("typing.", "") + " # optional"
    return name


def scalar_formatted_for_schema(value, *, number_of_indent=1):
    """
    Return a string showing how to configure a Scalar.

    :param int number_of_indent:
        How many indentations beyond the base should this schema have,
        useful for when used with other schema such as Dict.
    """
    block_indentation = BASE_INDENT + INDENT * number_of_indent
    return f"\n{block_indentation}value: number\n{block_indentation}unit: string"


def array_formatted_for_schema(value, *, number_of_indent=1):
    """
    Return a string showing how to configure a Array.

    :param int number_of_indent:
        How many indentations beyond the base should this schema have,
        useful for when used with other schema such as Dict.
    """
    block_indentation = BASE_INDENT + INDENT * number_of_indent
    return f"\n{block_indentation}values: [number]\n{block_indentation}unit: string"


LIST_OF_CASE_ATTRIBUTES = [
    (is_enum, enum_formatted),
    (is_attrs, attrs_formatted),
    (is_list, list_formatted),
    (is_float, lambda value: value.__name__),
    (is_str, lambda value: value.__name__),
    (is_boolean, lambda value: value.__name__),
    (is_dict, dict_formatted),
    (is_union, union_formatted),
    (is_scalar, lambda value: _get_scalar_reference()),
    (is_array, lambda value: _get_array_reference()),
    (is_int, lambda value: value.__name__),
    (is_path, lambda value: value.__name__),
]


LIST_OF_CASE_SCHEMAS = [
    (is_enum, enum_formatted),
    (is_attrs, attrs_formatted_for_schema),
    (is_list, list_formatted_for_schema),
    (is_float, lambda value: "number"),
    (is_str, lambda value: "string"),
    (is_boolean, lambda value: "boolean"),
    (is_dict, dict_formatted_for_schema),
    (is_union, union_formatted_for_schema),
    (is_scalar, scalar_formatted_for_schema),
    (is_array, array_formatted_for_schema),
    (is_int, lambda value: "number"),
    (is_path, lambda value: value.__name__),
]
