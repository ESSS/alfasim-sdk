# -*- coding: utf-8 -*-
"""Top-level package for alfasim-sdk."""
import pluggy

from _alfasim_sdk import version
from _alfasim_sdk.units import register_units

# Package information
__author__ = "ESSS"
__email__ = "foss@esss.co"
__version__ = version.__version__

# Register new categories and units used from CaseDescription
register_units()

# Register ALFASim-SDK Hooks
hookimpl = pluggy.HookimplMarker("ALFAsim")


def get_alfasim_sdk_api_path():
    """
    Return the directory that contains the alfasim_sdk_api with the header files
    """
    from _alfasim_sdk import hook_specs
    from pathlib import Path

    return str(Path(hook_specs.__file__).parents[1])


# CLI:
from _alfasim_sdk.cli import console_main

# ALFACase: Descriptions
from _alfasim_sdk.alfacase.case_description import AnnulusDescription
from _alfasim_sdk.alfacase.case_description import BipDescription
from _alfasim_sdk.alfacase.case_description import CaseDescription
from _alfasim_sdk.alfacase.case_description import CaseOutputDescription
from _alfasim_sdk.alfacase.case_description import CasingDescription
from _alfasim_sdk.alfacase.case_description import CasingSectionDescription
from _alfasim_sdk.alfacase.case_description import CompositionDescription
from _alfasim_sdk.alfacase.case_description import CompressorEquipmentDescription
from _alfasim_sdk.alfacase.case_description import CompressorPressureTableDescription
from _alfasim_sdk.alfacase.case_description import CvTableDescription
from _alfasim_sdk.alfacase.case_description import EnvironmentDescription
from _alfasim_sdk.alfacase.case_description import EnvironmentPropertyDescription
from _alfasim_sdk.alfacase.case_description import EquipmentDescription
from _alfasim_sdk.alfacase.case_description import FluidDescription
from _alfasim_sdk.alfacase.case_description import FormationDescription
from _alfasim_sdk.alfacase.case_description import FormationLayerDescription
from _alfasim_sdk.alfacase.case_description import GasLiftValveEquipmentDescription
from _alfasim_sdk.alfacase.case_description import HeatSourceEquipmentDescription
from _alfasim_sdk.alfacase.case_description import HeavyComponentDescription
from _alfasim_sdk.alfacase.case_description import IPRCurveDescription
from _alfasim_sdk.alfacase.case_description import IPRModelsDescription
from _alfasim_sdk.alfacase.case_description import InitialConditionsDescription
from _alfasim_sdk.alfacase.case_description import InitialPressuresDescription
from _alfasim_sdk.alfacase.case_description import InitialTemperaturesDescription
from _alfasim_sdk.alfacase.case_description import (
    InitialTracersMassFractionsDescription,
)
from _alfasim_sdk.alfacase.case_description import InitialVelocitiesDescription
from _alfasim_sdk.alfacase.case_description import InitialVolumeFractionsDescription
from _alfasim_sdk.alfacase.case_description import InternalNodePropertiesDescription
from _alfasim_sdk.alfacase.case_description import LengthAndElevationDescription
from _alfasim_sdk.alfacase.case_description import LightComponentDescription
from _alfasim_sdk.alfacase.case_description import LinearIPRDescription
from _alfasim_sdk.alfacase.case_description import MassSourceEquipmentDescription
from _alfasim_sdk.alfacase.case_description import MassSourceNodePropertiesDescription
from _alfasim_sdk.alfacase.case_description import MaterialDescription
from _alfasim_sdk.alfacase.case_description import NodeDescription
from _alfasim_sdk.alfacase.case_description import NumericalOptionsDescription
from _alfasim_sdk.alfacase.case_description import OpenHoleDescription
from _alfasim_sdk.alfacase.case_description import OpeningCurveDescription
from _alfasim_sdk.alfacase.case_description import PackerDescription
from _alfasim_sdk.alfacase.case_description import PhysicsDescription
from _alfasim_sdk.alfacase.case_description import PipeDescription
from _alfasim_sdk.alfacase.case_description import PipeSegmentsDescription
from _alfasim_sdk.alfacase.case_description import PressureContainerDescription
from _alfasim_sdk.alfacase.case_description import PressureNodePropertiesDescription
from _alfasim_sdk.alfacase.case_description import ProfileDescription
from _alfasim_sdk.alfacase.case_description import ProfileOutputDescription
from _alfasim_sdk.alfacase.case_description import PumpEquipmentDescription
from _alfasim_sdk.alfacase.case_description import PvtModelCompositionalDescription
from _alfasim_sdk.alfacase.case_description import PvtModelCorrelationDescription
from _alfasim_sdk.alfacase.case_description import PvtModelsDescription
from _alfasim_sdk.alfacase.case_description import PvtModelTableParametersDescription
from _alfasim_sdk.alfacase.case_description import (
    ReferencedPressureContainerDescription,
)
from _alfasim_sdk.alfacase.case_description import (
    ReferencedTemperaturesContainerDescription,
)
from _alfasim_sdk.alfacase.case_description import (
    ReferencedTracersMassFractionsContainerDescription,
)
from _alfasim_sdk.alfacase.case_description import (
    ReferencedVelocitiesContainerDescription,
)
from _alfasim_sdk.alfacase.case_description import (
    ReferencedVolumeFractionsContainerDescription,
)
from _alfasim_sdk.alfacase.case_description import ReservoirInflowEquipmentDescription
from _alfasim_sdk.alfacase.case_description import SeparatorNodePropertiesDescription
from _alfasim_sdk.alfacase.case_description import SpeedCurveDescription
from _alfasim_sdk.alfacase.case_description import TableIPRDescription
from _alfasim_sdk.alfacase.case_description import TablePumpDescription
from _alfasim_sdk.alfacase.case_description import TemperaturesContainerDescription
from _alfasim_sdk.alfacase.case_description import TimeOptionsDescription
from _alfasim_sdk.alfacase.case_description import (
    TracerModelConstantCoefficientsDescription,
)
from _alfasim_sdk.alfacase.case_description import TracersDescription
from _alfasim_sdk.alfacase.case_description import (
    TracersMassFractionsContainerDescription,
)
from _alfasim_sdk.alfacase.case_description import TrendOutputDescription
from _alfasim_sdk.alfacase.case_description import TubingDescription
from _alfasim_sdk.alfacase.case_description import ValveEquipmentDescription
from _alfasim_sdk.alfacase.case_description import VelocitiesContainerDescription
from _alfasim_sdk.alfacase.case_description import VolumeFractionsContainerDescription
from _alfasim_sdk.alfacase.case_description import WallDescription
from _alfasim_sdk.alfacase.case_description import WallLayerDescription
from _alfasim_sdk.alfacase.case_description import WellDescription
from _alfasim_sdk.alfacase.case_description import XAndYDescription

