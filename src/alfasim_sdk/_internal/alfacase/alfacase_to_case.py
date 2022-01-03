import enum
import inspect
from functools import lru_cache
from functools import partial
from numbers import Number
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

import attr
from attr.validators import instance_of
from barril.curve.curve import Curve
from barril.units import Array
from barril.units import Scalar
from barril.units import UnitDatabase
from strictyaml import YAML

from alfasim_sdk._internal import constants
from alfasim_sdk._internal.alfacase import case_description

T = TypeVar("T")


@attr.s
class DescriptionDocument:
    """
    A class to hold information from the Alfacase file loaded.

    :ivar strictyaml.YAML content:
        YAML object with the parsed content from the ALfacase file, (access trough .data)

    :ivar Path file_path:
        Path to the alfacase file loaded.
    """

    content = attr.ib(type=YAML)
    file_path = attr.ib(type=Path, validator=instance_of(Path))

    def __getitem__(self, key: str) -> "DescriptionDocument":
        return DescriptionDocument(self.content[key], self.file_path)

    def __contains__(self, item: str) -> bool:
        return item in self.content

    @classmethod
    def from_file(cls, file_path: Path) -> "DescriptionDocument":
        """
        Load the values from the given file_path validating against the Schema defined on
        alfacase.schema.case_schema
        """
        import strictyaml

        from alfasim_sdk._internal.alfacase.case_description_attributes import (
            DescriptionError,
        )
        from alfasim_sdk._internal.alfacase.schema import case_description_schema

        try:
            content = strictyaml.dirty_load(
                yaml_string=Path(file_path).read_text(encoding="UTF-8"),
                schema=case_description_schema,
                allow_flow_style=True,
            )
        except strictyaml.YAMLValidationError as e:
            raise DescriptionError(str(e))

        return cls(content, file_path)


@lru_cache(maxsize=None)
def get_category_for(unit: Optional[str]) -> Optional[str]:
    """
    Return the default category for the given unit
    """
    if unit:
        return UnitDatabase.GetSingleton().GetDefaultCategory(unit)


def update_multi_input_flags(document: DescriptionDocument, item_description: T) -> T:
    """
    Update the multi input flags in `item_description` if not present in `alfacase_content` and
    can be unambiguously deduced from the presence of constant and transient inputs. If deduction
    is ambiguous or value is already correct, nothing is changed (no-op).

    :returns: The updated `item_description` (can return `item_description` unchanged).
    """
    item_attr_dict = attr.asdict(item_description, recurse=False)
    fields_to_update: Dict[str, constants.MultiInputType] = {}
    for key, value in item_attr_dict.items():
        is_set_in_alfacase = key in document
        if (not is_set_in_alfacase) and isinstance(value, constants.MultiInputType):
            assert key.endswith(constants.MULTI_INPUT_TYPE_SUFFIX)

            constant_key = key[: -len(constants.MULTI_INPUT_TYPE_SUFFIX)]
            has_constant_data = constant_key in document

            curve_key = f"{constant_key}_curve"
            has_curve_data = curve_key in document

            new_value: Optional[constants.MultiInputType] = None
            if has_constant_data and not has_curve_data:
                new_value = constants.MultiInputType.Constant
            elif has_curve_data and not has_constant_data:
                new_value = constants.MultiInputType.Curve

            if (new_value is not None) and (
                getattr(item_description, key) != new_value
            ):
                fields_to_update[key] = new_value

    if fields_to_update:
        item_description = attr.evolve(item_description, **fields_to_update)
    return item_description


def load_instance(alfacase_content: DescriptionDocument, class_: Type[T]) -> T:
    """
    Create an instance of class_ with the attributes found in alfacase_content.
    """
    alfacase_to_case_description = get_case_description_attribute_loader_dict(class_)
    case_values = to_case_values(alfacase_content, alfacase_to_case_description)
    item_description = class_(**case_values)
    return update_multi_input_flags(alfacase_content, item_description)


@lru_cache(maxsize=None)
def get_instance_loader(*, class_: type) -> Callable:
    """
    Return a load instance function pre-populate with the class_.
    """
    return partial(load_instance, class_=class_)


def load_dict_of_instance(alfacase_content: DescriptionDocument, class_: Type[T]) -> T:
    return {
        key.data: load_instance(
            DescriptionDocument(value, alfacase_content.file_path), class_=class_
        )
        for key, value in alfacase_content.content.items()
    }


@lru_cache(maxsize=None)
def get_dict_of_instance_loader(*, class_: type) -> Callable:
    return partial(load_dict_of_instance, class_=class_)


def get_case_description_attribute_loader_dict(
    class_: Any, explicit_loaders: Optional[Dict[str, Callable]] = None
) -> Dict[str, Callable]:
    """
    Create a dict of loaders to be used with `to_case_values`.

    Loaders are created for all attributes (``attr.id``) in ``class_``.
    If ``explicit_loaders`` are supplied those loaders are used instead of the
    automatically generated ones.
    """
    loaders: Dict[str, Callable] = (
        {} if explicit_loaders is None else explicit_loaders.copy()
    )

    for attr_instance in attr.fields(class_):
        name = attr_instance.name
        if name in loaders:
            continue

        metadata = attr_instance.metadata
        if "type" in metadata:
            kwargs = metadata.copy()
            type_ = kwargs.pop("type")
            loader_getter_name = f"get_{type_}_loader"
            loader = globals()[loader_getter_name]
            loaders[name] = loader(**kwargs)
            continue

        loaders[name] = load_value

    return loaders


def load_scalar(
    key: str, alfacase_content: DescriptionDocument, category: str
) -> Scalar:
    """
    Create a barril.units.Scalar instance from the given alfacase_content.
    # TODO: ASIM-3556: All atributes from this module should get the category from the CaseDescription
    """
    return Scalar(
        category,
        alfacase_content[key]["value"].content.data,
        alfacase_content[key]["unit"].content.data,
    )


@lru_cache(maxsize=None)
def get_scalar_loader(
    *, category: Optional[str] = None, from_unit: Optional[str] = None
) -> Callable:
    """
    Return a LoadArray function pre-populate with the category

    If ``from_unit`` is provided, the category parameter will be filled with
    the default category for the given unit.
    """
    return partial(
        load_scalar, category=_obtain_category_for_scalar(category, from_unit)
    )


def load_array(key: str, alfacase_content: DescriptionDocument, category: str) -> Array:
    """
    Create a barril.units.Array instance from the given YAML content.
    # TODO: ASIM-3556: All atributes from this module should get the category from the CaseDescription
    """
    return Array(
        category,
        alfacase_content[key]["values"].content.data,
        alfacase_content[key]["unit"].content.data,
    )


