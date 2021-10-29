import enum
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Sequence
from typing import Tuple
from typing import Type

import attr
from attr._make import Attribute
from barril.curve.curve import Curve
from barril.units import Array
from barril.units._scalar import Scalar

from alfasim_sdk._internal.alfacase.generate_schema import IGNORED_PROPERTIES
from alfasim_sdk._internal.alfacase.generate_schema import is_array
from alfasim_sdk._internal.alfacase.generate_schema import is_attrs
from alfasim_sdk._internal.alfacase.generate_schema import is_boolean
from alfasim_sdk._internal.alfacase.generate_schema import is_curve
from alfasim_sdk._internal.alfacase.generate_schema import is_dict
from alfasim_sdk._internal.alfacase.generate_schema import is_enum
from alfasim_sdk._internal.alfacase.generate_schema import is_float
from alfasim_sdk._internal.alfacase.generate_schema import is_int
from alfasim_sdk._internal.alfacase.generate_schema import is_list
from alfasim_sdk._internal.alfacase.generate_schema import is_path
from alfasim_sdk._internal.alfacase.generate_schema import is_scalar
from alfasim_sdk._internal.alfacase.generate_schema import is_str
from alfasim_sdk._internal.alfacase.generate_schema import is_union
from alfasim_sdk._internal.alfacase.generate_schema import obtain_schema_name


INDENT = "    "

""" Space needed to reach the root of the literal block. """
BASE_INDENT = " " * 12

CATEGORIES_USED_ON_DESCRIPTION = sorted(
    [
        "angle per time",
        "density",
        "dimensionless",
        "dynamic viscosity",
        "emissivity",
        "flow coefficient",
        "force",
        "force per velocity",
        "force per velocity squared",
        "heat transfer coefficient",
        "length",
        "mass",
        "mass flow rate",
        "mass fraction",
        "mass per mol",
        "molar thermodynamic energy",
        "molar volume",
        "mole per mole",
        "power",
        "pressure",
        "productivity index",
        "specific heat capacity",
        "standard volume per standard volume",
        "standard volume per standard volume",
        "standard volume per time",
        "temperature",
        "thermal conductivity",
        "time",
        "velocity",
        "volume flow rate",
        "volume fraction",
        "volumetric thermal expansion",
    ]
)


def generate_list_of_units(category: str) -> str:
    """Return an admonition with toggle to show the units available for a given category."""
    from barril.units import UnitDatabase

    unit_database = UnitDatabase.GetSingleton()
    units = unit_database.GetCategoryInfo(category).valid_units_set
    info = unit_database.unit_to_unit_info
    body = [f'    :"{unit}": {info[unit].name}' for unit in units]
    lines = [
        f".. admonition:: Available units for category '{category}'",
        "    :class: dropdown",
        "",
        *sorted(body, key=str.casefold),
        "",
    ]
    return "\n".join(lines)


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
        *_generate_declaration_for_class(class_name),
        "",
        ".. tab:: Schema",
        "",
        "    .. parsed-literal::",
        "",
    ]

    lines.extend(_generate_declaration_for_schema(class_name))
    lines.append("")
    return "\n".join(lines)


def _generate_declaration_for_class(class_: Any) -> List[str]:
    """Return all attributes for the given Class with CaseDescription definition."""
    class_fields = attr.fields_dict(class_)
    return [
        f"{INDENT*2}class {class_.__name__}",
        *_get_declaration(class_fields, LIST_OF_CASE_ATTRIBUTES),
    ]


def _generate_declaration_for_schema(class_: Any) -> List[str]:
    """Return all attributes for the given Class using ALFACase schema definition."""
    class_fields = attr.fields_dict(class_)
    return _get_declaration(class_fields, LIST_OF_CASE_SCHEMAS, is_schema=True)


def _get_case_attr_default_value(value: attr.Attribute) -> str:
    """Return the default value of a CaseDescription."""

    if value.default == attr.NOTHING:
        return ""

    default_value_string = " = "
    if isinstance(value.default, enum.Enum):
        default_value_string += (
            f"{value.default.__class__.__name__}.{value.default.name}"
        )
    elif isinstance(value.default, attr.Factory):
        if value.default.factory is dict:
            default_value_string += "{}"
        elif value.default.factory is list:
            default_value_string += "[]"
        elif is_attrs(value.default.factory):
            default_value_string += f"{value.default.factory.__name__}()"
        else:
            default_value_string += "UNKNOWN FACTORY"
    elif is_attrs(value.default):
        default_value_string += f"{value.default.__class__.__name__}()"
    else:
        default_value_string += f"{repr(value.default)}"

    return default_value_string


