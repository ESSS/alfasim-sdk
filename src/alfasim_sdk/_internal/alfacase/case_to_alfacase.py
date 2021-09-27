import math
from enum import Enum
from functools import partial
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import attr
import numpy as np
from barril.curve.curve import Curve
from barril.units import Array
from barril.units import Scalar

from alfasim_sdk import MultiInputType
from alfasim_sdk._internal import constants
from alfasim_sdk._internal.alfacase import case_description
from alfasim_sdk._internal.alfacase.generate_schema import IGNORED_PROPERTIES
from alfasim_sdk._internal.alfacase.generate_schema import is_attrs

ATTRIBUTES = Union[Scalar, Array, Curve, Enum, np.ndarray, List, List[Enum]]

NON_FININTE_VALUES_TO_STRING = [
    (math.isnan, ".nan"),
    (lambda value: math.isinf(value) and value > 0, ".inf"),
    (lambda value: math.isinf(value) and value < 0, "-.inf"),
]


def format_list(values: List[Any], *, enable_flow_style: bool = False):
    """
    This method marks specific nodes for dumping in flow mode,
    and everything "below" will then be dumped with flow-mode as well.

    This approach was intended to avoid to dump dictionary with curly brackets "{ }"
    and keep a list of strings with block style.

    For more details check:
    https://stackoverflow.com/questions/63364894/how-to-dump-only-lists-with-flow-style-with-pyyaml-or-ruamel-yaml
    """
    import ruamel

    retval = ruamel.yaml.comments.CommentedSeq(values)

    if enable_flow_style:
        retval.fa.set_flow_style()
    return retval


def _convert_value_to_valid_alfacase_format(
    value: ATTRIBUTES, enable_flow_style_on_numpy: bool
) -> Union[str, Dict[str, str], List[str], List[List[str]]]:
    """
    Returns an yaml convertible representation from the given equipment_attribute

    :param enable_flow_style_on_numpy:
        Signalize that numpy arrays should dumped with inline list ( pressure: [1, 2] ).
    """
    if isinstance(value, Scalar):
        return {"value": str(value.value), "unit": value.unit}

    if isinstance(value, Array):
        return {"values": [str(i) for i in value.values], "unit": value.unit}

    if isinstance(value, Curve):
        return {
            "image": _convert_value_to_valid_alfacase_format(
                value.image, enable_flow_style_on_numpy
            ),
            "domain": _convert_value_to_valid_alfacase_format(
                value.domain, enable_flow_style_on_numpy
            ),
        }

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, np.ndarray) and value.ndim == 1:
        return format_list(
            values=[str(coefficients) for coefficients in value],
            enable_flow_style=enable_flow_style_on_numpy,
        )

    if isinstance(value, list) and all(
        (isinstance(item, np.ndarray) and item.ndim == 1 for item in value)
    ):
        return [
            format_list(
                values=[str(np_value) for np_value in np_array],
                enable_flow_style=enable_flow_style_on_numpy,
            )
            for np_array in value
        ]

    if isinstance(value, list) and all((isinstance(item, Array) for item in value)):
        return [
            {"values": [str(i) for i in item.values], "unit": item.unit}
            for item in value
        ]

    if isinstance(value, list):
        return [str(i) for i in value]

    # YAML 1.2 specification uses `.nan` instead of `nan` and `.inf` instead of `inf`.
    if isinstance(value, float):
        for validator, fixed_value in NON_FININTE_VALUES_TO_STRING:
            if validator(value):
                float_formatted_value = fixed_value
                break
        else:
            float_formatted_value = str(value)

        return float_formatted_value

    return str(value)


def convert_dict_to_valid_alfacase_format(
    case_description_dict: Dict[str, ATTRIBUTES],
    *,
    enable_flow_style_on_numpy: bool,
    remove_redundant_input_type_data: bool = True,
) -> Dict[str, Any]:
    """
    Convert all values of the dictionary to string.

    Note.: strict_yaml only allows "str" values on all attributes in order to render the YAML content.

    :param enable_flow_style_on_numpy:
        Signalize that numpy arrays should dumped with inline list ( pressure: [1, 2] ).

    :param remove_redundant_input_type_data:
        For transient entries remove input type selector, and the unused constant or curve entries.
    """
    transient_fields: Dict[str, MultiInputType] = {}
    converted_dict = {}
    for key, value in case_description_dict.items():
        is_empty_dict = isinstance(value, dict) and not value
        ignore = key in IGNORED_PROPERTIES

        if is_empty_dict or value is None or ignore:
            continue

        if remove_redundant_input_type_data and isinstance(
            value, constants.MultiInputType
        ):
            assert key.endswith(constants.MULTI_INPUT_TYPE_SUFFIX)
            transient_fields[key] = value

        if is_attrs(value):

            to_dict = partial(attr.asdict, recurse=False)

            if isinstance(value, list):
                converted_value = [
                    convert_dict_to_valid_alfacase_format(
                        to_dict(i),
                        enable_flow_style_on_numpy=enable_flow_style_on_numpy,
                        remove_redundant_input_type_data=remove_redundant_input_type_data,
                    )
                    for i in value
                ]
            else:
                converted_value = convert_dict_to_valid_alfacase_format(
                    to_dict(value),
                    enable_flow_style_on_numpy=enable_flow_style_on_numpy,
                    remove_redundant_input_type_data=remove_redundant_input_type_data,
                )

            if converted_value:
                converted_dict[key] = converted_value
            continue

        if isinstance(value, dict):
            converted_dict[key] = convert_dict_to_valid_alfacase_format(
                value,
                enable_flow_style_on_numpy=enable_flow_style_on_numpy,
                remove_redundant_input_type_data=remove_redundant_input_type_data,
            )
            continue

        converted_dict[key] = _convert_value_to_valid_alfacase_format(
            value, enable_flow_style_on_numpy
        )

    if remove_redundant_input_type_data:
        for key, multi_input_type in transient_fields.items():
            constant_key = key[: -len(constants.MULTI_INPUT_TYPE_SUFFIX)]
            curve_key = f"{constant_key}_curve"

            converted_dict.pop(key, None)
            if multi_input_type == constants.MultiInputType.Constant:
                converted_dict.pop(curve_key, None)
            elif multi_input_type == constants.MultiInputType.Curve:
                converted_dict.pop(constant_key, None)
            else:  # pragma: no cover
                raise AssertionError(f"unexpected value {key}: {multi_input_type}")

    return converted_dict


EquipmentTypes = Union[
    case_description.MassSourceEquipmentDescription,
    case_description.HeatSourceEquipmentDescription,
    case_description.CompressorEquipmentDescription,
    case_description.ReservoirInflowEquipmentDescription,
    case_description.ValveEquipmentDescription,
    case_description.PumpEquipmentDescription,
    case_description.GasLiftValveEquipmentDescription,
    case_description.LeakEquipmentDescription,
    case_description.PigEquipmentDescription,
]