@lru_cache(maxsize=None)
def get_array_loader(
    *, category: Optional[str] = None, from_unit: Optional[str] = None
) -> Callable:
    """
    Return a LoadArray function pre-populate with the category

    If ``from_unit`` is provided, the category parameter will be filled with
    the default category for the given unit.
    """
    return partial(
        load_array, category=_obtain_category_for_scalar(category, from_unit)
    )


def load_list_of_arrays(
    key: str,
    alfacase_content: DescriptionDocument,
    category: str,
) -> List[Array]:
    """
    Create a barril.units.Array instance from the given YAML content.
    # TODO: ASIM-3556: All atributes from this module should get the category from the CaseDescription
    """
    return [
        Array(category, entry.content.data["values"], entry.content.data["unit"])
        for entry in alfacase_content[key]
    ]


@lru_cache(maxsize=None)
def get_list_of_arrays_loader(
    *, category: Optional[str] = None, from_unit: Optional[str] = None
) -> Callable:
    """
    Return a LoadListOfArrays function pre-populated with the category

    If ``from_unit`` is provided, the category parameter will be filled with
    the default category for the given unit.
    """
    return partial(
        load_list_of_arrays, category=_obtain_category_for_scalar(category, from_unit)
    )


def load_dict_of_arrays(
    key: str,
    alfacase_content: DescriptionDocument,
    category: str,
) -> Dict[str, Array]:
    """
    Create a Dict of str to barril.units.Array instances from the given YAML content.
    # TODO: ASIM-3556: All atributes from this module should get the category from the CaseDescription
    """
    return {
        k: Array(category, v["values"], v["unit"])
        for k, v in alfacase_content[key].content.data.items()
    }


@lru_cache(maxsize=None)
def get_dict_of_arrays_loader(
    *, category: Optional[str] = None, from_unit: Optional[str] = None
) -> Callable:
    """
    Return a LoadDictOfArrays function pre-populated with the category

    If ``from_unit`` is provided, the category parameter will be filled with
    the default category for the given unit.
    """
    return partial(
        load_dict_of_arrays, category=_obtain_category_for_scalar(category, from_unit)
    )


def load_curve(key: str, alfacase_content: DescriptionDocument, category: str) -> Curve:
    """
    Create a barril.curve.curve.Curve instance from the given YAML content.
    # TODO: ASIM-3556: All atributes from this module should get the category from the CaseDescription
    """
    curve_in_alfacase = alfacase_content[key]
    return Curve(
        load_array("image", curve_in_alfacase, category),
        load_array("domain", curve_in_alfacase, "time"),
    )


@lru_cache(maxsize=None)
def get_curve_loader(
    *, category: Optional[str] = None, from_unit: Optional[str] = None
) -> Callable:
    """
    Return a load_curve function pre-populated with the category

    If ``from_unit`` is provided, the category parameter will be filled with
    the default category for the given unit.
    """
    return partial(
        load_curve, category=_obtain_category_for_scalar(category, from_unit)
    )


def load_dict_of_curves(
    key: str, alfacase_content: DescriptionDocument, category: str
) -> Dict[str, Curve]:
    """
    Create a Dict of str to barril.curve.curve.Curve instances from the given YAML content.
    # TODO: ASIM-3556: All atributes from this module should get the category from the CaseDescription
    """
    curve_dict_in_alfacase = alfacase_content[key]
    return {
        k: load_curve(k, curve_dict_in_alfacase, category)
        for k in curve_dict_in_alfacase.content.data.keys()
    }


@lru_cache(maxsize=None)
def get_curve_dict_loader(
    *, category: Optional[str] = None, from_unit: Optional[str] = None
) -> Callable:
    """
    Return a load_dict_of_curves function pre-populated with the category

    If ``from_unit`` is provided, the category parameter will be filled with
    the default category for the given unit.
    """
    return partial(
        load_dict_of_curves, category=_obtain_category_for_scalar(category, from_unit)
    )


def _obtain_category_for_scalar(category: str, from_unit: str) -> str:
    """
    Obtain the category to be used for GetArrayLoader and GetScalarLoader.

    Raises ValueError with either category and from_unit are defined, and also raises ValueError if
    neither category or from_unit are defined.
    """
    if category is not None and from_unit is not None:
        raise ValueError(
            "Both parameters 'category' and 'from_unit' were provided, only one must be informed"
        )
    if category is None and from_unit is None:
        raise ValueError("Either 'category' or 'from_unit' parameter must be defined")

    return category or get_category_for(from_unit)


def load_dict_with_scalar(
    key: str,
    alfacase_content: DescriptionDocument,
    category: str,
) -> Dict[str, Scalar]:
    return {
        key: Scalar(category, value["value"], value["unit"])
        for key, value in alfacase_content[key].content.data.items()
    }


def get_scalar_dict_loader(*, category: str) -> Callable:
    """
    Return a LoadDictWithScalar function pre-populate with the category
    """
    return partial(load_dict_with_scalar, category=category)


def load_enum(
    key: str, alfacase_content: DescriptionDocument, enum_class: Type[enum.Enum]
) -> enum.Enum:
    """
    Return the PythonEnum equivalent from the yaml content
    """
    enum_value = alfacase_content[key].content.data

    return enum_class(enum_value)


def get_enum_loader(*, enum_class: enum.EnumMeta) -> Callable:
    """
    Return a LoadEnum function pre-populated with the enum_class
    """
    return partial(load_enum, enum_class=enum_class)


def load_value(
    key: str, alfacase_content: DescriptionDocument
) -> Union[str, Number, list, dict]:
    """
    Loads a python builtin value such as str, int, float, bool, etc
    """
    return alfacase_content[key].content.data


def load_path(key: str, alfacase_content: DescriptionDocument) -> Path:
    path_from_alfacase_file = Path(alfacase_content[key].content.data)
    return (
        path_from_alfacase_file
        if path_from_alfacase_file.is_absolute()
        else alfacase_content.file_path.parent / path_from_alfacase_file
    )


PvtModelTable = str
PvtModels = Union[
    PvtModelTable,
    case_description.PvtModelCompositionalDescription,
    case_description.PvtModelCorrelationDescription,
]


def load_pvt_tables(alfacase_content: DescriptionDocument) -> Dict[str, Path]:
    def get_table_file(value):
        """
        Value can be:
        - An absolute path
        - A relative path

        Either option accepts a way to inform which PVTModel from the file should be used,
        to cover cases where multiples PvtModels are available inside a single tab file.
        """
        (
            pvt_file,
            model_name,
        ) = case_description.PvtModelsDescription.get_pvt_file_and_model_name(value)

        def append_pvt_model_name_if_defined(file_path: Path) -> Path:
            """
            Append "<path_name>" on the "<tab_file_path>" if the model_name is specified.
            """
            return Path(f"{file_path}|{model_name}") if model_name else file_path

        pvt_path = (
            pvt_file
            if pvt_file.is_absolute()
            else alfacase_content.file_path.parent / pvt_file
        )

        if pvt_path.is_file():
            return Path(append_pvt_model_name_if_defined(pvt_path))
        else:
            raise RuntimeError(
                f"The PVT Table {value} must be place within the "
                f"{alfacase_content.file_path.name} file on {str(alfacase_content.file_path.parent)}"
            )

    return {
        key.data: get_table_file(value.data)
        for key, value in alfacase_content.content.items()
    }