def _get_declaration(
    class_: Dict[str, Attribute],
    list_of_predicate_and_handles: Sequence[Tuple[Callable, Callable]],
    is_schema: bool = False,
) -> List[str]:
    """Helper class to extract the logic to iterate over the attributes from the given class."""
    lines = []
    for attribute_name, value in class_.items():
        if attribute_name not in IGNORED_PROPERTIES:
            for predicate_function, handle_function in list_of_predicate_and_handles:
                if predicate_function(value.type):
                    attribute_value = handle_function(value.type)
                    default_value = _get_case_attr_default_value(value)

                    # For Schema: if the attributes have a default value the entry is optional.
                    if default_value and is_schema:
                        if attribute_value.lstrip(" \t").startswith("\n"):
                            attribute_value = " # optional" + attribute_value
                        else:
                            attribute_value += "  # optional"
                        default_value = ""

                    # If attribute_value ends with backslash (because of the cross-reference), add extra space
                    # for a default value.
                    # Otherwise, the equal symbol will be sticky with the link.
                    if default_value and attribute_value[-1] == "\\":
                        default_value = f" {default_value}"

                    line_content = f"{BASE_INDENT}{attribute_name}: {attribute_value}{default_value}"

                    # Remove the last character if it's a backslash otherwise the line break will be avoided.
                    if line_content.endswith("\\"):
                        line_content = line_content[:-1]

                    lines.append(line_content)
                    break  # Match found, break inner loop
    return lines


def _get_class_with_reference(visible_name: str, ref: str) -> str:
    """
    Return the name of the class with a valid reference to be used by sphinx.
    """
    return f"\\ :class:`{visible_name} <{ref}>`\\"


def _get_scalar_reference() -> str:
    """Return a string with a cross-reference to Scalar documentation."""
    return _get_class_with_reference(visible_name="Scalar", ref="barril.units.Scalar")


def _get_array_reference() -> str:
    """Return a string with a cross-reference to Array documentation."""
    return _get_class_with_reference(visible_name="Array", ref="barril.units.Array")


def _get_curve_reference() -> str:
    """Return a string with a cross-reference to Curve documentation."""
    return _get_class_with_reference(
        visible_name="Curve", ref="barril.curve.curve.Curve"
    )


def _get_list_reference() -> str:
    """Return a string with a cross-reference to List documentation."""
    return _get_class_with_reference(visible_name="List", ref="typing.List")


def _get_dict_reference() -> str:
    """Return a string with a cross-reference to Dict documentation."""
    return _get_class_with_reference(visible_name="Dict", ref="typing.Dict")


def _get_optional_reference() -> str:
    """Return a string with a cross-reference to Optional documentation."""
    return _get_class_with_reference(visible_name="Optional", ref="typing.Optional")


def attrs_formatted(value: Any) -> str:
    """
    Return the attr class name with a cross-referencing link for the class.
    """
    name = value.__name__
    return _get_class_with_reference(visible_name=name, ref=name)


def list_formatted(value: Any) -> str:
    """
    Return a string with a cross-referencing link for the List class and to the refer type.
    """
    name = value.__args__[0].__name__
    list_with_ref = _get_list_reference()
    if is_attrs(value.__args__[0]):
        name = attrs_formatted(value.__args__[0])

    return f"{list_with_ref}[{name}]"


def dict_formatted(value: Any) -> str:
    """
    Return a string with a cross-referencing link for the Dict class and to the refer type.
    """
    dict_with_reference = _get_dict_reference()
    referenced_value = value.__args__[1]
    if is_attrs(referenced_value):
        name = attrs_formatted(referenced_value)
    elif is_scalar(referenced_value):
        name = _get_scalar_reference()
    elif is_array(referenced_value):
        name = _get_array_reference()
    else:
        name = str(referenced_value).replace("typing.", "")

    return f"{dict_with_reference}[str, {name}]"


