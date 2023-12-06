import itertools
from functools import partial
from pathlib import Path
from pathlib import PurePosixPath
from types import ModuleType
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

import attr
from barril.units import Array
from barril.units import Scalar
from typing_extensions import TypeGuard

from alfasim_sdk import BaseField
from alfasim_sdk._internal.alfacase.alfacase_to_case import DescriptionDocument
from alfasim_sdk._internal.alfacase.alfacase_to_case import load_value
from alfasim_sdk._internal.alfacase.alfacase_to_case import to_case_values
from alfasim_sdk._internal.alfacase.case_description import CaseDescription
from alfasim_sdk._internal.alfacase.case_description import PluginDescription
from alfasim_sdk._internal.alfacase.case_description import PluginFileContent
from alfasim_sdk._internal.alfacase.case_description import PluginInternalReference
from alfasim_sdk._internal.alfacase.case_description import PluginMultipleReference
from alfasim_sdk._internal.alfacase.case_description import PluginTableContainer
from alfasim_sdk._internal.alfacase.case_description import PluginTracerReference
from alfasim_sdk._internal.alfacase.case_description_attributes import (
    InvalidPluginDataError,
)
from alfasim_sdk._internal.alfacase.plugin_introspection import get_attributes
from alfasim_sdk._internal.types import Boolean
from alfasim_sdk._internal.types import Enum
from alfasim_sdk._internal.types import FileContent
from alfasim_sdk._internal.types import MultipleReference
from alfasim_sdk._internal.types import Quantity
from alfasim_sdk._internal.types import Reference
from alfasim_sdk._internal.types import String
from alfasim_sdk._internal.types import Table
from alfasim_sdk._internal.types import TracerType

_CHILDREN_LIST_KEY = "_children_list"


def get_unused_filename(alfacase_folder: Path, path: Path) -> Path:
    """
    Return a not used file name inside ``alfacase_folder``.
    """
    # The original file does not need to actually exist (`path.stem` could be empty).
    stem = path.stem or "(unnamed)"
    fullpath = alfacase_folder / f"{stem}{path.suffix}"
    for i in itertools.count(2):
        if fullpath.exists():
            fullpath = fullpath.with_name(f"{stem} ({i}){path.suffix}")
        else:
            return fullpath