def load_pvt_model_correlation_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.PvtModelCorrelationDescription]:
    alfacase_to_case_description = {
        "oil_density_std": get_scalar_loader(from_unit="kg/m3"),
        "gas_density_std": get_scalar_loader(from_unit="kg/m3"),
        "rs_sat": get_scalar_loader(from_unit="sm3/sm3"),
        "pvt_correlation_package": get_enum_loader(
            enum_class=constants.CorrelationPackage
        ),
    }

    def generate_pvt_model_correlation(
        value: DescriptionDocument,
    ) -> case_description.PvtModelCorrelationDescription:
        case_values = to_case_values(value, alfacase_to_case_description)
        item_description = case_description.PvtModelCorrelationDescription(
            **case_values
        )
        return update_multi_input_flags(document, item_description)

    return {
        key.data: generate_pvt_model_correlation(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def load_heavy_component_description(
    document: DescriptionDocument,
) -> List[case_description.HeavyComponentDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "scn": load_value,
        "MW": get_scalar_loader(from_unit="kg/mol"),
        "rho": get_scalar_loader(from_unit="kg/m3"),
    }

    def generate_heavy_components_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.HeavyComponentDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_heavy_components_description(alfacase_document)
        for alfacase_document in document
    ]


def load_light_component_description(
    document: DescriptionDocument,
) -> List[case_description.LightComponentDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "Pc": get_scalar_loader(from_unit="Pa"),
        "Tc": get_scalar_loader(from_unit="K"),
        "Vc": get_scalar_loader(from_unit="m3/mol"),
        "omega": get_scalar_loader(from_unit="-"),
        "MW": get_scalar_loader(from_unit="kg/mol"),
        "Tb": get_scalar_loader(from_unit="K"),
        "Parachor": get_scalar_loader(from_unit="-"),
        "Cp_0": get_scalar_loader(from_unit="-"),
        "Cp_1": get_scalar_loader(from_unit="-"),
        "Cp_2": get_scalar_loader(from_unit="-"),
        "Cp_3": get_scalar_loader(from_unit="-"),
        "Cp_4": get_scalar_loader(from_unit="-"),
    }

    def generate_light_components_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.LightComponentDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_light_components_description(alfacase_document)
        for alfacase_document in document
    ]


def load_bip_description(
    document: DescriptionDocument,
) -> List[case_description.BipDescription]:
    alfacase_to_case_description = {
        "component_1": load_value,
        "component_2": load_value,
        "value": load_value,
    }

    def generate_bip_description(alfacase_document: DescriptionDocument):
        case_values = to_case_values(alfacase_document, alfacase_to_case_description)
        item_description = case_description.BipDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_bip_description(alfacase_document) for alfacase_document in document
    ]


def load_composition_description(
    document: DescriptionDocument,
) -> List[case_description.CompositionDescription]:
    alfacase_to_case_description = {
        "component": load_value,
        "molar_fraction": get_scalar_loader(from_unit="mol/mol"),
        "reference_enthalpy": get_scalar_loader(from_unit="J/mol"),
    }

    def generate_composition_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.CompositionDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_composition_description(alfacase_document)
        for alfacase_document in document
    ]