# ALFACase: Utilities
from _alfasim_sdk.alfacase.alfacase import convert_alfacase_to_case
from _alfasim_sdk.alfacase.alfacase import convert_description_to_alfacase
from _alfasim_sdk.alfacase.alfacase import generate_alfacase_file
from _alfasim_sdk.alfacase.alfatable import generate_alfatable_file
from _alfasim_sdk.alfacase.alfatable import (
    load_pvt_model_table_parameters_description_from_alfatable,
)

# Constants
from _alfasim_sdk.constants import BUBBLE_FIELD
from _alfasim_sdk.constants import CompressorSpeedType
from _alfasim_sdk.constants import CorrelationPackage
from _alfasim_sdk.constants import CorrelationPackageType
from _alfasim_sdk.constants import DEFAULT_TEMPERATURE_IN_K
from _alfasim_sdk.constants import DROPLET_FIELD
from _alfasim_sdk.constants import EXTRAS_REQUIRED_VERSION_KEY
from _alfasim_sdk.constants import EmulsionModelType
from _alfasim_sdk.constants import EnergyModel
from _alfasim_sdk.constants import EnergyModelPrimaryVariable
from _alfasim_sdk.constants import EquationOfStateType
from _alfasim_sdk.constants import EvaluationStrategyType
from _alfasim_sdk.constants import FLUID_GAS
from _alfasim_sdk.constants import FLUID_OIL
from _alfasim_sdk.constants import FLUID_PHASE_NAMES
from _alfasim_sdk.constants import FLUID_WATER
from _alfasim_sdk.constants import FlashModel
from _alfasim_sdk.constants import FlowDirection
from _alfasim_sdk.constants import GAS_FIELD
from _alfasim_sdk.constants import GAS_LAYER
from _alfasim_sdk.constants import GAS_PHASE
from _alfasim_sdk.constants import HydrodynamicModelType
from _alfasim_sdk.constants import InitialConditionStrategyType
from _alfasim_sdk.constants import InterpolationType
from _alfasim_sdk.constants import MassInflowSplitType
from _alfasim_sdk.constants import MassSourceType
from _alfasim_sdk.constants import MaterialType
from _alfasim_sdk.constants import NodeCellType
from _alfasim_sdk.constants import NonlinearSolverType
from _alfasim_sdk.constants import OIL_FIELD
from _alfasim_sdk.constants import OIL_LAYER
from _alfasim_sdk.constants import OIL_PHASE
from _alfasim_sdk.constants import OutputAttachmentLocation
from _alfasim_sdk.constants import PVTCompositionalViscosityModel
from _alfasim_sdk.constants import PipeEnvironmentHeatTransferCoefficientModelType
from _alfasim_sdk.constants import PipeThermalModelType
from _alfasim_sdk.constants import PipeThermalPositionInput
from _alfasim_sdk.constants import PumpType
from _alfasim_sdk.constants import SOLID_PHASE
from _alfasim_sdk.constants import SeparatorGeometryType
from _alfasim_sdk.constants import SimulationModeType
from _alfasim_sdk.constants import SimulationRegimeType
from _alfasim_sdk.constants import SolidsModelType
from _alfasim_sdk.constants import SurfaceTensionType
from _alfasim_sdk.constants import TableInputType
from _alfasim_sdk.constants import TracerModelType
from _alfasim_sdk.constants import ValveOpeningType
from _alfasim_sdk.constants import ValveType
from _alfasim_sdk.constants import WATER_DROPLET_IN_OIL_FIELD
from _alfasim_sdk.constants import WATER_FIELD
from _alfasim_sdk.constants import WATER_LAYER
from _alfasim_sdk.constants import WATER_PHASE
from _alfasim_sdk.constants import WellConnectionPort
from _alfasim_sdk.constants import WellIndexPhaseType