def _dump_file_contents_and_update_dict(
    gui_models_part: object, alfacase_folder: Path
) -> object:
    """
    If ``gui_models_part``:
    - is a ``dict`` or ``list`` an updated copy returned;
    - is a ``PluginFileContent`` the contents are dumped to the disc and the nem file name is returned;
    - otherwise the value is returned unchanged;
    """
    if isinstance(gui_models_part, dict):
        return {
            k: _dump_file_contents_and_update_dict(v, alfacase_folder)
            for k, v in gui_models_part.items()
        }
    elif isinstance(gui_models_part, list):
        return [
            _dump_file_contents_and_update_dict(v, alfacase_folder)
            for v in gui_models_part
        ]
    elif isinstance(gui_models_part, PluginFileContent):
        path = get_unused_filename(alfacase_folder, gui_models_part.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(gui_models_part.content)
        path = path.relative_to(alfacase_folder)
        return str(PurePosixPath(path))
    else:
        return gui_models_part


def _dump_file_contents_and_update_plugin_description(
    plugin: PluginDescription, alfacase_folder: Path
) -> PluginDescription:
    """
    "attr.evolve" the ``PluginDescription`` with an update ``gui_models``
    where the ``PluginFileContent`` instances are replaced by a path to files
    with the expected content.
    """
    gui_models = plugin.gui_models
    gui_models = _dump_file_contents_and_update_dict(gui_models, alfacase_folder)
    return attr.evolve(plugin, gui_models=gui_models)


def dump_file_contents_and_update_plugins(
    alfacase_description: CaseDescription, alfacase_file: Path
) -> CaseDescription:
    alfacase_folder = alfacase_file.parent
    plugins = alfacase_description.plugins
    plugins = [
        _dump_file_contents_and_update_plugin_description(p, alfacase_folder)
        for p in plugins
    ]
    return attr.evolve(alfacase_description, plugins=plugins)


def load_list_of_plugin(
    alfacase_content: DescriptionDocument,
) -> List[PluginDescription]:
    """
    A loader function similar to ``load_list_of_instance`` for plugins.
    """
    plugins = (
        load_plugin(DescriptionDocument(value, alfacase_content.file_path))
        for value in alfacase_content.content
    )
    return [p for p in plugins if p is not None]


def load_plugin(alfacase_content: DescriptionDocument) -> Optional[PluginDescription]:
    """
    A loader function similar to ``load_instance`` for plugins.
    """
    alfacase_to_case_description = (
        get_case_description_attribute_loader_dict_for_plugin(alfacase_content)
    )
    if alfacase_to_case_description is not None:
        case_values = to_case_values(alfacase_content, alfacase_to_case_description)
        return PluginDescription(**case_values)
    else:
        return None


def get_case_description_attribute_loader_dict_for_plugin(
    alfacase_content: DescriptionDocument,
) -> Optional[Dict[str, Callable]]:
    """
    Create a dict of loaders to be used with `to_case_values`, if the plugin is not installed return `None`.

    Equivalent to ``get_case_description_attribute_loader_dict``
    but designed to load plugins data (class info is not readily available).
    """
    plugin_id = load_value("name", alfacase_content)
    data_structure: Optional[List[Type]] = load_plugin_data_structure(plugin_id)
    if data_structure is None:
        return None
    else:
        return {
            "name": load_value,
            "gui_models": partial(load_gui_models, data_structure=data_structure),
            "is_enabled": load_value,
        }


def get_plugin_module_candidates(plugin_id: str) -> List[Path]:
    """
    List the possible module paths the the plugins models.
    """
    from os import environ
    from os.path import pathsep

    alfasim_plugins_dir_env_var = environ.get("ALFASIM_PLUGINS_DIR")
    if alfasim_plugins_dir_env_var is None:
        alfasim_plugins_dirs = []
    else:
        alfasim_plugins_dirs = alfasim_plugins_dir_env_var.split(pathsep)

    alfasim_plugins_dirs.append(Path.home() / ".alfasim_plugins")
    asset_suffix = f"{plugin_id}/artifacts/{plugin_id}.py"
    return [Path(p) / asset_suffix for p in alfasim_plugins_dirs]


def import_module(path: Path) -> ModuleType:
    """
    Import and return a module.
    """
    import importlib

    assert path.is_file()
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_plugin_data_structure(plugin_id: str) -> Optional[List[Type]]:
    """
    Obtain the models for a given plugin.
    """
    import alfasim_sdk_plugins

    for candidate in get_plugin_module_candidates(plugin_id):
        if candidate.is_file():
            # Update the "alfasim_sdk_plugins" namespace.
            namespace_package_str = None
            remove_namespace_package = False
            namespace_package = candidate.parent / "alfasim_sdk_plugins"
            if namespace_package.is_dir():
                namespace_package_str = str(namespace_package.absolute())
                if namespace_package_str not in alfasim_sdk_plugins.__path__:
                    alfasim_sdk_plugins.__path__.append(namespace_package_str)
                    remove_namespace_package = True

            module = import_module(candidate)
            if hasattr(module, "alfasim_get_data_model_type"):
                models = module.alfasim_get_data_model_type()
                if all(hasattr(m, "_alfasim_metadata") for m in models):
                    return models

            # Cleanup "alfasim_sdk_plugins" namespace.
            # When a valid plugin is found leave the namespace package unchanged.
            if remove_namespace_package:
                alfasim_sdk_plugins.__path__.remove(namespace_package_str)

    else:
        return None


def is_dict_with_keys(
    possible_dict: object, *keys: str, strict: bool = True
) -> TypeGuard[Dict]:
    """
    Check if `possible_dict` is a `dict` with keys `keys`.
    If `strict` is `True` the dict can not have extra keys.
    """
    if isinstance(possible_dict, dict):
        for k in keys:
            if k not in possible_dict:
                return False
        else:
            return not (strict and (len(keys) != len(possible_dict)))

    return False


def _convert_boolean(
    value: object, type_from_plugin: BaseField, alfacase_path: Path
) -> bool:
    """
    Try to convert a object loaded from alfacase as a boolean.
    """
    assert isinstance(type_from_plugin, Boolean)
    if isinstance(value, str):
        return value.upper() == "TRUE"
    raise InvalidPluginDataError(f"Can not convert to a boolean: {value!r}")


def _convert_enum(
    value: object, type_from_plugin: BaseField, alfacase_path: Path
) -> str:
    """
    Try to convert a object loaded from alfacase as an enum.
    """
    assert isinstance(type_from_plugin, Enum)
    if isinstance(value, str) and (value in type_from_plugin.values):
        return value
    raise InvalidPluginDataError(
        f"Can not convert to an enum: {value!r}"
        f" (valid values are {type_from_plugin.values!r}"
    )


def _convert_file_content(
    value: object, type_from_plugin: BaseField, alfacase_path: Path
) -> PluginFileContent:
    """
    Try to convert a object loaded from alfacase as a plugin file content.
    """
    assert isinstance(type_from_plugin, FileContent)
    if isinstance(value, str):
        parent = alfacase_path.parent.absolute()
        file_path = (alfacase_path.parent / Path(value)).absolute()
        return PluginFileContent.from_path(file_path, parent)
    raise InvalidPluginDataError(f"Can not convert to a file content: {value!r}")


def _convert_multiple_reference(
    value: object, type_from_plugin: BaseField, alfacase_path: Path
) -> PluginMultipleReference:
    """
    Try to convert a object loaded from alfacase as a plugin multiple reference.
    """
    assert isinstance(type_from_plugin, MultipleReference)
    if is_dict_with_keys(value, "container_key", "item_id_list"):
        return PluginMultipleReference(
            container_key=value["container_key"],
            item_id_list=[int(i) for i in value["item_id_list"]],
        )
    raise InvalidPluginDataError(f"Can not convert to a multiple reference: {value!r}")


def _convert_reference(
    value: object, type_from_plugin: BaseField, alfacase_path: Path
) -> Union[PluginTracerReference, PluginInternalReference]:
    """
    Try to convert a object loaded from alfacase as a plugin internal reference or plugin trace reference.
    """
    assert isinstance(type_from_plugin, Reference)
    ref_type = type_from_plugin.ref_type
    if ref_type is TracerType:
        if is_dict_with_keys(value, "tracer_id"):
            return PluginTracerReference(tracer_id=int(value["tracer_id"]))
    else:
        if is_dict_with_keys(value, "plugin_item_id"):
            return PluginInternalReference(plugin_item_id=int(value["plugin_item_id"]))
    raise InvalidPluginDataError(f"Can not convert to a reference: {value!r}")


def _convert_quantity(
    value: object, type_from_plugin: BaseField, alfacase_path: Path
) -> Scalar:
    """
    Try to convert a object loaded from alfacase as a scalar.
    """
    assert isinstance(type_from_plugin, Quantity)
    if is_dict_with_keys(value, "value", "unit"):
        return Scalar(float(value["value"]), value["unit"])
    raise InvalidPluginDataError(f"Can not convert to a quantity: {value!r}")


def _convert_string(
    value: object, type_from_plugin: BaseField, alfacase_path: Path
) -> str:
    """
    Try to convert a object loaded from alfacase as a string.
    Just check if the input is actually a string.
    """
    assert isinstance(type_from_plugin, String)
    if isinstance(value, str):
        return value
    raise InvalidPluginDataError(f"Can not convert to a string: {value!r}")


def _convert_table(
    value: object, type_from_plugin: BaseField, alfacase_path: Path
) -> PluginTableContainer:
    """
    Try to convert a object loaded from alfacase as a table.
    """
    assert isinstance(type_from_plugin, Table)
    if is_dict_with_keys(value, "columns"):
        raw_columns = value["columns"]
        col_ids = [col.id for col in type_from_plugin.rows]
        if is_dict_with_keys(raw_columns, *col_ids):
            columns = {}
            for col in col_ids:
                raw_col = raw_columns[col]
                if is_dict_with_keys(raw_col, "values", "unit"):
                    columns[col] = Array(
                        [float(v) for v in raw_col["values"]], raw_col["unit"]
                    )
                else:
                    raise InvalidPluginDataError(
                        f"Can not convert table column: {raw_col!r}"
                    )
            return PluginTableContainer(columns=columns)
    raise InvalidPluginDataError(f"Can not convert to a table: {value!r}")


_PluginDataLoader = Callable[[object, BaseField, Path], object]
_PLUGIN_FIELD_TO_CASEDESCRIPTION: Dict[Type, _PluginDataLoader] = {
    Boolean: _convert_boolean,
    Enum: _convert_enum,
    FileContent: _convert_file_content,
    MultipleReference: _convert_multiple_reference,
    Reference: _convert_reference,
    Quantity: _convert_quantity,
    String: _convert_string,
    Table: _convert_table,
}


def load_model(alfacase_content: DescriptionDocument, class_: Type) -> Dict[str, Any]:
    """
    Convert alfacase fragment as a dict equivalent to a plugin model.
    """
    alfasim_metadata: Optional[object] = getattr(class_, "_alfasim_metadata")
    assert isinstance(alfasim_metadata, dict)
    alfacase_path = alfacase_content.file_path

    result = {}
    for attribute in get_attributes(class_):
        type_from_plugin = attribute.default
        name: str = attribute.name
        if name in alfacase_content.content:
            value: Union[dict, list, str] = alfacase_content.content[name].data
            convert_func = _PLUGIN_FIELD_TO_CASEDESCRIPTION[type(type_from_plugin)]
            result[name] = convert_func(value, type_from_plugin, alfacase_path)

    child_model_type = alfasim_metadata["model"]
    if child_model_type is not None:
        children = alfacase_content.content.get("_children_list", [])
        result["_children_list"] = [
            load_model(DescriptionDocument(v, alfacase_path), class_=child_model_type)
            for v in children
        ]

    return result


def load_gui_models(
    alfacase_content: DescriptionDocument, *, data_structure: List[Type]
):
    result = {}
    for model in data_structure:
        name = model.__name__
        if name in alfacase_content.content:
            result[name] = load_model(alfacase_content[name], class_=model)

    return result
