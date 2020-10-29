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
from typing import Union

import attr
from attr.validators import instance_of
from barril.units import Array
from barril.units import Scalar
from barril.units import UnitDatabase
from strictyaml import YAML

from alfasim_sdk import constants
from alfasim_sdk.alfacase import case_description


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
    def FromFile(cls, file_path: Path) -> "DescriptionDocument":
        """
        Load the values from the given file_path validating against the Schema defined on
        alfacase.schema.case_schema
        """
        from alfasim_sdk.alfacase.schema import case_description_schema
        import strictyaml

        content = strictyaml.dirty_load(
            yaml_string=Path(file_path).read_text(encoding="UTF-8"),
            schema=case_description_schema,
            allow_flow_style=True,
        )
        return cls(content, file_path)


@lru_cache(maxsize=None)
def GetCategoryFor(unit: Optional[str]) -> Optional[str]:
    """
    Return the default category for the given unit
    """
    if unit:
        return UnitDatabase.GetSingleton().GetDefaultCategory(unit)


def LoadScalar(key: str, alfacase_content: DescriptionDocument, category) -> Scalar:
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
def GetScalarLoader(
    *, category: Optional[str] = None, from_unit: Optional[str] = None
) -> Callable:
    """
    Return a LoadArray function pre-populate with the category

    If ``from_unit`` is provided, the category parameter will be filled with
    the default category for the given unit.
    """
    return partial(LoadScalar, category=_ObtainCategoryForScalar(category, from_unit))


def LoadArray(key: str, alfacase_content: DescriptionDocument, category) -> Array:
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
def GetArrayLoader(
    *, category: Optional[str] = None, from_unit: Optional[str] = None
) -> Callable:
    """
    Return a LoadArray function pre-populate with the category

    If ``from_unit`` is provided, the category parameter will be filled with
    the default category for the given unit.
    """
    return partial(LoadArray, category=_ObtainCategoryForScalar(category, from_unit))


def LoadListOfArrays(
    key: str, alfacase_content: DescriptionDocument, category
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
def GetListOfArraysLoader(
    *, category: Optional[str] = None, from_unit: Optional[str] = None
) -> Callable:
    """
    Return a LoadListOfArrays function pre-populated with the category

    If ``from_unit`` is provided, the category parameter will be filled with
    the default category for the given unit.
    """
    return partial(
        LoadListOfArrays, category=_ObtainCategoryForScalar(category, from_unit)
    )


def LoadDictOfArrays(
    key: str, alfacase_content: DescriptionDocument, category
) -> Array:
    """
    Create a Dict of str to barril.units.Array instances from the given YAML content.
    # TODO: ASIM-3556: All atributes from this module should get the category from the CaseDescription
    """
    return {
        k: Array(category, v["values"], v["unit"])
        for k, v in alfacase_content[key].content.data.items()
    }


@lru_cache(maxsize=None)
def GetDictOfArraysLoader(
    *, category: Optional[str] = None, from_unit: Optional[str] = None
) -> Callable:
    """
    Return a LoadDictOfArrays function pre-populated with the category

    If ``from_unit`` is provided, the category parameter will be filled with
    the default category for the given unit.
    """
    return partial(
        LoadDictOfArrays, category=_ObtainCategoryForScalar(category, from_unit)
    )


def _ObtainCategoryForScalar(category: str, from_unit: str) -> str:
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

    return category or GetCategoryFor(from_unit)


def LoadDictWithScalar(
    key: str, alfacase_content: DescriptionDocument, category
) -> Dict[str, Scalar]:
    return {
        key: Scalar(category, value["value"], value["unit"])
        for key, value in alfacase_content[key].content.data.items()
    }


def GetDictWithScalarLoader(*, category: str) -> Callable:
    """
    Return a LoadDictWithScalar function pre-populate with the category
    """
    return partial(LoadDictWithScalar, category=category)


def LoadEnum(
    key: str, alfacase_content: DescriptionDocument, enum_class: Type[enum.Enum]
) -> enum.Enum:
    """
    Return the PythonEnum equivalent from the yaml content
    """
    enum_value = alfacase_content[key].content.data

    return enum_class(enum_value)


def GetEnumLoader(*, enum_class: enum.EnumMeta) -> Callable:
    """
    Return a LoadEnum function pre-populated with the enum_class
    """
    return partial(LoadEnum, enum_class=enum_class)


def LoadValue(
    key: str, alfacase_content: DescriptionDocument
) -> Union[str, Number, list, dict]:
    """
    Loads a python builtin value such as str, int, float, bool, etc
    """
    return alfacase_content[key].content.data


def LoadPath(key: str, alfacase_content: DescriptionDocument) -> Path:
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


def LoadPvtTables(alfacase_content: DescriptionDocument) -> Dict[str, Path]:
    def GetTableFile(value):
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
        ) = case_description.PvtModelsDescription.GetPvtFileAndModelName(value)

        def AppendPvtModelNameIfDefined(file_path: Path) -> Path:
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
            return Path(AppendPvtModelNameIfDefined(pvt_path))
        else:
            raise RuntimeError(
                f"The PVT Table {value} must be place within the "
                f"{alfacase_content.file_path.name} file on {str(alfacase_content.file_path.parent)}"
            )

    return {
        key.data: GetTableFile(value.data)
        for key, value in alfacase_content.content.items()
    }


def LoadPvtModelCorrelationDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.PvtModelCorrelationDescription]:
    alfacase_to_case_description = {
        "oil_density_std": GetScalarLoader(from_unit="kg/m3"),
        "gas_density_std": GetScalarLoader(from_unit="kg/m3"),
        "rs_sat": GetScalarLoader(from_unit="sm3/sm3"),
        "pvt_correlation_package": GetEnumLoader(
            enum_class=constants.CorrelationPackage
        ),
    }

    def GeneratePvtModelCorrelation(value: DescriptionDocument):
        case_values = ToCaseValues(value, alfacase_to_case_description)
        return case_description.PvtModelCorrelationDescription(**case_values)

    return {
        key.data: GeneratePvtModelCorrelation(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadHeavyComponentDescription(
    document: DescriptionDocument,
) -> List[case_description.HeavyComponentDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "scn": LoadValue,
        "MW": GetScalarLoader(from_unit="kg/mol"),
        "rho": GetScalarLoader(from_unit="kg/m3"),
    }

    def GenerateHeavyComponentsDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.HeavyComponentDescription(**case_values)

    return [
        GenerateHeavyComponentsDescription(alfacase_document)
        for alfacase_document in document
    ]


def LoadLightComponentDescription(
    document: DescriptionDocument,
) -> List[case_description.LightComponentDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "Pc": GetScalarLoader(from_unit="Pa"),
        "Tc": GetScalarLoader(from_unit="K"),
        "Vc": GetScalarLoader(from_unit="m3/mol"),
        "omega": GetScalarLoader(from_unit="-"),
        "MW": GetScalarLoader(from_unit="kg/mol"),
        "Tb": GetScalarLoader(from_unit="K"),
        "Parachor": GetScalarLoader(from_unit="-"),
        "B_parameter": GetScalarLoader(from_unit="-"),
        "Cp_0": GetScalarLoader(from_unit="-"),
        "Cp_1": GetScalarLoader(from_unit="-"),
        "Cp_2": GetScalarLoader(from_unit="-"),
        "Cp_3": GetScalarLoader(from_unit="-"),
        "Cp_4": GetScalarLoader(from_unit="-"),
    }

    def GenerateLightComponentsDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.LightComponentDescription(**case_values)

    return [
        GenerateLightComponentsDescription(alfacase_document)
        for alfacase_document in document
    ]


def LoadBipDescription(
    document: DescriptionDocument,
) -> List[case_description.BipDescription]:
    alfacase_to_case_description = {
        "component_1": LoadValue,
        "component_2": LoadValue,
        "value": LoadValue,
    }

    def GenerateBipDescription(alfacase_document: DescriptionDocument):
        case_values = ToCaseValues(alfacase_document, alfacase_to_case_description)
        return case_description.BipDescription(**case_values)

    return [GenerateBipDescription(alfacase_document) for alfacase_document in document]


def LoadCompositionDescription(
    document: DescriptionDocument,
) -> List[case_description.CompositionDescription]:
    alfacase_to_case_description = {
        "component": LoadValue,
        "molar_fraction": GetScalarLoader(from_unit="mol/mol"),
        "reference_enthalpy": GetScalarLoader(from_unit="J/mol"),
    }

    def GenerateCompositionDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.CompositionDescription(**case_values)

    return [
        GenerateCompositionDescription(alfacase_document)
        for alfacase_document in document
    ]


def LoadFluidDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.FluidDescription]:
    alfacase_to_case_description = {
        "composition": LoadCompositionDescription,
        "fraction_pairs": LoadBipDescription,
    }

    def GenerateFluidDescription(
        value: DescriptionDocument,
    ) -> case_description.FluidDescription:
        case_values = ToCaseValues(value, alfacase_to_case_description)
        return case_description.FluidDescription(**case_values)

    return {
        key.data: GenerateFluidDescription(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadPvtModelCompositionalDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.PvtModelCompositionalDescription]:
    alfacase_to_case_description = {
        "equation_of_state_type": GetEnumLoader(
            enum_class=constants.EquationOfStateType
        ),
        "surface_tension_model_type": GetEnumLoader(
            enum_class=constants.SurfaceTensionType
        ),
        "viscosity_model": GetEnumLoader(
            enum_class=constants.PVTCompositionalViscosityModel
        ),
        "heavy_components": LoadHeavyComponentDescription,
        "light_components": LoadLightComponentDescription,
        "fluids": LoadFluidDescription,
    }

    def GeneratePvtModelCompositional(value: DescriptionDocument):
        case_values = ToCaseValues(value, alfacase_to_case_description)
        return case_description.PvtModelCompositionalDescription(**case_values)

    return {
        key.data: GeneratePvtModelCompositional(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadPvtModelsDescription(
    document: DescriptionDocument,
) -> case_description.PvtModelsDescription:
    alfacase_to_case_description = {
        "default_model": LoadValue,
        "tables": LoadPvtTables,
        "correlations": LoadPvtModelCorrelationDescription,
        "compositions": LoadPvtModelCompositionalDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.PvtModelsDescription(**case_values)


# Used for testing - Will be ignored on the document contents
IGNORE_KEY = "IgnoreKey"


def ToCaseValues(
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
            alfacase_to_case_description[attr_name] = ExecuteLoader(
                attr_name, function_handle, document
            )

    return alfacase_to_case_description


def ExecuteLoader(
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


def LoadCasingSectionDescription(
    document: DescriptionDocument,
) -> List[case_description.CasingSectionDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "hanger_depth": GetScalarLoader(from_unit="m"),
        "settings_depth": GetScalarLoader(from_unit="m"),
        "hole_diameter": GetScalarLoader(from_unit="m"),
        "outer_diameter": GetScalarLoader(from_unit="m"),
        "inner_diameter": GetScalarLoader(from_unit="m"),
        "inner_roughness": GetScalarLoader(from_unit="m"),
        "material": LoadValue,
        "top_of_filler": GetScalarLoader(from_unit="m"),
        "filler_material": LoadValue,
        "material_above_filler": LoadValue,
    }

    def GenerateCasingSectionDescription(document: DescriptionDocument):
        case_content = ToCaseValues(document, alfacase_to_case_description)
        return case_description.CasingSectionDescription(**case_content)

    return [
        GenerateCasingSectionDescription(alfacase_document)
        for alfacase_document in document
    ]


def LoadCvTableDescription(
    document: DescriptionDocument,
) -> case_description.CvTableDescription:
    alfacase_to_case_description = {
        "opening": GetArrayLoader(from_unit="-"),
        "flow_coefficient": GetArrayLoader(from_unit="(galUS/min)/(psi^0.5)"),
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.CvTableDescription(**case_values)


def LoadEnvironmentPropertyDescription(
    document: DescriptionDocument,
) -> List[case_description.EnvironmentPropertyDescription]:
    # fmt: off
    alfacase_to_case_description = {
        'type': GetEnumLoader(enum_class=constants.PipeEnvironmentHeatTransferCoefficientModelType),
        'position': GetScalarLoader(from_unit='m'),
        'temperature': GetScalarLoader(from_unit='degC'),
        'heat_transfer_coefficient': GetScalarLoader(from_unit='W/m2.K'),
        'overall_heat_transfer_coefficient': GetScalarLoader(from_unit='W/m2.K'),
        'fluid_velocity': GetScalarLoader(from_unit='m/s'),
    }
    # fmt: on
    def GenerateEnvironmentPropertyDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.EnvironmentPropertyDescription(**case_values)

    return [
        GenerateEnvironmentPropertyDescription(alfacase_document)
        for alfacase_document in document
    ]


def LoadFormationLayerDescription(
    document: DescriptionDocument,
) -> List[case_description.FormationLayerDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "start": GetScalarLoader(from_unit="m"),
        "material": LoadValue,
    }

    def GenerateFormationLayerDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.FormationLayerDescription(**case_values)

    return [
        GenerateFormationLayerDescription(alfacase_document)
        for alfacase_document in document
    ]


def LoadGasLiftValveEquipmentDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.GasLiftValveEquipmentDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "position": GetScalarLoader(from_unit="m"),
        "diameter": GetScalarLoader(from_unit="m"),
        "valve_type": GetEnumLoader(enum_class=constants.ValveType),
        "delta_p_min": GetScalarLoader(from_unit="Pa"),
        "discharge_coeff": GetScalarLoader(from_unit="-"),
    }

    def GenerateGasLiftDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.GasLiftValveEquipmentDescription(**case_values)

    return {
        key.data: GenerateGasLiftDescription(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadHeatSourceEquipmentDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.HeatSourceEquipmentDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "start": GetScalarLoader(from_unit="m"),
        "length": GetScalarLoader(from_unit="m"),
        "power": GetScalarLoader(from_unit="W"),
    }

    def GenerateHeatSourceDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.HeatSourceEquipmentDescription(**case_values)

    return {
        key.data: GenerateHeatSourceDescription(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def GetInitialConditionsTableLoader(
    table_class, attr_name, attr_unit, *, is_referenced, is_multidimensional
):
    if is_multidimensional:
        attr_loader = GetDictOfArraysLoader(from_unit=attr_unit)
    else:
        attr_loader = GetArrayLoader(from_unit=attr_unit)

    def LoadInitialConditionsTable(document: DescriptionDocument):
        alfacase_to_case_description = {
            "positions": GetArrayLoader(from_unit="m"),
            attr_name: attr_loader,
        }
        if is_referenced:
            alfacase_to_case_description["reference_coordinate"] = GetScalarLoader(
                from_unit="m"
            )
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return table_class(**case_values)

    return LoadInitialConditionsTable


def GetTracersInitialConditionsTableLoader(
    table_class, attr_name, attr_unit, *, is_referenced
):
    attr_loader = GetListOfArraysLoader(from_unit=attr_unit)

    def LoadInitialConditionsTable(document: DescriptionDocument):
        alfacase_to_case_description = {
            "positions": GetArrayLoader(from_unit="m"),
            attr_name: attr_loader,
        }
        if is_referenced:
            alfacase_to_case_description["reference_coordinate"] = GetScalarLoader(
                from_unit="m"
            )
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return table_class(**case_values)

    return LoadInitialConditionsTable


LoadReferencedVelocitiesContainerDescription = GetInitialConditionsTableLoader(
    case_description.ReferencedVelocitiesContainerDescription,
    "velocities",
    "m/s",
    is_referenced=True,
    is_multidimensional=True,
)
LoadVelocitiesContainerDescription = GetInitialConditionsTableLoader(
    case_description.VelocitiesContainerDescription,
    "velocities",
    "m/s",
    is_referenced=False,
    is_multidimensional=True,
)


def LoadInitialVelocitiesDescription(
    document: DescriptionDocument,
) -> case_description.InitialVelocitiesDescription:
    alfacase_to_case_description = {
        "position_input_type": GetEnumLoader(enum_class=constants.TableInputType),
        "table_x": LoadReferencedVelocitiesContainerDescription,
        "table_y": LoadReferencedVelocitiesContainerDescription,
        "table_length": LoadVelocitiesContainerDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.InitialVelocitiesDescription(**case_values)


LoadReferencedTemperaturesContainerDescription = GetInitialConditionsTableLoader(
    case_description.ReferencedTemperaturesContainerDescription,
    "temperatures",
    "K",
    is_referenced=True,
    is_multidimensional=False,
)
LoadTemperaturesContainerDescription = GetInitialConditionsTableLoader(
    case_description.TemperaturesContainerDescription,
    "temperatures",
    "K",
    is_referenced=False,
    is_multidimensional=False,
)


def LoadInitialTemperaturesDescription(
    document: DescriptionDocument,
) -> case_description.InitialTemperaturesDescription:
    alfacase_to_case_description = {
        "position_input_type": GetEnumLoader(enum_class=constants.TableInputType),
        "table_x": LoadReferencedTemperaturesContainerDescription,
        "table_y": LoadReferencedTemperaturesContainerDescription,
        "table_length": LoadTemperaturesContainerDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.InitialTemperaturesDescription(**case_values)


LoadReferencedVolumeFractionsContainerDescription = GetInitialConditionsTableLoader(
    case_description.ReferencedVolumeFractionsContainerDescription,
    "fractions",
    "-",
    is_referenced=True,
    is_multidimensional=True,
)
LoadVolumeFractionsContainerDescription = GetInitialConditionsTableLoader(
    case_description.VolumeFractionsContainerDescription,
    "fractions",
    "-",
    is_referenced=False,
    is_multidimensional=True,
)


def LoadInitialVolumeFractionsDescription(
    document: DescriptionDocument,
) -> case_description.InitialVolumeFractionsDescription:
    alfacase_to_case_description = {
        "position_input_type": GetEnumLoader(enum_class=constants.TableInputType),
        "table_x": LoadReferencedVolumeFractionsContainerDescription,
        "table_y": LoadReferencedVolumeFractionsContainerDescription,
        "table_length": LoadVolumeFractionsContainerDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.InitialVolumeFractionsDescription(**case_values)


LoadReferencedPressureContainerDescription = GetInitialConditionsTableLoader(
    case_description.ReferencedPressureContainerDescription,
    "pressures",
    "Pa",
    is_referenced=True,
    is_multidimensional=False,
)
LoadPressureContainerDescription = GetInitialConditionsTableLoader(
    case_description.PressureContainerDescription,
    "pressures",
    "Pa",
    is_referenced=False,
    is_multidimensional=False,
)


def LoadInitialPressuresDescription(
    document: DescriptionDocument,
) -> case_description.InitialPressuresDescription:
    alfacase_to_case_description = {
        "position_input_type": GetEnumLoader(enum_class=constants.TableInputType),
        "table_x": LoadReferencedPressureContainerDescription,
        "table_y": LoadReferencedPressureContainerDescription,
        "table_length": LoadPressureContainerDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.InitialPressuresDescription(**case_values)


LoadReferencedTracersMassFractionsContainerDescription = (
    GetTracersInitialConditionsTableLoader(
        case_description.ReferencedTracersMassFractionsContainerDescription,
        "tracers_mass_fractions",
        "-",
        is_referenced=True,
    )
)
LoadTracersMassFractionsContainerDescription = GetTracersInitialConditionsTableLoader(
    case_description.TracersMassFractionsContainerDescription,
    "tracers_mass_fractions",
    "-",
    is_referenced=False,
)


def LoadInitialTracersMassFractionsDescription(
    document: DescriptionDocument,
) -> case_description.InitialTracersMassFractionsDescription:
    alfacase_to_case_description = {
        "position_input_type": GetEnumLoader(enum_class=constants.TableInputType),
        "table_x": LoadReferencedTracersMassFractionsContainerDescription,
        "table_y": LoadReferencedTracersMassFractionsContainerDescription,
        "table_length": LoadTracersMassFractionsContainerDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.InitialTracersMassFractionsDescription(**case_values)


def LoadInitialConditionsDescription(
    document: DescriptionDocument,
) -> case_description.InitialConditionsDescription:
    alfacase_to_case_description = {
        "velocities": LoadInitialVelocitiesDescription,
        "temperatures": LoadInitialTemperaturesDescription,
        "volume_fractions": LoadInitialVolumeFractionsDescription,
        "pressures": LoadInitialPressuresDescription,
        "tracers_mass_fractions": LoadInitialTracersMassFractionsDescription,
        "initial_fluid": LoadValue,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.InitialConditionsDescription(**case_values)


def _LoadMassSourceCommon() -> Dict[str, Callable]:
    return {
        "fluid": LoadValue,
        "temperature": GetScalarLoader(from_unit="K"),
        "tracer_mass_fraction": GetArrayLoader(category="mass fraction"),
        "water_cut": GetScalarLoader(category="volume fraction"),
        "gas_oil_ratio": GetScalarLoader(from_unit="sm3/sm3"),
        "source_type": GetEnumLoader(enum_class=constants.MassSourceType),
        "volumetric_flow_rates_std": GetDictWithScalarLoader(
            category="volume flow rate"
        ),
        "mass_flow_rates": GetDictWithScalarLoader(category="mass flow rate"),
        "total_mass_flow_rate": GetScalarLoader(from_unit="kg/s"),
    }


def LoadMassSourceEquipmentDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.MassSourceEquipmentDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "position": GetScalarLoader(from_unit="m"),
        "material_above_filler": LoadValue,
    }
    alfacase_to_case_description.update(**_LoadMassSourceCommon())

    def GenerateMassSourceDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.MassSourceEquipmentDescription(**case_values)

    return {
        key.data: GenerateMassSourceDescription(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadMaterialDescription(
    document: DescriptionDocument,
) -> List[case_description.MaterialDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "material_type": GetEnumLoader(enum_class=constants.MaterialType),
        "density": GetScalarLoader(from_unit="kg/m3"),
        "heat_capacity": GetScalarLoader(from_unit="J/kg.degC"),
        "thermal_conductivity": GetScalarLoader(from_unit="W/m.degC"),
        "inner_emissivity": GetScalarLoader(category="emissivity"),
        "outer_emissivity": GetScalarLoader(category="emissivity"),
        "expansion": GetScalarLoader(from_unit="1/K"),
        "viscosity": GetScalarLoader(from_unit="cP"),
    }

    def GenerateMaterialsDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.MaterialDescription(**case_values)

    return [
        GenerateMaterialsDescription(alfacase_document)
        for alfacase_document in document
    ]


def LoadInternalNodePropertiesDescription(
    document: DescriptionDocument,
) -> case_description.InternalNodePropertiesDescription:
    alfacase_to_case_description = {"fluid": LoadValue}
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.InternalNodePropertiesDescription(**case_values)


def LoadMassSourceNodePropertiesDescription(
    document: DescriptionDocument,
) -> case_description.MassSourceNodePropertiesDescription:
    case_values = ToCaseValues(document, _LoadMassSourceCommon())
    return case_description.MassSourceNodePropertiesDescription(**case_values)


def LoadPressureNodePropertiesDescription(
    document: DescriptionDocument,
) -> case_description.PressureNodePropertiesDescription:
    case_values = ToCaseValues(document, _LoadPressureSourceCommon())
    return case_description.PressureNodePropertiesDescription(**case_values)


def LoadSeparatorNodePropertiesDescription(
    document: DescriptionDocument,
) -> case_description.SeparatorNodePropertiesDescription:
    alfacase_to_case_description = {
        "environment_temperature": GetScalarLoader(from_unit="K"),
        "geometry": GetEnumLoader(enum_class=constants.SeparatorGeometryType),
        "length": GetScalarLoader(from_unit="m"),
        "overall_heat_transfer_coefficient": GetScalarLoader(from_unit="W/m2.K"),
        "radius": GetScalarLoader(from_unit="m"),
        "nozzles": GetDictWithScalarLoader(category=GetCategoryFor("m")),
        "initial_phase_volume_fractions": GetDictWithScalarLoader(
            category="volume fraction"
        ),
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.SeparatorNodePropertiesDescription(**case_values)


def LoadNodeDescription(
    document: DescriptionDocument,
) -> List[case_description.NodeDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "node_type": GetEnumLoader(enum_class=constants.NodeCellType),
        "pvt_model": LoadValue,
        "pressure_properties": LoadPressureNodePropertiesDescription,
        "mass_source_properties": LoadMassSourceNodePropertiesDescription,
        "internal_properties": LoadInternalNodePropertiesDescription,
        "separator_properties": LoadSeparatorNodePropertiesDescription,
    }

    def GenerateNodeDescription(
        document: DescriptionDocument,
    ) -> case_description.NodeDescription:
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.NodeDescription(**case_values)

    return [
        GenerateNodeDescription(alfacase_document) for alfacase_document in document
    ]


def LoadOpeningCurveDescription(
    document: DescriptionDocument,
) -> case_description.OpeningCurveDescription:
    alfacase_to_case_description = {
        "time": GetArrayLoader(from_unit="s"),
        "opening": GetArrayLoader(from_unit="-"),
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.OpeningCurveDescription(**case_values)


def LoadPackerDescription(
    document: DescriptionDocument,
) -> List[case_description.PackerDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "position": GetScalarLoader(from_unit="m"),
        "material_above": LoadValue,
    }

    def GeneratePackerDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.PackerDescription(**case_values)

    return [
        GeneratePackerDescription(alfacase_document) for alfacase_document in document
    ]


def LoadPipeSegmentsDescription(
    document: DescriptionDocument,
) -> case_description.PipeSegmentsDescription:
    alfacase_to_case_description = {
        "start_positions": GetArrayLoader(from_unit="m"),
        "diameters": GetArrayLoader(from_unit="m"),
        "roughnesses": GetArrayLoader(from_unit="m"),
        "wall_names": LoadValue,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.PipeSegmentsDescription(**case_values)


def LoadProfileOutputDescription(
    document: DescriptionDocument,
) -> List[case_description.ProfileOutputDescription]:
    alfacase_to_case_description = {
        "curve_names": LoadValue,
        "element_name": LoadValue,
        "location": GetEnumLoader(enum_class=constants.OutputAttachmentLocation),
    }

    def GenerateProfileDefinitions(
        document: DescriptionDocument,
    ) -> case_description.ProfileOutputDescription:
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.ProfileOutputDescription(**case_values)

    return [
        GenerateProfileDefinitions(alfacase_document) for alfacase_document in document
    ]


def LoadLinearIPRDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.LinearIPRDescription]:
    alfacase_to_case_description = {
        "well_index_phase": GetEnumLoader(enum_class=constants.WellIndexPhaseType),
        "min_pressure_difference": GetScalarLoader(from_unit="Pa"),
        "well_index": GetScalarLoader(from_unit="m3/bar.d"),
    }

    def GenerateLinearIPRCorrelation(value: DescriptionDocument):
        case_values = ToCaseValues(value, alfacase_to_case_description)
        return case_description.LinearIPRDescription(**case_values)

    return {
        key.data: GenerateLinearIPRCorrelation(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadIPRCurveDescription(
    document: DescriptionDocument,
) -> case_description.IPRCurveDescription:
    alfacase_to_case_description = {
        "pressure_difference": GetArrayLoader(from_unit="Pa"),
        "flow_rate": GetArrayLoader(from_unit="sm3/d"),
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.IPRCurveDescription(**case_values)


def LoadTableIPRDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.LinearIPRDescription]:
    alfacase_to_case_description = {
        "well_index_phase": GetEnumLoader(enum_class=constants.WellIndexPhaseType),
        "table": LoadIPRCurveDescription,
    }

    def GenerateTableIPRCorrelation(value: DescriptionDocument):
        case_values = ToCaseValues(value, alfacase_to_case_description)
        return case_description.TableIPRDescription(**case_values)

    return {
        key.data: GenerateTableIPRCorrelation(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadIPRModelsDescription(
    document: DescriptionDocument,
) -> case_description.IPRModelsDescription:
    alfacase_to_case_description = {
        "linear_models": LoadLinearIPRDescription,
        "table_models": LoadTableIPRDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.IPRModelsDescription(**case_values)


def _LoadPressureSourceCommon() -> Dict[str, Callable]:
    return {
        "fluid": LoadValue,
        "tracer_mass_fraction": GetArrayLoader(category="mass fraction"),
        "split_type": GetEnumLoader(enum_class=constants.MassInflowSplitType),
        "mass_fractions": GetDictWithScalarLoader(category="mass fraction"),
        "volume_fractions": GetDictWithScalarLoader(category="volume fraction"),
        "water_cut": GetScalarLoader(category="volume fraction"),
        "gas_oil_ratio": GetScalarLoader(from_unit="sm3/sm3"),
        "gas_liquid_ratio": GetScalarLoader(from_unit="sm3/sm3"),
        "pressure": GetScalarLoader(from_unit="bar"),
        "temperature": GetScalarLoader(from_unit="K"),
    }


def LoadReservoirInflowEquipmentDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.ReservoirInflowEquipmentDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "fluid": LoadValue,
        "start": GetScalarLoader(from_unit="m"),
        "length": GetScalarLoader(from_unit="m"),
        "pressure": GetScalarLoader(from_unit="bar"),
        "temperature": GetScalarLoader(from_unit="degC"),
        "productivity_IPR": LoadValue,
        "injectivity_IPR": LoadValue,
        "tracer_mass_fraction": GetArrayLoader(category="mass fraction"),
    }
    alfacase_to_case_description.update(**_LoadPressureSourceCommon())

    def GenerateReservoirInflowDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.ReservoirInflowEquipmentDescription(**case_values)

    return {
        key.data: GenerateReservoirInflowDescription(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadSpeedCurveDescription(
    document: DescriptionDocument,
) -> case_description.SpeedCurveDescription:
    alfacase_to_case_description = {
        "time": GetArrayLoader(from_unit="s"),
        "speed": GetArrayLoader(from_unit="rpm"),
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.SpeedCurveDescription(**case_values)


def LoadTablePumpDescription(
    document: DescriptionDocument,
) -> case_description.TablePumpDescription:
    alfacase_to_case_description = {
        "speeds": GetArrayLoader(from_unit="rpm"),
        "void_fractions": GetArrayLoader(category="volume fraction"),
        "flow_rates": GetArrayLoader(category="volume flow rate"),
        "pressure_boosts": GetArrayLoader(from_unit="bar"),
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.TablePumpDescription(**case_values)


def LoadTrendOutputDescription(
    document: DescriptionDocument,
) -> List[case_description.TrendOutputDescription]:
    alfacase_to_case_description = {
        "curve_names": LoadValue,
        "location": GetEnumLoader(enum_class=constants.OutputAttachmentLocation),
        "element_name": LoadValue,
        "position": GetScalarLoader(from_unit="m"),
    }

    def GenerateTrendDescription(
        document: DescriptionDocument,
    ) -> case_description.TrendOutputDescription:
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.TrendOutputDescription(**case_values)

    return [
        GenerateTrendDescription(alfacase_document) for alfacase_document in document
    ]


def LoadTubingDescription(
    document: DescriptionDocument,
) -> List[case_description.TubingDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "length": GetScalarLoader(from_unit="m"),
        "outer_diameter": GetScalarLoader(from_unit="m"),
        "inner_diameter": GetScalarLoader(from_unit="m"),
        "inner_roughness": GetScalarLoader(from_unit="m"),
        "material": LoadValue,
    }

    def GenerateTubingsDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.TubingDescription(**case_values)

    return [
        GenerateTubingsDescription(alfacase_document) for alfacase_document in document
    ]


def LoadWallLayerDescription(
    document: DescriptionDocument,
) -> List[case_description.WallLayerDescription]:
    alfacase_to_case_description = {
        "thickness": GetScalarLoader(from_unit="m"),
        "material_name": LoadValue,
        "has_annulus_flow": LoadValue,
    }

    def GenerateWallLayerContainerDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.WallLayerDescription(**case_values)

    return [
        GenerateWallLayerContainerDescription(alfacase_document)
        for alfacase_document in document
    ]


def LoadAnnulusDescription(
    document: DescriptionDocument,
) -> case_description.AnnulusDescription:
    alfacase_to_case_description = {
        "has_annulus_flow": LoadValue,
        "pvt_model": LoadValue,
        "top_node": LoadValue,
        "initial_conditions": LoadInitialConditionsDescription,
        "gas_lift_valve_equipment": LoadGasLiftValveEquipmentDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.AnnulusDescription(**case_values)


def LoadCaseOutputDescription(
    document: DescriptionDocument,
) -> case_description.CaseOutputDescription:
    alfacase_to_case_description = {
        "profiles": LoadProfileOutputDescription,
        "trends": LoadTrendOutputDescription,
        "profile_frequency": GetScalarLoader(from_unit="s"),
        "trend_frequency": GetScalarLoader(from_unit="s"),
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.CaseOutputDescription(**case_values)


def LoadOpenHoleDescription(
    document: DescriptionDocument,
) -> List[case_description.OpenHoleDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "length": GetScalarLoader(from_unit="m"),
        "diameter": GetScalarLoader(from_unit="m"),
        "inner_roughness": GetScalarLoader(from_unit="m"),
    }

    def GenerateOpenHoleDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.OpenHoleDescription(**case_values)

    return [
        GenerateOpenHoleDescription(alfacase_document) for alfacase_document in document
    ]


def LoadCasingDescription(
    document: DescriptionDocument,
) -> case_description.CasingDescription:
    alfacase_to_case_description = {
        "casing_sections": LoadCasingSectionDescription,
        "tubings": LoadTubingDescription,
        "packers": LoadPackerDescription,
        "open_holes": LoadOpenHoleDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.CasingDescription(**case_values)


def LoadCompressorPressureTableDescription(
    document: DescriptionDocument,
) -> case_description.CompressorPressureTableDescription:
    alfacase_to_case_description = {
        "speed_entries": GetArrayLoader(from_unit="rpm"),
        "corrected_mass_flow_rate_entries": GetArrayLoader(from_unit="kg/s"),
        "pressure_ratio_table": GetArrayLoader(from_unit="-"),
        "isentropic_efficiency_table": GetArrayLoader(from_unit="-"),
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.CompressorPressureTableDescription(**case_values)


def LoadCompressorEquipmentDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.CompressorEquipmentDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "position": GetScalarLoader(from_unit="m"),
        "table": LoadCompressorPressureTableDescription,
        "speed_curve": LoadSpeedCurveDescription,
        "reference_pressure": GetScalarLoader(from_unit="bar"),
        "reference_temperature": GetScalarLoader(from_unit="degC"),
        "constant_speed": GetScalarLoader(from_unit="rpm"),
        "compressor_type": GetEnumLoader(enum_class=constants.CompressorSpeedType),
        "speed_curve_interpolation_type": GetEnumLoader(
            enum_class=constants.InterpolationType
        ),
        "flow_direction": GetEnumLoader(enum_class=constants.FlowDirection),
    }

    def GenerateCompressorDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.CompressorEquipmentDescription(**case_values)

    return {
        key.data: GenerateCompressorDescription(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadEnvironmentDescription(
    document: DescriptionDocument,
) -> case_description.EnvironmentDescription:
    alfacase_to_case_description = {
        "thermal_model": GetEnumLoader(enum_class=constants.PipeThermalModelType),
        "position_input_mode": GetEnumLoader(
            enum_class=constants.PipeThermalPositionInput
        ),
        "reference_y_coordinate": GetScalarLoader(from_unit="m"),
        "md_properties_table": LoadEnvironmentPropertyDescription,
        "tvd_properties_table": LoadEnvironmentPropertyDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.EnvironmentDescription(**case_values)


def LoadFormationDescription(
    document: DescriptionDocument,
) -> case_description.FormationDescription:
    alfacase_to_case_description = {
        "reference_y_coordinate": GetScalarLoader(from_unit="m"),
        "layers": LoadFormationLayerDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.FormationDescription(**case_values)


def LoadPumpEquipmentDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.PumpEquipmentDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "position": GetScalarLoader(from_unit="m"),
        "type": GetEnumLoader(enum_class=constants.PumpType),
        "pressure_boost": GetScalarLoader(from_unit="Pa"),
        "thermal_efficiency": GetScalarLoader(from_unit="-"),
        "table": LoadTablePumpDescription,
        "speed_curve": LoadSpeedCurveDescription,
        "speed_curve_interpolation_type": GetEnumLoader(
            enum_class=constants.InterpolationType
        ),
        "flow_direction": GetEnumLoader(enum_class=constants.FlowDirection),
    }

    def GeneratePumpDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.PumpEquipmentDescription(**case_values)

    return {
        key.data: GeneratePumpDescription(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadValveEquipmentDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.ValveEquipmentDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "position": GetScalarLoader(from_unit="m"),
        "type": GetEnumLoader(enum_class=constants.ValveType),
        "diameter": GetScalarLoader(from_unit="m"),
        "opening_type": GetEnumLoader(enum_class=constants.ValveOpeningType),
        "opening": GetScalarLoader(from_unit="-"),
        "opening_curve_interpolation_type": GetEnumLoader(
            enum_class=constants.InterpolationType
        ),
        "opening_curve": LoadOpeningCurveDescription,
        "cv_table": LoadCvTableDescription,
        "flow_direction": GetEnumLoader(enum_class=constants.FlowDirection),
    }

    def GenerateValveDescription(document: DescriptionDocument):

        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.ValveEquipmentDescription(**case_values)

    return {
        key.data: GenerateValveDescription(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadWallDescription(
    document: DescriptionDocument,
) -> List[case_description.WallDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "inner_roughness": GetScalarLoader(from_unit="m"),
        "wall_layer_container": LoadWallLayerDescription,
    }

    def GenerateWallsDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.WallDescription(**case_values)

    return [
        GenerateWallsDescription(alfacase_document) for alfacase_document in document
    ]


def LoadEquipmentDescription(
    document: DescriptionDocument,
) -> case_description.EquipmentDescription:
    alfacase_to_case_description = {
        "mass_sources": LoadMassSourceEquipmentDescription,
        "pumps": LoadPumpEquipmentDescription,
        "valves": LoadValveEquipmentDescription,
        "reservoir_inflows": LoadReservoirInflowEquipmentDescription,
        "heat_sources": LoadHeatSourceEquipmentDescription,
        "compressors": LoadCompressorEquipmentDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.EquipmentDescription(**case_values)


def LoadXAndYDescription(
    document: DescriptionDocument,
) -> case_description.XAndYDescription:
    alfacase_to_case_description = {
        "x": GetArrayLoader(from_unit="m"),
        "y": GetArrayLoader(from_unit="m"),
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.XAndYDescription(**case_values)


def LoadLengthAndElevationDescription(
    document: DescriptionDocument,
) -> case_description.LengthAndElevationDescription:
    alfacase_to_case_description = {
        "length": GetArrayLoader(from_unit="m"),
        "elevation": GetArrayLoader(from_unit="m"),
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.LengthAndElevationDescription(**case_values)


def LoadProfileDescription(
    document: DescriptionDocument,
) -> case_description.ProfileDescription:
    alfacase_to_case_description = {
        "x_and_y": LoadXAndYDescription,
        "length_and_elevation": LoadLengthAndElevationDescription,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.ProfileDescription(**case_values)


def LoadPipeDescription(
    document: DescriptionDocument,
) -> List[case_description.PipeDescription]:
    # fmt: off
    alfacase_to_case_description = {
        "environment": LoadEnvironmentDescription,
        "equipment": LoadEquipmentDescription,
        "initial_conditions": LoadInitialConditionsDescription,
        "profile": LoadProfileDescription,
        "name": LoadValue,
        "pvt_model": LoadValue,
        "segments": LoadPipeSegmentsDescription,
        "source": LoadValue,
        "target": LoadValue,
    }
    # fmt: on
    def GeneratePipesDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.PipeDescription(**case_values)

    return [
        GeneratePipesDescription(alfacase_document) for alfacase_document in document
    ]


def LoadWellDescription(
    document: DescriptionDocument,
) -> List[case_description.WellDescription]:
    alfacase_to_case_description = {
        "name": LoadValue,
        "pvt_model": LoadValue,
        "stagnant_fluid": LoadValue,
        "profile": LoadProfileDescription,
        "casing": LoadCasingDescription,
        "annulus": LoadAnnulusDescription,
        "top_node": LoadValue,
        "bottom_node": LoadValue,
        "initial_conditions": LoadInitialConditionsDescription,
        "environment": LoadEnvironmentDescription,
        "equipment": LoadEquipmentDescription,
        "formation": LoadFormationDescription,
    }

    def GenerateWellsDescription(document: DescriptionDocument):
        case_values = ToCaseValues(document, alfacase_to_case_description)
        return case_description.WellDescription(**case_values)

    return [
        GenerateWellsDescription(alfacase_document) for alfacase_document in document
    ]


def LoadPhysicsDescription(
    document: DescriptionDocument,
) -> case_description.PhysicsDescription:
    # fmt: off
    alfacase_to_case_description = {
        'hydrodynamic_model': GetEnumLoader(enum_class=constants.HydrodynamicModelType),
        'simulation_regime': GetEnumLoader(enum_class=constants.SimulationRegimeType),
        'energy_model': GetEnumLoader(enum_class=constants.EnergyModel),
        'solids_model': GetEnumLoader(enum_class=constants.SolidsModelType),
        'initial_condition_strategy': GetEnumLoader(enum_class=constants.InitialConditionStrategyType),
        'restart_filepath': LoadPath,
        'keep_former_results': LoadValue,
        'emulsion_model': GetEnumLoader(enum_class=constants.EmulsionModelType),
        'flash_model': GetEnumLoader(enum_class=constants.FlashModel),
        'correlations_package': GetEnumLoader(enum_class=constants.CorrelationPackageType),
    }
    # fmt: on
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.PhysicsDescription(**case_values)


# fmt: off
def LoadNumericalOptionsDescription(document: DescriptionDocument) -> case_description.NumericalOptionsDescription:
    alfacase_to_case_description = {
        'tolerance': LoadValue,
        'maximum_iterations': LoadValue,
        'maximum_timestep_change_factor': LoadValue,
        'maximum_cfl_value': LoadValue,
        'nonlinear_solver_type': GetEnumLoader(enum_class=constants.NonlinearSolverType),
        'relaxed_tolerance': LoadValue,
        'divergence_tolerance': LoadValue,
        'friction_factor_evaluation_strategy': GetEnumLoader(enum_class=constants.EvaluationStrategyType),
        'simulation_mode': GetEnumLoader(enum_class=constants.SimulationModeType),
        'enable_solver_caching': LoadValue,
        'caching_rtol': LoadValue,
        'caching_atol': LoadValue,
        'always_repeat_timestep': LoadValue,
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.NumericalOptionsDescription(**case_values)
# fmt: on

# fmt: off
def LoadTimeOptionsDescription(
    document: DescriptionDocument
) -> case_description.TimeOptionsDescription:
    alfacase_to_case_description = {
        "stop_on_steady_state": LoadValue,
        "initial_time": GetScalarLoader(from_unit="h"),
        "final_time": GetScalarLoader(from_unit="h"),
        "initial_timestep": GetScalarLoader(from_unit="s"),
        "minimum_timestep": GetScalarLoader(from_unit="s"),
        "maximum_timestep": GetScalarLoader(from_unit="s"),
        "restart_autosave_frequency": GetScalarLoader(from_unit="h"),
        "minimum_time_for_steady_state_stop": GetScalarLoader(from_unit="s"),
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.TimeOptionsDescription(**case_values)


# fmt: on


def LoadTracerModelConstantCoefficientsDescription(
    document: DescriptionDocument,
) -> Dict[str, case_description.TracerModelConstantCoefficientsDescription]:
    alfacase_to_case_description = {
        "partition_coefficients": GetDictWithScalarLoader(category="mass fraction")
    }

    def GenerateTracerModelConstantCoefficientsDescription(value: DescriptionDocument):
        case_values = ToCaseValues(value, alfacase_to_case_description)
        return case_description.TracerModelConstantCoefficientsDescription(
            **case_values
        )

    return {
        key.data: GenerateTracerModelConstantCoefficientsDescription(
            DescriptionDocument(value, document.file_path)
        )
        for key, value in document.content.items()
    }


def LoadTracersDescription(
    document: DescriptionDocument,
) -> case_description.TracersDescription:
    alfacase_to_case_description = {
        "constant_coefficients": LoadTracerModelConstantCoefficientsDescription
    }
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.TracersDescription(**case_values)


def LoadCaseDescription(
    document: DescriptionDocument,
) -> case_description.CaseDescription:
    # fmt: off
    alfacase_to_case_description = {
        'physics': LoadPhysicsDescription,
        'numerical_options': LoadNumericalOptionsDescription,
        'time_options': LoadTimeOptionsDescription,
        'max_timestep_change_factor': LoadValue,
        'max_cfl_value': LoadValue,
        'friction_factor_evaluation_strategy': GetEnumLoader(enum_class=constants.EvaluationStrategyType),
        'name': LoadValue,
        'positions': LoadValue,
        'tracers': LoadTracersDescription,
        'ipr_models': LoadIPRModelsDescription,
        'pvt_models': LoadPvtModelsDescription,
        'materials': LoadMaterialDescription,
        'nodes': LoadNodeDescription,
        'outputs': LoadCaseOutputDescription,
        'pipes': LoadPipeDescription,
        'walls': LoadWallDescription,
        'wells': LoadWellDescription,
    }
    # fmt: on
    case_values = ToCaseValues(document, alfacase_to_case_description)
    return case_description.CaseDescription(**case_values)