# Plugins: Layouts imports
from _alfasim_sdk.layout import tab
from _alfasim_sdk.layout import tabs
from _alfasim_sdk.layout import group

# Plugins: Models imports
from _alfasim_sdk.models import container_model
from _alfasim_sdk.models import data_model

# Plugins: Status imports
from _alfasim_sdk.status import WarningMessage
from _alfasim_sdk.status import ErrorMessage

# Plugins: Types for configure_fields hook
from _alfasim_sdk.types import AddField

# Plugins: Types for configure_phases hook
from _alfasim_sdk.types import AddPhase
from _alfasim_sdk.types import UpdatePhase

# Plugins: Types for configure_layers hook
from _alfasim_sdk.types import AddLayer
from _alfasim_sdk.types import UpdateLayer

# Plugins: Types  for UI customization
from _alfasim_sdk.types import Boolean
from _alfasim_sdk.types import Enum
from _alfasim_sdk.types import FileContent
from _alfasim_sdk.types import MultipleReference
from _alfasim_sdk.types import Quantity
from _alfasim_sdk.types import Reference
from _alfasim_sdk.types import String
from _alfasim_sdk.types import Table
from _alfasim_sdk.types import TableColumn
from _alfasim_sdk.types import TracerType

# Plugins: Type for alfasim_get_additional_variables hook
from _alfasim_sdk.variables import SecondaryVariable

# Plugins: Constants used on SecondaryVariable
from _alfasim_sdk.variables import Visibility
from _alfasim_sdk.variables import Scope
from _alfasim_sdk.variables import Type
from _alfasim_sdk.variables import Location