def union_formatted(value: Any) -> str:
    """
    Return a string with a cross-referencing link for the Optional module.
    Note that all usages of union on CaseDescription are from the Optional module.
    """
    optional_with_reference = _get_optional_reference()
    ref_value = value.__args__[0]

    if isinstance(ref_value, enum.EnumMeta):
        name = enum_formatted(ref_value)
    elif is_array(ref_value):
        name = _get_array_reference()
    elif is_list(ref_value):
        name = f"{_get_list_reference()}[{ref_value.__args__[0].__name__}]"
    else:
        name = ref_value.__name__

    return f"{optional_with_reference}[{name}]"


def enum_formatted(value: Any) -> str:
    """Return the name of the Enum a cross-referencing link for the constants section."""
    name = value.__name__
    ref_name = f"{value.__module__}.{name}"
    return _get_class_with_reference(visible_name=name, ref=ref_name)


def attrs_formatted_for_schema(value: Any) -> str:
    """Return the name of the schema with a reference for the API reference section."""
    return _get_class_with_reference(
        visible_name=obtain_schema_name(value), ref=value.__name__
    )


def enum_formatted_for_schema(value: enum.EnumMeta) -> str:
    """Return the name of the schema with a reference for the API reference section."""
    return _get_class_with_reference(
        visible_name=obtain_schema_name(value),
        ref=f"{value.__module__}.{value.__name__}",
    )


def list_formatted_for_schema(value: Any) -> str:
    """
    Return a string showing a list with the parameters used, if the parameter is an attrs class,
    a cross-referencing link will be added.
    """
    block_indentation = BASE_INDENT + INDENT
    argument = value.__args__[0]
    if is_attrs(argument):
        return f"\n{block_indentation}- {attrs_formatted_for_schema(argument)}"

    return f"\n{block_indentation}- {argument.__name__}"


def dict_formatted_for_schema(value: Any) -> str:
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


def union_formatted_for_schema(value: Any) -> str:
    """
    All usages of union on CaseDescription are from the Optional module, so this function will
    return a string showing parameters with a label '# optional' indicating that this field could be
    is not mandatory.
    """
    parameter = value.__args__[0]
    if value.__args__ in ((str, type(None)), (Path, type(None))):
        name = "string"
    elif value.__args__ == (Scalar, type(None)):
        name = scalar_formatted_for_schema(value)
    elif value.__args__ == (Array, type(None)):
        name = array_formatted_for_schema(value)
    elif isinstance(parameter, enum.EnumMeta):
        name = f"{enum_formatted_for_schema(parameter)}"
    elif is_attrs(parameter):
        name = f"{attrs_formatted_for_schema(parameter)}"
    elif is_list(parameter):
        name = f"{INDENT}"
        name += list_formatted_for_schema(parameter)
    else:
        name = str(value).replace("typing.", "")
    return name


def scalar_formatted_for_schema(value: Type[Scalar], *, number_of_indent=1) -> str:
    """
    Return a string showing how to configure a Scalar.

    :param int number_of_indent:
        How many indentations beyond the base should this schema have,
        useful for when used with other schema such as Dict.
    """
    block_indentation = BASE_INDENT + INDENT * number_of_indent
    return f"\n{block_indentation}value: number\n{block_indentation}unit: string"


def array_formatted_for_schema(value: Type[Array], *, number_of_indent=1) -> str:
    """
    Return a string showing how to configure a Array.

    :param int number_of_indent:
        How many indentations beyond the base should this schema have,
        useful for when used with other schema such as Dict.
    """
    block_indentation = BASE_INDENT + INDENT * number_of_indent
    return f"\n{block_indentation}values: [number]\n{block_indentation}unit: string"


def curve_formatted_for_schema(value: Type[Curve], *, number_of_indent=1) -> str:
    """
    Return a string showing how to configure a Array.

    :param int number_of_indent:
        How many indentations beyond the base should this schema have,
        useful for when used with other schema such as Dict.
    """
    block_indentation = BASE_INDENT + INDENT * number_of_indent
    array_schema = array_formatted_for_schema(
        Array, number_of_indent=number_of_indent + 1
    )
    return f"\n{block_indentation}image:{array_schema}\n{block_indentation}domain:{array_schema}"


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
    (is_curve, lambda value: _get_curve_reference()),
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
    (is_curve, curve_formatted_for_schema),
    (is_int, lambda value: "number"),
    (is_path, lambda value: value.__name__),
]