def load_fluid_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.FluidDescription]:
    alfacase_to_case_description = {
        "composition": load_composition_description,
        "fraction_pairs": load_bip_description,
    }

    def generate_fluid_description(
        value: DescriptionDocument,
    ) -> case_description.FluidDescription:
        case_values = to_case_values(value, alfacase_to_case_description)
        item_description = case_description.FluidDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return {
        key.data: generate_fluid_description(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def load_pvt_model_compositional_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.PvtModelCompositionalDescription]:
    alfacase_to_case_description = {
        "equation_of_state_type": get_enum_loader(
            enum_class=constants.EquationOfStateType
        ),
        "surface_tension_model_type": get_enum_loader(
            enum_class=constants.SurfaceTensionType
        ),
        "viscosity_model": get_enum_loader(
            enum_class=constants.PVTCompositionalViscosityModel
        ),
        "heavy_components": load_heavy_component_description,
        "light_components": load_light_component_description,
        "fluids": load_fluid_description,
    }

    def generate_pvt_model_compositional(value: DescriptionDocument):
        case_values = to_case_values(value, alfacase_to_case_description)
        item_description = case_description.PvtModelCompositionalDescription(
            **case_values
        )
        return update_multi_input_flags(document, item_description)

    return {
        key.data: generate_pvt_model_compositional(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def load_pvt_models_description(
    document: DescriptionDocument,
) -> case_description.PvtModelsDescription:
    alfacase_to_case_description = {
        "default_model": load_value,
        "tables": load_pvt_tables,
        "correlations": load_pvt_model_correlation_description,
        "compositions": load_pvt_model_compositional_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.PvtModelsDescription(**case_values)
    return update_multi_input_flags(document, item_description)


# Used for testing - Will be ignored on the document contents
IGNORE_KEY = "IgnoreKey"


def to_case_values(
    document: DescriptionDocument,
    alfacase_to_case_description_dict: Dict[str, Callable],
) -> Dict[str, Any]:
    """
    Function that return a dictionary with the attributes and their respective values on CaseDescription domain.

    :param document:
        The DescriptionDocument object, with the value loaded from YAML file
    :param alfacase_to_case_description_dict:
        Dictionary with pairs attribute_name:loader_function to convert the values from YAML content
        to case description domain.
    """
    alfacase_to_case_description = {}
    for attr_name, function_handle in alfacase_to_case_description_dict.items():
        if attr_name in document:
            alfacase_to_case_description[attr_name] = execute_loader(
                attr_name, function_handle, document
            )

    return alfacase_to_case_description


def execute_loader(
    attr_name: str, loader_function: Callable, alfacase_content: YAML
) -> Any:
    """
    Execute the loader function passing the YAML content, and return the value converted
    """
    is_a_description_loader = len(inspect.getfullargspec(loader_function).args) == 1

    if is_a_description_loader:
        return loader_function(alfacase_content[attr_name])
    else:
        return loader_function(key=attr_name, alfacase_content=alfacase_content)


def load_casing_section_description(
    document: DescriptionDocument,
) -> List[case_description.CasingSectionDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "hanger_depth": get_scalar_loader(from_unit="m"),
        "settings_depth": get_scalar_loader(from_unit="m"),
        "hole_diameter": get_scalar_loader(category="diameter"),
        "outer_diameter": get_scalar_loader(category="diameter"),
        "inner_diameter": get_scalar_loader(category="diameter"),
        "inner_roughness": get_scalar_loader(from_unit="m"),
        "material": load_value,
        "top_of_filler": get_scalar_loader(from_unit="m"),
        "filler_material": load_value,
        "material_above_filler": load_value,
    }

    def generate_casing_section_description(document: DescriptionDocument):
        case_content = to_case_values(document, alfacase_to_case_description)
        return case_description.CasingSectionDescription(**case_content)

    return [
        generate_casing_section_description(alfacase_document)
        for alfacase_document in document
    ]


def load_environment_property_description(
    document: DescriptionDocument,
) -> List[case_description.EnvironmentPropertyDescription]:
    # fmt: off
    alfacase_to_case_description = {
        'type': get_enum_loader(enum_class=constants.PipeEnvironmentHeatTransferCoefficientModelType),
        'position': get_scalar_loader(from_unit='m'),
        'temperature': get_scalar_loader(from_unit='degC'),
        'heat_transfer_coefficient': get_scalar_loader(from_unit='W/m2.K'),
        'overall_heat_transfer_coefficient': get_scalar_loader(from_unit='W/m2.K'),
        'fluid_velocity': get_scalar_loader(from_unit='m/s'),
    }

    # fmt: on
    def generate_environment_property_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.EnvironmentPropertyDescription(
            **case_values
        )
        return update_multi_input_flags(document, item_description)

    return [
        generate_environment_property_description(alfacase_document)
        for alfacase_document in document
    ]


def load_formation_layer_description(
    document: DescriptionDocument,
) -> List[case_description.FormationLayerDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "start": get_scalar_loader(from_unit="m"),
        "material": load_value,
    }

    def generate_formation_layer_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.FormationLayerDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_formation_layer_description(alfacase_document)
        for alfacase_document in document
    ]


def load_gas_lift_valve_equipment_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.GasLiftValveEquipmentDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "position": get_scalar_loader(from_unit="m"),
        "diameter": get_scalar_loader(category="diameter"),
        "valve_type": get_enum_loader(enum_class=constants.ValveType),
        "delta_p_min": get_scalar_loader(from_unit="Pa"),
        "discharge_coefficient": get_scalar_loader(from_unit="-"),
    }

    def generate_gas_lift_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.GasLiftValveEquipmentDescription(
            **case_values
        )
        return update_multi_input_flags(document, item_description)

    return {
        key.data: generate_gas_lift_description(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def load_heat_source_equipment_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.HeatSourceEquipmentDescription]:
    alfacase_to_case_description = get_case_description_attribute_loader_dict(
        case_description.HeatSourceEquipmentDescription
    )

    def generate_heat_source_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.HeatSourceEquipmentDescription(
            **case_values
        )
        return update_multi_input_flags(document, item_description)

    return {
        key.data: generate_heat_source_description(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def get_initial_conditions_table_loader(
    table_class, attr_name, attr_unit, *, is_referenced, is_multidimensional
):
    if is_multidimensional:
        attr_loader = get_dict_of_arrays_loader(from_unit=attr_unit)
    else:
        attr_loader = get_array_loader(from_unit=attr_unit)

    def load_initial_conditions_table(document: DescriptionDocument):
        alfacase_to_case_description = {
            "positions": get_array_loader(from_unit="m"),
            attr_name: attr_loader,
        }
        if is_referenced:
            alfacase_to_case_description["reference_coordinate"] = get_scalar_loader(
                from_unit="m"
            )
        case_values = to_case_values(document, alfacase_to_case_description)
        return table_class(**case_values)

    return load_initial_conditions_table


def get_tracers_initial_conditions_table_loader(
    table_class, attr_name, attr_unit, *, is_referenced
):
    attr_loader = get_list_of_arrays_loader(from_unit=attr_unit)

    def load_initial_conditions_table(document: DescriptionDocument):
        alfacase_to_case_description = {
            "positions": get_array_loader(from_unit="m"),
            attr_name: attr_loader,
        }
        if is_referenced:
            alfacase_to_case_description["reference_coordinate"] = get_scalar_loader(
                from_unit="m"
            )
        case_values = to_case_values(document, alfacase_to_case_description)
        return table_class(**case_values)

    return load_initial_conditions_table


load_referenced_velocities_container_description = get_initial_conditions_table_loader(
    case_description.ReferencedVelocitiesContainerDescription,
    "velocities",
    "m/s",
    is_referenced=True,
    is_multidimensional=True,
)
load_velocities_container_description = get_initial_conditions_table_loader(
    case_description.VelocitiesContainerDescription,
    "velocities",
    "m/s",
    is_referenced=False,
    is_multidimensional=True,
)


def load_initial_velocities_description(
    document: DescriptionDocument,
) -> case_description.InitialVelocitiesDescription:
    alfacase_to_case_description = {
        "position_input_type": get_enum_loader(enum_class=constants.TableInputType),
        "table_x": load_referenced_velocities_container_description,
        "table_y": load_referenced_velocities_container_description,
        "table_length": load_velocities_container_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.InitialVelocitiesDescription(**case_values)
    return update_multi_input_flags(document, item_description)


load_referenced_temperatures_container_description = (
    get_initial_conditions_table_loader(
        case_description.ReferencedTemperaturesContainerDescription,
        "temperatures",
        "K",
        is_referenced=True,
        is_multidimensional=False,
    )
)
load_temperatures_container_description = get_initial_conditions_table_loader(
    case_description.TemperaturesContainerDescription,
    "temperatures",
    "K",
    is_referenced=False,
    is_multidimensional=False,
)


def load_initial_temperatures_description(
    document: DescriptionDocument,
) -> case_description.InitialTemperaturesDescription:
    alfacase_to_case_description = {
        "position_input_type": get_enum_loader(enum_class=constants.TableInputType),
        "table_x": load_referenced_temperatures_container_description,
        "table_y": load_referenced_temperatures_container_description,
        "table_length": load_temperatures_container_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.InitialTemperaturesDescription(**case_values)
    return update_multi_input_flags(document, item_description)


load_referenced_volume_fractions_container_description = (
    get_initial_conditions_table_loader(
        case_description.ReferencedVolumeFractionsContainerDescription,
        "fractions",
        "-",
        is_referenced=True,
        is_multidimensional=True,
    )
)
load_volume_fractions_container_description = get_initial_conditions_table_loader(
    case_description.VolumeFractionsContainerDescription,
    "fractions",
    "-",
    is_referenced=False,
    is_multidimensional=True,
)


def load_initial_volume_fractions_description(
    document: DescriptionDocument,
) -> case_description.InitialVolumeFractionsDescription:
    alfacase_to_case_description = {
        "position_input_type": get_enum_loader(enum_class=constants.TableInputType),
        "table_x": load_referenced_volume_fractions_container_description,
        "table_y": load_referenced_volume_fractions_container_description,
        "table_length": load_volume_fractions_container_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.InitialVolumeFractionsDescription(**case_values)
    return update_multi_input_flags(document, item_description)


load_referenced_pressure_container_description = get_initial_conditions_table_loader(
    case_description.ReferencedPressureContainerDescription,
    "pressures",
    "Pa",
    is_referenced=True,
    is_multidimensional=False,
)
load_pressure_container_description = get_initial_conditions_table_loader(
    case_description.PressureContainerDescription,
    "pressures",
    "Pa",
    is_referenced=False,
    is_multidimensional=False,
)


def load_initial_pressures_description(
    document: DescriptionDocument,
) -> case_description.InitialPressuresDescription:
    alfacase_to_case_description = {
        "position_input_type": get_enum_loader(enum_class=constants.TableInputType),
        "table_x": load_referenced_pressure_container_description,
        "table_y": load_referenced_pressure_container_description,
        "table_length": load_pressure_container_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.InitialPressuresDescription(**case_values)
    return update_multi_input_flags(document, item_description)


load_referenced_tracers_mass_fractions_container_description = (
    get_tracers_initial_conditions_table_loader(
        case_description.ReferencedTracersMassFractionsContainerDescription,
        "tracers_mass_fractions",
        "-",
        is_referenced=True,
    )
)
load_tracers_mass_fractions_container_description = (
    get_tracers_initial_conditions_table_loader(
        case_description.TracersMassFractionsContainerDescription,
        "tracers_mass_fractions",
        "-",
        is_referenced=False,
    )
)


def load_initial_tracers_mass_fractions_description(
    document: DescriptionDocument,
) -> case_description.InitialTracersMassFractionsDescription:
    alfacase_to_case_description = {
        "position_input_type": get_enum_loader(enum_class=constants.TableInputType),
        "table_x": load_referenced_tracers_mass_fractions_container_description,
        "table_y": load_referenced_tracers_mass_fractions_container_description,
        "table_length": load_tracers_mass_fractions_container_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.InitialTracersMassFractionsDescription(
        **case_values
    )
    return update_multi_input_flags(document, item_description)


def load_initial_conditions_description(
    document: DescriptionDocument,
) -> case_description.InitialConditionsDescription:
    alfacase_to_case_description = {
        "velocities": load_initial_velocities_description,
        "temperatures": load_initial_temperatures_description,
        "volume_fractions": load_initial_volume_fractions_description,
        "pressures": load_initial_pressures_description,
        "tracers_mass_fractions": load_initial_tracers_mass_fractions_description,
        "fluid": load_value,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.InitialConditionsDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def _load_mass_source_common() -> Dict[str, Callable]:
    return get_case_description_attribute_loader_dict(
        case_description._MassSourceCommon
    )


def load_mass_source_equipment_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.MassSourceEquipmentDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "position": get_scalar_loader(from_unit="m"),
        "material_above_filler": load_value,
    }
    alfacase_to_case_description.update(**_load_mass_source_common())

    def generate_mass_source_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.MassSourceEquipmentDescription(
            **case_values
        )
        return update_multi_input_flags(document, item_description)

    return {
        key.data: generate_mass_source_description(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def load_material_description(
    document: DescriptionDocument,
) -> List[case_description.MaterialDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "material_type": get_enum_loader(enum_class=constants.MaterialType),
        "density": get_scalar_loader(from_unit="kg/m3"),
        "heat_capacity": get_scalar_loader(from_unit="J/kg.degC"),
        "thermal_conductivity": get_scalar_loader(from_unit="W/m.degC"),
        "inner_emissivity": get_scalar_loader(category="emissivity"),
        "outer_emissivity": get_scalar_loader(category="emissivity"),
        "expansion": get_scalar_loader(from_unit="1/K"),
        "viscosity": get_scalar_loader(from_unit="cP"),
    }

    def generate_materials_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.MaterialDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_materials_description(alfacase_document)
        for alfacase_document in document
    ]


def load_internal_node_properties_description(
    document: DescriptionDocument,
) -> case_description.InternalNodePropertiesDescription:
    alfacase_to_case_description = {"fluid": load_value}
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.InternalNodePropertiesDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_mass_source_node_properties_description(
    document: DescriptionDocument,
) -> case_description.MassSourceNodePropertiesDescription:
    case_values = to_case_values(document, _load_mass_source_common())
    item_description = case_description.MassSourceNodePropertiesDescription(
        **case_values
    )
    return update_multi_input_flags(document, item_description)


def load_pressure_node_properties_description(
    document: DescriptionDocument,
) -> case_description.PressureNodePropertiesDescription:
    case_values = to_case_values(document, _load_pressure_source_common())
    item_description = case_description.PressureNodePropertiesDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_separator_node_properties_description(
    document: DescriptionDocument,
) -> case_description.SeparatorNodePropertiesDescription:
    alfacase_to_case_description = {
        "environment_temperature": get_scalar_loader(from_unit="K"),
        "geometry": get_enum_loader(enum_class=constants.SeparatorGeometryType),
        "length": get_scalar_loader(from_unit="m"),
        "overall_heat_transfer_coefficient": get_scalar_loader(from_unit="W/m2.K"),
        "diameter": get_scalar_loader(category="diameter"),
        "nozzles": get_scalar_dict_loader(category=get_category_for("m")),
        "initial_phase_volume_fractions": get_scalar_dict_loader(
            category="volume fraction"
        ),
        "gas_separation_efficiency": get_scalar_loader(from_unit="%"),
        "liquid_separation_efficiency": get_scalar_loader(from_unit="%"),
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.SeparatorNodePropertiesDescription(
        **case_values
    )
    return update_multi_input_flags(document, item_description)


def load_node_description(
    document: DescriptionDocument,
) -> List[case_description.NodeDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "node_type": get_enum_loader(enum_class=constants.NodeCellType),
        "pvt_model": load_value,
        "pressure_properties": load_pressure_node_properties_description,
        "mass_source_properties": load_mass_source_node_properties_description,
        "internal_properties": load_internal_node_properties_description,
        "separator_properties": load_separator_node_properties_description,
    }

    def generate_node_description(
        document: DescriptionDocument,
    ) -> case_description.NodeDescription:
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.NodeDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_node_description(alfacase_document) for alfacase_document in document
    ]


def load_packer_description(
    document: DescriptionDocument,
) -> List[case_description.PackerDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "position": get_scalar_loader(from_unit="m"),
        "material_above": load_value,
    }

    def generate_packer_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.PackerDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_packer_description(alfacase_document) for alfacase_document in document
    ]


def load_pipe_segments_description(
    document: DescriptionDocument,
) -> case_description.PipeSegmentsDescription:
    alfacase_to_case_description = {
        "start_positions": get_array_loader(from_unit="m"),
        "diameters": get_array_loader(from_unit="m"),
        "roughnesses": get_array_loader(from_unit="m"),
        "wall_names": load_value,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.PipeSegmentsDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_profile_output_description(
    document: DescriptionDocument,
) -> List[case_description.ProfileOutputDescription]:
    alfacase_to_case_description = {
        "curve_names": load_value,
        "element_name": load_value,
        "location": get_enum_loader(enum_class=constants.OutputAttachmentLocation),
    }

    def generate_profile_definitions(
        document: DescriptionDocument,
    ) -> case_description.ProfileOutputDescription:
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.ProfileOutputDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_profile_definitions(alfacase_document)
        for alfacase_document in document
    ]


def load_linear_ipr_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.LinearIPRDescription]:
    alfacase_to_case_description = get_case_description_attribute_loader_dict(
        case_description.LinearIPRDescription
    )

    def generate_linear_ipr_correlation(value: DescriptionDocument):
        case_values = to_case_values(value, alfacase_to_case_description)
        item_description = case_description.LinearIPRDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return {
        key.data: generate_linear_ipr_correlation(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def load_ipr_curve_description(
    document: DescriptionDocument,
) -> case_description.IPRCurveDescription:
    alfacase_to_case_description = {
        "pressure_difference": get_array_loader(from_unit="Pa"),
        "flow_rate": get_array_loader(from_unit="sm3/d"),
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.IPRCurveDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_table_ipr_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.LinearIPRDescription]:
    alfacase_to_case_description = {
        "well_index_phase": get_enum_loader(enum_class=constants.WellIndexPhaseType),
        "table": load_ipr_curve_description,
    }

    def generate_table_ipr_correlation(value: DescriptionDocument):
        case_values = to_case_values(value, alfacase_to_case_description)
        item_description = case_description.TableIPRDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return {
        key.data: generate_table_ipr_correlation(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def load_ipr_models_description(
    document: DescriptionDocument,
) -> case_description.IPRModelsDescription:
    alfacase_to_case_description = {
        "linear_models": load_linear_ipr_description,
        "table_models": load_table_ipr_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.IPRModelsDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def _load_pressure_source_common() -> Dict[str, Callable]:
    return get_case_description_attribute_loader_dict(
        case_description._PressureSourceCommon
    )


def load_reservoir_inflow_equipment_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.ReservoirInflowEquipmentDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "fluid": load_value,
        "start": get_scalar_loader(from_unit="m"),
        "length": get_scalar_loader(from_unit="m"),
        "pressure": get_scalar_loader(from_unit="bar"),
        "temperature": get_scalar_loader(from_unit="degC"),
        "productivity_ipr": load_value,
        "injectivity_ipr": load_value,
        "tracer_mass_fraction": get_array_loader(category="mass fraction"),
    }
    alfacase_to_case_description.update(**_load_pressure_source_common())

    def generate_reservoir_inflow_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.ReservoirInflowEquipmentDescription(
            **case_values
        )
        return update_multi_input_flags(document, item_description)

    return {
        key.data: generate_reservoir_inflow_description(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def load_speed_curve_description(
    document: DescriptionDocument,
) -> case_description.SpeedCurveDescription:
    alfacase_to_case_description = {
        "time": get_array_loader(from_unit="s"),
        "speed": get_array_loader(from_unit="rpm"),
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.SpeedCurveDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_table_pump_description(
    document: DescriptionDocument,
) -> case_description.TablePumpDescription:
    alfacase_to_case_description = {
        "speeds": get_array_loader(from_unit="rpm"),
        "void_fractions": get_array_loader(category="volume fraction"),
        "flow_rates": get_array_loader(category="volume flow rate"),
        "pressure_boosts": get_array_loader(from_unit="bar"),
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.TablePumpDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def generate_trend_description(
    document: DescriptionDocument,
    alfacase_to_case_description: Dict[str, Callable],
    description_type: [T],
) -> [T]:
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = description_type(**case_values)
    return update_multi_input_flags(document, item_description)


def load_positional_pipe_trend_description(
    document: DescriptionDocument,
) -> List[case_description.PositionalPipeTrendDescription]:
    alfacase_to_case_description = get_case_description_attribute_loader_dict(
        case_description.PositionalPipeTrendDescription
    )
    return [
        generate_trend_description(
            alfacase_document,
            alfacase_to_case_description,
            case_description.PositionalPipeTrendDescription,
        )
        for alfacase_document in document
    ]


def load_equipment_trend_description(
    document: DescriptionDocument,
) -> List[case_description.EquipmentTrendDescription]:
    alfacase_to_case_description = {
        "curve_names": load_value,
        "element_name": load_value,
    }
    return [
        generate_trend_description(
            alfacase_document,
            alfacase_to_case_description,
            case_description.EquipmentTrendDescription,
        )
        for alfacase_document in document
    ]


def load_separator_trend_description(
    document: DescriptionDocument,
) -> List[case_description.SeparatorTrendDescription]:
    alfacase_to_case_description = {
        "curve_names": load_value,
        "element_name": load_value,
    }
    return [
        generate_trend_description(
            alfacase_document,
            alfacase_to_case_description,
            case_description.SeparatorTrendDescription,
        )
        for alfacase_document in document
    ]


def load_global_trend_description(
    document: DescriptionDocument,
) -> List[case_description.GlobalTrendDescription]:
    alfacase_to_case_description = {
        "curve_names": load_value,
    }
    return [
        generate_trend_description(
            alfacase_document,
            alfacase_to_case_description,
            case_description.GlobalTrendDescription,
        )
        for alfacase_document in document
    ]


def load_overall_pipe_trend_description(
    document: DescriptionDocument,
) -> List[case_description.OverallPipeTrendDescription]:
    alfacase_to_case_description = {
        "curve_names": load_value,
        "element_name": load_value,
        "location": get_enum_loader(enum_class=constants.OutputAttachmentLocation),
    }
    return [
        generate_trend_description(
            alfacase_document,
            alfacase_to_case_description,
            case_description.OverallPipeTrendDescription,
        )
        for alfacase_document in document
    ]


def load_tubing_description(
    document: DescriptionDocument,
) -> List[case_description.TubingDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "length": get_scalar_loader(from_unit="m"),
        "outer_diameter": get_scalar_loader(category="diameter"),
        "inner_diameter": get_scalar_loader(category="diameter"),
        "inner_roughness": get_scalar_loader(from_unit="m"),
        "material": load_value,
    }

    def generate_tubings_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.TubingDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_tubings_description(alfacase_document)
        for alfacase_document in document
    ]


def load_wall_layer_description(
    document: DescriptionDocument,
) -> List[case_description.WallLayerDescription]:
    alfacase_to_case_description = {
        "thickness": get_scalar_loader(from_unit="m"),
        "material_name": load_value,
        "has_annulus_flow": load_value,
    }

    def generate_wall_layer_container_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.WallLayerDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_wall_layer_container_description(alfacase_document)
        for alfacase_document in document
    ]


def load_annulus_description(
    document: DescriptionDocument,
) -> case_description.AnnulusDescription:
    alfacase_to_case_description = {
        "has_annulus_flow": load_value,
        "pvt_model": load_value,
        "top_node": load_value,
        "initial_conditions": load_initial_conditions_description,
        "equipment": get_instance_loader(
            class_=case_description.AnnulusEquipmentDescription
        ),
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.AnnulusDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_trends_output_description(
    document: DescriptionDocument,
) -> case_description.TrendsOutputDescription:
    alfacase_to_case_description = {
        "positional_pipe_trends": load_positional_pipe_trend_description,
        "equipment_trends": load_equipment_trend_description,
        "global_trends": load_global_trend_description,
        "overall_pipe_trends": load_overall_pipe_trend_description,
        "separator_trends": load_separator_trend_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.TrendsOutputDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_case_output_description(
    document: DescriptionDocument,
) -> case_description.CaseOutputDescription:
    alfacase_to_case_description = {
        "profiles": load_profile_output_description,
        "profile_frequency": get_scalar_loader(from_unit="s"),
        "trends": load_trends_output_description,
        "trend_frequency": get_scalar_loader(from_unit="s"),
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.CaseOutputDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_open_hole_description(
    document: DescriptionDocument,
) -> List[case_description.OpenHoleDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "length": get_scalar_loader(from_unit="m"),
        "diameter": get_scalar_loader(category="diameter"),
        "inner_roughness": get_scalar_loader(from_unit="m"),
    }

    def generate_open_hole_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.OpenHoleDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_open_hole_description(alfacase_document)
        for alfacase_document in document
    ]


def load_casing_description(
    document: DescriptionDocument,
) -> case_description.CasingDescription:
    alfacase_to_case_description = {
        "casing_sections": load_casing_section_description,
        "tubings": load_tubing_description,
        "packers": load_packer_description,
        "open_holes": load_open_hole_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.CasingDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_compressor_pressure_table_description(
    document: DescriptionDocument,
) -> case_description.CompressorPressureTableDescription:
    alfacase_to_case_description = {
        "speed_entries": get_array_loader(from_unit="rpm"),
        "corrected_mass_flow_rate_entries": get_array_loader(from_unit="kg/s"),
        "pressure_ratio_table": get_array_loader(from_unit="-"),
        "isentropic_efficiency_table": get_array_loader(from_unit="-"),
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.CompressorPressureTableDescription(
        **case_values
    )
    return update_multi_input_flags(document, item_description)


def load_compressor_equipment_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.CompressorEquipmentDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "position": get_scalar_loader(from_unit="m"),
        "table": load_compressor_pressure_table_description,
        "speed_curve": load_speed_curve_description,
        "reference_pressure": get_scalar_loader(from_unit="bar"),
        "reference_temperature": get_scalar_loader(from_unit="degC"),
        "constant_speed": get_scalar_loader(from_unit="rpm"),
        "compressor_type": get_enum_loader(enum_class=constants.CompressorSpeedType),
        "speed_curve_interpolation_type": get_enum_loader(
            enum_class=constants.InterpolationType
        ),
        "flow_direction": get_enum_loader(enum_class=constants.FlowDirection),
    }

    def generate_compressor_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.CompressorEquipmentDescription(
            **case_values
        )
        return update_multi_input_flags(document, item_description)

    return {
        key.data: generate_compressor_description(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def load_environment_description(
    document: DescriptionDocument,
) -> case_description.EnvironmentDescription:
    alfacase_to_case_description = {
        "thermal_model": get_enum_loader(enum_class=constants.PipeThermalModelType),
        "position_input_mode": get_enum_loader(
            enum_class=constants.PipeThermalPositionInput
        ),
        "reference_y_coordinate": get_scalar_loader(from_unit="m"),
        "md_properties_table": load_environment_property_description,
        "tvd_properties_table": load_environment_property_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.EnvironmentDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_formation_description(
    document: DescriptionDocument,
) -> case_description.FormationDescription:
    alfacase_to_case_description = {
        "reference_y_coordinate": get_scalar_loader(from_unit="m"),
        "layers": load_formation_layer_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.FormationDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def _generate_description(
    document: DescriptionDocument,
    alfacase_to_case_description: Dict[str, Callable],
    description_type: Type[T],
) -> T:
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = description_type(**case_values)
    return update_multi_input_flags(document, item_description)


def load_pump_equipment_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.PumpEquipmentDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "position": get_scalar_loader(from_unit="m"),
        "type": get_enum_loader(enum_class=constants.PumpType),
        "pressure_boost": get_scalar_loader(from_unit="Pa"),
        "thermal_efficiency": get_scalar_loader(from_unit="-"),
        "table": load_table_pump_description,
        "speed_curve": load_speed_curve_description,
        "speed_curve_interpolation_type": get_enum_loader(
            enum_class=constants.InterpolationType
        ),
        "flow_direction": get_enum_loader(enum_class=constants.FlowDirection),
    }

    return {
        key.data: _generate_description(
            DescriptionDocument(value, document.file_path),
            alfacase_to_case_description,
            case_description.PumpEquipmentDescription,
        )
        for key, value in document.content.items()
    }


def load_valve_equipment_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.ValveEquipmentDescription]:
    alfacase_to_case_description = get_case_description_attribute_loader_dict(
        case_description.ValveEquipmentDescription
    )

    return {
        key.data: _generate_description(
            DescriptionDocument(value, document.file_path),
            alfacase_to_case_description,
            case_description.ValveEquipmentDescription,
        )
        for key, value in document.content.items()
    }


def load_pig_equipment_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.PigEquipmentDescription]:
    alfacase_to_case_description = get_case_description_attribute_loader_dict(
        case_description.PigEquipmentDescription
    )

    return {
        key.data: _generate_description(
            DescriptionDocument(value, document.file_path),
            alfacase_to_case_description,
            case_description.PigEquipmentDescription,
        )
        for key, value in document.content.items()
    }


def load_wall_description(
    document: DescriptionDocument,
) -> List[case_description.WallDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "inner_roughness": get_scalar_loader(from_unit="m"),
        "wall_layer_container": load_wall_layer_description,
    }

    return [
        _generate_description(
            alfacase_document,
            alfacase_to_case_description,
            case_description.WallDescription,
        )
        for alfacase_document in document
    ]


def load_equipment_description(
    document: DescriptionDocument,
) -> case_description.EquipmentDescription:
    return load_instance(document, case_description.EquipmentDescription)


def load_x_and_y_description(
    document: DescriptionDocument,
) -> case_description.XAndYDescription:
    alfacase_to_case_description = {
        "x": get_array_loader(from_unit="m"),
        "y": get_array_loader(from_unit="m"),
    }
    return _generate_description(
        document,
        alfacase_to_case_description,
        case_description.XAndYDescription,
    )


def load_length_and_elevation_description(
    document: DescriptionDocument,
) -> case_description.LengthAndElevationDescription:
    alfacase_to_case_description = {
        "length": get_array_loader(from_unit="m"),
        "elevation": get_array_loader(from_unit="m"),
    }
    return _generate_description(
        document,
        alfacase_to_case_description,
        case_description.LengthAndElevationDescription,
    )


def load_profile_description(
    document: DescriptionDocument,
) -> case_description.ProfileDescription:
    alfacase_to_case_description = {
        "x_and_y": load_x_and_y_description,
        "length_and_elevation": load_length_and_elevation_description,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.ProfileDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_pipe_description(
    document: DescriptionDocument,
) -> List[case_description.PipeDescription]:
    # fmt: off
    alfacase_to_case_description = {
        "environment": load_environment_description,
        "equipment": load_equipment_description,
        "initial_conditions": load_initial_conditions_description,
        "profile": load_profile_description,
        "name": load_value,
        "pvt_model": load_value,
        "segments": load_pipe_segments_description,
        "source": load_value,
        "target": load_value,
        "source_port": get_enum_loader(enum_class=constants.WellConnectionPort),
        "target_port": get_enum_loader(enum_class=constants.WellConnectionPort),
    }

    # fmt: on
    def generate_pipes_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.PipeDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_pipes_description(alfacase_document) for alfacase_document in document
    ]


def load_well_description(
    document: DescriptionDocument,
) -> List[case_description.WellDescription]:
    alfacase_to_case_description = {
        "name": load_value,
        "pvt_model": load_value,
        "stagnant_fluid": load_value,
        "profile": load_profile_description,
        "casing": load_casing_description,
        "annulus": load_annulus_description,
        "top_node": load_value,
        "bottom_node": load_value,
        "initial_conditions": load_initial_conditions_description,
        "environment": load_environment_description,
        "equipment": load_equipment_description,
        "formation": load_formation_description,
    }

    def generate_wells_description(document: DescriptionDocument):
        case_values = to_case_values(document, alfacase_to_case_description)
        item_description = case_description.WellDescription(**case_values)
        return update_multi_input_flags(document, item_description)

    return [
        generate_wells_description(alfacase_document) for alfacase_document in document
    ]


def load_physics_description(
    document: DescriptionDocument,
) -> case_description.PhysicsDescription:
    # fmt: off
    alfacase_to_case_description = {
        'hydrodynamic_model': get_enum_loader(enum_class=constants.HydrodynamicModelType),
        'simulation_regime': get_enum_loader(enum_class=constants.SimulationRegimeType),
        'energy_model': get_enum_loader(enum_class=constants.EnergyModel),
        'solids_model': get_enum_loader(enum_class=constants.SolidsModelType),
        'initial_condition_strategy': get_enum_loader(enum_class=constants.InitialConditionStrategyType),
        'restart_filepath': load_path,
        'keep_former_results': load_value,
        'emulsion_model': get_enum_loader(enum_class=constants.EmulsionModelType),
        'emulsion_model_plugin_id': load_value,
        'flash_model': get_enum_loader(enum_class=constants.FlashModel),
        'correlations_package': get_enum_loader(enum_class=constants.CorrelationPackageType),
    }
    # fmt: on
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.PhysicsDescription(**case_values)
    return update_multi_input_flags(document, item_description)


# fmt: off
def load_numerical_options_description(document: DescriptionDocument) -> case_description.NumericalOptionsDescription:
    alfacase_to_case_description = {
        'tolerance': load_value,
        'maximum_iterations': load_value,
        'maximum_timestep_change_factor': load_value,
        'maximum_cfl_value': load_value,
        'nonlinear_solver_type': get_enum_loader(enum_class=constants.NonlinearSolverType),
        'relaxed_tolerance': load_value,
        'divergence_tolerance': load_value,
        'friction_factor_evaluation_strategy': get_enum_loader(enum_class=constants.EvaluationStrategyType),
        'simulation_mode': get_enum_loader(enum_class=constants.SimulationModeType),
        'enable_solver_caching': load_value,
        'caching_rtol': load_value,
        'caching_atol': load_value,
        'always_repeat_timestep': load_value,
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.NumericalOptionsDescription(**case_values)
    return update_multi_input_flags(document, item_description)
# fmt: on


# fmt: off
def load_time_options_description(
    document: DescriptionDocument
) -> case_description.TimeOptionsDescription:
    alfacase_to_case_description = {
        "stop_on_steady_state": load_value,
        "initial_time": get_scalar_loader(from_unit="h"),
        "final_time": get_scalar_loader(from_unit="h"),
        "initial_timestep": get_scalar_loader(from_unit="s"),
        "minimum_timestep": get_scalar_loader(from_unit="s"),
        "maximum_timestep": get_scalar_loader(from_unit="s"),
        "restart_autosave_frequency": get_scalar_loader(from_unit="h"),
        "minimum_time_for_steady_state_stop": get_scalar_loader(from_unit="s"),
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.TimeOptionsDescription(**case_values)
    return update_multi_input_flags(document, item_description)

# fmt: on


def load_tracer_model_constant_coefficients_description(
    document: DescriptionDocument,
) -> Dict[str, case_description.TracerModelConstantCoefficientsDescription]:
    alfacase_to_case_description = {
        "partition_coefficients": get_scalar_dict_loader(category="mass fraction")
    }

    def generate_tracer_model_constant_coefficients_description(
        value: DescriptionDocument,
    ):
        case_values = to_case_values(value, alfacase_to_case_description)
        return case_description.TracerModelConstantCoefficientsDescription(
            **case_values
        )

    return {
        key.data: generate_tracer_model_constant_coefficients_description(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def load_tracers_description(
    document: DescriptionDocument,
) -> case_description.TracersDescription:
    alfacase_to_case_description = {
        "constant_coefficients": load_tracer_model_constant_coefficients_description
    }
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.TracersDescription(**case_values)
    return update_multi_input_flags(document, item_description)


def load_case_description(
    document: DescriptionDocument,
) -> case_description.CaseDescription:
    # fmt: off
    alfacase_to_case_description = {
        'physics': load_physics_description,
        'numerical_options': load_numerical_options_description,
        'time_options': load_time_options_description,
        'max_timestep_change_factor': load_value,
        'max_cfl_value': load_value,
        'friction_factor_evaluation_strategy': get_enum_loader(enum_class=constants.EvaluationStrategyType),
        'name': load_value,
        'positions': load_value,
        'tracers': load_tracers_description,
        'ipr_models': load_ipr_models_description,
        'pvt_models': load_pvt_models_description,
        'materials': load_material_description,
        'nodes': load_node_description,
        'outputs': load_case_output_description,
        'pipes': load_pipe_description,
        'walls': load_wall_description,
        'wells': load_well_description,
    }
    # fmt: on
    case_values = to_case_values(document, alfacase_to_case_description)
    item_description = case_description.CaseDescription(**case_values)
    return update_multi_input_flags(document, item_description)