__all__ = [
    "console_main",
    "AnnulusDescription",
    "BipDescription",
    "CaseDescription",
    "CaseOutputDescription",
    "CasingDescription",
    "CasingSectionDescription",
    "CompositionDescription",
    "CompressorEquipmentDescription",
    "CompressorPressureTableDescription",
    "CvTableDescription",
    "EnvironmentDescription",
    "EnvironmentPropertyDescription",
    "EquipmentDescription",
    "FluidDescription",
    "FormationDescription",
    "FormationLayerDescription",
    "GasLiftValveEquipmentDescription",
    "HeatSourceEquipmentDescription",
    "HeavyComponentDescription",
    "IPRCurveDescription",
    "IPRModelsDescription",
    "InitialConditionsDescription",
    "InitialPressuresDescription",
    "InitialTemperaturesDescription",
    "InitialTracersMassFractionsDescription",
    "InitialVelocitiesDescription",
    "InitialVolumeFractionsDescription",
    "InternalNodePropertiesDescription",
    "LengthAndElevationDescription",
    "LightComponentDescription",
    "LinearIPRDescription",
    "MassSourceEquipmentDescription",
    "MassSourceNodePropertiesDescription",
    "MaterialDescription",
    "NodeDescription",
    "NumericalOptionsDescription",
    "OpenHoleDescription",
    "OpeningCurveDescription",
    "PackerDescription",
    "PhysicsDescription",
    "PipeDescription",
    "PipeSegmentsDescription",
    "PressureContainerDescription",
    "PressureNodePropertiesDescription",
    "ProfileDescription",
    "ProfileOutputDescription",
    "PumpEquipmentDescription",
    "PvtModelCompositionalDescription",
    "PvtModelCorrelationDescription",
    "PvtModelsDescription",
    "PvtModelTableParametersDescription",
    "ReferencedPressureContainerDescription",
    "ReferencedTemperaturesContainerDescription",
    "ReferencedTracersMassFractionsContainerDescription",
    "ReferencedVelocitiesContainerDescription",
    "ReferencedVolumeFractionsContainerDescription",
    "ReservoirInflowEquipmentDescription",
    "SeparatorNodePropertiesDescription",
    "SpeedCurveDescription",
    "TableIPRDescription",
    "TablePumpDescription",
    "TemperaturesContainerDescription",
    "TimeOptionsDescription",
    "TracerModelConstantCoefficientsDescription",
    "TracersDescription",
    "TracersMassFractionsContainerDescription",
    "TrendOutputDescription",
    "TubingDescription",
    "ValveEquipmentDescription",
    "VelocitiesContainerDescription",
    "VolumeFractionsContainerDescription",
    "WallDescription",
    "WallLayerDescription",
    "WellDescription",
    "XAndYDescription",
    "convert_alfacase_to_case",
    "convert_description_to_alfacase",
    "generate_alfacase_file",
    "generate_alfatable_file",
    "load_pvt_model_table_parameters_description_from_alfatable",
    "BUBBLE_FIELD",
    "CompressorSpeedType",
    "CorrelationPackage",
    "CorrelationPackageType",
    "DEFAULT_TEMPERATURE_IN_K",
    "DROPLET_FIELD",
    "EXTRAS_REQUIRED_VERSION_KEY",
    "EmulsionModelType",
    "EnergyModel",
    "EnergyModelPrimaryVariable",
    "EquationOfStateType",
    "EvaluationStrategyType",
    "FLUID_GAS",
    "FLUID_OIL",
    "FLUID_PHASE_NAMES",
    "FLUID_WATER",
    "FlashModel",
    "FlowDirection",
    "GAS_FIELD",
    "GAS_LAYER",
    "GAS_PHASE",
    "HydrodynamicModelType",
    "InitialConditionStrategyType",
    "InterpolationType",
    "MassInflowSplitType",
    "MassSourceType",
    "MaterialType",
    "NodeCellType",
    "NonlinearSolverType",
    "OIL_FIELD",
    "OIL_LAYER",
    "OIL_PHASE",
    "OutputAttachmentLocation",
    "PVTCompositionalViscosityModel",
    "PipeEnvironmentHeatTransferCoefficientModelType",
    "PipeThermalModelType",
    "PipeThermalPositionInput",
    "PumpType",
    "SOLID_PHASE",
    "SeparatorGeometryType",
    "SimulationModeType",
    "SimulationRegimeType",
    "SolidsModelType",
    "SurfaceTensionType",
    "TableInputType",
    "TracerModelType",
    "ValveOpeningType",
    "ValveType",
    "WATER_DROPLET_IN_OIL_FIELD",
    "WATER_FIELD",
    "WATER_LAYER",
    "WATER_PHASE",
    "WellConnectionPort",
    "WellIndexPhaseType",
    "tab",
    "tabs",
    "group",
    "container_model",
    "data_model",
    "WarningMessage",
    "ErrorMessage",
    "AddField",
    "AddPhase",
    "UpdatePhase",
    "AddLayer",
    "UpdateLayer",
    "Boolean",
    "Enum",
    "FileContent",
    "MultipleReference",
    "Quantity",
    "Reference",
    "String",
    "Table",
    "TableColumn",
    "TracerType",
    "SecondaryVariable",
    "Visibility",
    "Scope",
    "Type",
    "Location",
]
