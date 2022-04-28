# -*- coding: utf-8 -*-
"""Top-level package for alfasim-sdk."""
import pluggy

from alfasim_sdk._internal import version
from alfasim_sdk._internal.alfasim_sdk_utils import get_metadata
from alfasim_sdk._internal.units import register_units

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
    from alfasim_sdk._internal import hook_specs
    from pathlib import Path

    return str(Path(hook_specs.__file__).parents[1])


# CLI:
from alfasim_sdk._internal.cli import console_main

# ALFACase: Descriptions
from alfasim_sdk._internal.alfacase.case_description import AnnulusDescription
from alfasim_sdk._internal.alfacase.case_description import BipDescription
from alfasim_sdk._internal.alfacase.case_description import CaseDescription
from alfasim_sdk._internal.alfacase.case_description import CaseOutputDescription
from alfasim_sdk._internal.alfacase.case_description import CasingDescription
from alfasim_sdk._internal.alfacase.case_description import CasingSectionDescription
from alfasim_sdk._internal.alfacase.case_description import CompositionDescription
from alfasim_sdk._internal.alfacase.case_description import (
    CompressorEquipmentDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    CompressorPressureTableDescription,
)
from alfasim_sdk._internal.alfacase.case_description import CvTableDescription
from alfasim_sdk._internal.alfacase.case_description import EnvironmentDescription
from alfasim_sdk._internal.alfacase.case_description import (
    EnvironmentPropertyDescription,
)
from alfasim_sdk._internal.alfacase.case_description import EquipmentDescription
from alfasim_sdk._internal.alfacase.case_description import AnnulusEquipmentDescription
from alfasim_sdk._internal.alfacase.case_description import CombinedFluidDescription
from alfasim_sdk._internal.alfacase.case_description import (
    CompositionalFluidDescription,
)
from alfasim_sdk._internal.alfacase.case_description import FormationDescription
from alfasim_sdk._internal.alfacase.case_description import FormationLayerDescription
from alfasim_sdk._internal.alfacase.case_description import (
    GasLiftValveEquipmentDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    HeatSourceEquipmentDescription,
)
from alfasim_sdk._internal.alfacase.case_description import HeavyComponentDescription
from alfasim_sdk._internal.alfacase.case_description import IPRCurveDescription
from alfasim_sdk._internal.alfacase.case_description import IPRModelsDescription
from alfasim_sdk._internal.alfacase.case_description import (
    InitialConditionsDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    InitialPressuresDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    InitialTemperaturesDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    InitialTracersMassFractionsDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    InitialVelocitiesDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    InitialVolumeFractionsDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    InternalNodePropertiesDescription,
)
from alfasim_sdk._internal.alfacase.case_description import LeakEquipmentDescription
from alfasim_sdk._internal.alfacase.case_description import (
    LengthAndElevationDescription,
)
from alfasim_sdk._internal.alfacase.case_description import LightComponentDescription
from alfasim_sdk._internal.alfacase.case_description import LinearIPRDescription
from alfasim_sdk._internal.alfacase.case_description import (
    MassSourceEquipmentDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    MassSourceNodePropertiesDescription,
)
from alfasim_sdk._internal.alfacase.case_description import MaterialDescription
from alfasim_sdk._internal.alfacase.case_description import NodeDescription
from alfasim_sdk._internal.alfacase.case_description import (
    NumericalOptionsDescription,
)
from alfasim_sdk._internal.alfacase.case_description import OpenHoleDescription
from alfasim_sdk._internal.alfacase.case_description import PackerDescription
from alfasim_sdk._internal.alfacase.case_description import PhysicsDescription
from alfasim_sdk._internal.alfacase.case_description import PigEquipmentDescription
from alfasim_sdk._internal.alfacase.case_description import PipeDescription
from alfasim_sdk._internal.alfacase.case_description import PipeSegmentsDescription
from alfasim_sdk._internal.alfacase.case_description import (
    PressureContainerDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    PressureNodePropertiesDescription,
)
from alfasim_sdk._internal.alfacase.case_description import ProfileDescription
from alfasim_sdk._internal.alfacase.case_description import ProfileOutputDescription
from alfasim_sdk._internal.alfacase.case_description import PumpEquipmentDescription
from alfasim_sdk._internal.alfacase.case_description import (
    PvtModelCompositionalDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    PvtModelCombinedDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    PvtModelCorrelationDescription,
)
from alfasim_sdk._internal.alfacase.case_description import PvtModelsDescription
from alfasim_sdk._internal.alfacase.case_description import (
    PvtModelTableParametersDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    ReferencedPressureContainerDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    ReferencedTemperaturesContainerDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    ReferencedTracersMassFractionsContainerDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    ReferencedVelocitiesContainerDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    ReferencedVolumeFractionsContainerDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    ReservoirInflowEquipmentDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    SeparatorNodePropertiesDescription,
)
from alfasim_sdk._internal.alfacase.case_description import SpeedCurveDescription
from alfasim_sdk._internal.alfacase.case_description import (
    SurgeVolumeOptionsDescription,
)
from alfasim_sdk._internal.alfacase.case_description import TableIPRDescription
from alfasim_sdk._internal.alfacase.case_description import TablePumpDescription
from alfasim_sdk._internal.alfacase.case_description import (
    TemperaturesContainerDescription,
)
from alfasim_sdk._internal.alfacase.case_description import TimeOptionsDescription
from alfasim_sdk._internal.alfacase.case_description import (
    TracerModelConstantCoefficientsDescription,
)
from alfasim_sdk._internal.alfacase.case_description import TracersDescription
from alfasim_sdk._internal.alfacase.case_description import (
    TracersMassFractionsContainerDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    TrendsOutputDescription,
    PositionalPipeTrendDescription,
    OverallPipeTrendDescription,
    GlobalTrendDescription,
    EquipmentTrendDescription,
    SeparatorTrendDescription,
    ControllerTrendDescription,
)
from alfasim_sdk._internal.alfacase.case_description import TubingDescription
from alfasim_sdk._internal.alfacase.case_description import ValveEquipmentDescription
from alfasim_sdk._internal.alfacase.case_description import (
    VelocitiesContainerDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    VolumeFractionsContainerDescription,
)
from alfasim_sdk._internal.alfacase.case_description import WallDescription
from alfasim_sdk._internal.alfacase.case_description import WallLayerDescription
from alfasim_sdk._internal.alfacase.case_description import WellDescription
from alfasim_sdk._internal.alfacase.case_description import XAndYDescription

from alfasim_sdk._internal.alfacase.case_description import (
    ControllerNodePropertiesDescription,
)
from alfasim_sdk._internal.alfacase.case_description import (
    ControllerInputSignalPropertiesDescription,
    ControllerOutputSignalPropertiesDescription,
)

# ALFACase: Utilities
from alfasim_sdk._internal.alfacase.alfacase import convert_alfacase_to_description
from alfasim_sdk._internal.alfacase.alfacase import convert_description_to_alfacase
from alfasim_sdk._internal.alfacase.alfacase import generate_alfacase_file
from alfasim_sdk._internal.alfacase.alfatable import generate_alfatable_file
from alfasim_sdk._internal.alfacase.alfatable import (
    load_pvt_model_table_parameters_description_from_alfatable,
)

# Constants
from alfasim_sdk._internal.constants import BUBBLE_FIELD
from alfasim_sdk._internal.constants import CompressorSpeedType
from alfasim_sdk._internal.constants import ControllerType
from alfasim_sdk._internal.constants import CorrelationPackage
from alfasim_sdk._internal.constants import CorrelationPackageType
from alfasim_sdk._internal.constants import DEFAULT_TEMPERATURE_IN_K
from alfasim_sdk._internal.constants import DrainageRateMode
from alfasim_sdk._internal.constants import DROPLET_FIELD
from alfasim_sdk._internal.constants import EmulsionModelType
from alfasim_sdk._internal.constants import EnergyModel
from alfasim_sdk._internal.constants import EnergyModelPrimaryVariable
from alfasim_sdk._internal.constants import EquationOfStateType
from alfasim_sdk._internal.constants import EquipmentAttachmentLocation
from alfasim_sdk._internal.constants import EvaluationStrategyType
from alfasim_sdk._internal.constants import EXTRAS_REQUIRED_VERSION_KEY
from alfasim_sdk._internal.constants import FlashModel
from alfasim_sdk._internal.constants import FlowDirection
from alfasim_sdk._internal.constants import FlowPatternModel
from alfasim_sdk._internal.constants import FLUID_GAS
from alfasim_sdk._internal.constants import FLUID_OIL
from alfasim_sdk._internal.constants import FLUID_PHASE_NAMES
from alfasim_sdk._internal.constants import FLUID_WATER
from alfasim_sdk._internal.constants import GAS_FIELD
from alfasim_sdk._internal.constants import GAS_LAYER
from alfasim_sdk._internal.constants import GAS_PHASE
from alfasim_sdk._internal.constants import GasLiftValveOpeningType
from alfasim_sdk._internal.constants import HydrodynamicModelType
from alfasim_sdk._internal.constants import InitialConditionStrategyType
from alfasim_sdk._internal.constants import InterpolationType
from alfasim_sdk._internal.constants import LeakLocation
from alfasim_sdk._internal.constants import LeakModel
from alfasim_sdk._internal.constants import LeakType
from alfasim_sdk._internal.constants import MassInflowSplitType
from alfasim_sdk._internal.constants import MassSourceType
from alfasim_sdk._internal.constants import MaterialType
from alfasim_sdk._internal.constants import MultiInputType
from alfasim_sdk._internal.constants import NodeCellType
from alfasim_sdk._internal.constants import NonlinearSolverType
from alfasim_sdk._internal.constants import OIL_FIELD
from alfasim_sdk._internal.constants import OIL_LAYER
from alfasim_sdk._internal.constants import OIL_PHASE
from alfasim_sdk._internal.constants import OutputAttachmentLocation
from alfasim_sdk._internal.constants import PigRoutingMode
from alfasim_sdk._internal.constants import PigTrappingMode
from alfasim_sdk._internal.constants import (
    PipeEnvironmentHeatTransferCoefficientModelType,
)
from alfasim_sdk._internal.constants import PipeThermalModelType
from alfasim_sdk._internal.constants import PipeThermalPositionInput
from alfasim_sdk._internal.constants import PumpType
from alfasim_sdk._internal.constants import PVTCompositionalViscosityModel
from alfasim_sdk._internal.constants import SeparatorGeometryType
from alfasim_sdk._internal.constants import SimulationModeType
from alfasim_sdk._internal.constants import SimulationRegimeType
from alfasim_sdk._internal.constants import SOLID_PHASE
from alfasim_sdk._internal.constants import SolidsModelType
from alfasim_sdk._internal.constants import SurfaceTensionType
from alfasim_sdk._internal.constants import SurgeVolumeTimeMode
from alfasim_sdk._internal.constants import TableInputType
from alfasim_sdk._internal.constants import TracerModelType
from alfasim_sdk._internal.constants import ValveOpeningType
from alfasim_sdk._internal.constants import ValveType
from alfasim_sdk._internal.constants import WATER_DROPLET_IN_OIL_FIELD
from alfasim_sdk._internal.constants import WATER_FIELD
from alfasim_sdk._internal.constants import WATER_LAYER
from alfasim_sdk._internal.constants import WATER_PHASE
from alfasim_sdk._internal.constants import WellConnectionPort
from alfasim_sdk._internal.constants import WellIndexPhaseType
from alfasim_sdk._internal.constants import CorrelationsOilViscosity
from alfasim_sdk._internal.constants import CorrelationsGasViscosity
from alfasim_sdk._internal.constants import CorrelationsSurfaceTension

# TODO: arthur: reorder this
from alfasim_sdk._internal.constants import PROFILES_GROUP_NAME
from alfasim_sdk._internal.constants import TRENDS_GROUP_NAME
from alfasim_sdk._internal.constants import TIME_SET_DSET_NAME
from alfasim_sdk._internal.constants import META_GROUP_NAME
from alfasim_sdk._internal.constants import PROFILES_STATISTICS_DSET_NAME_SUFFIX
from alfasim_sdk._internal.constants import RESULTS_FOLDER_NAME
from alfasim_sdk._internal.constants import RESULT_FILE_PREFIX


# SDK: Results API imports
from alfasim_sdk._internal.results_api import ALFASimResultMetadata
from alfasim_sdk._internal.results_api import load_result_files
from alfasim_sdk._internal.results_api import read_metadata
from alfasim_sdk._internal.results_api import read_time_set_info
from alfasim_sdk._internal.results_api import read_profiles_data
from alfasim_sdk._internal.results_api import read_profiles_domain_data
from alfasim_sdk._internal.results_api import read_profiles_local_statistics
from alfasim_sdk._internal.results_api import read_trends_data
from alfasim_sdk._internal.results_api import read_time_sets
from alfasim_sdk._internal.results_api import ResultsNeedFullReloadError
from alfasim_sdk._internal.results_api import map_output_key_to_time_set_key
from alfasim_sdk._internal.results_api import map_base_time_set_to_time_set_keys
from alfasim_sdk._internal.results_api import get_number_of_base_time_steps_from
from alfasim_sdk._internal.results_api import TimeSetInfoItem
from alfasim_sdk._internal.results_api import read_global_metadata
from alfasim_sdk._internal.results_api import BaseTimeStepIndexToMetaList
from alfasim_sdk._internal.results_api import cwd
from alfasim_sdk._internal.results_api import get_time_set_and_trend_from_trend_id
from alfasim_sdk._internal.results_api import get_profile_from_profile_id

# Plugins: Layouts imports
from alfasim_sdk._internal.layout import tab
from alfasim_sdk._internal.layout import tabs
from alfasim_sdk._internal.layout import group

# Plugins: Models imports
from alfasim_sdk._internal.models import container_model
from alfasim_sdk._internal.models import data_model

# Plugins: Status imports
from alfasim_sdk._internal.status import WarningMessage
from alfasim_sdk._internal.status import ErrorMessage

# Plugins: Types for configure_fields hook
from alfasim_sdk._internal.types import AddField

# Plugins: Types for configure_phases hook
from alfasim_sdk._internal.types import AddPhase
from alfasim_sdk._internal.types import UpdatePhase

# Plugins: Types for configure_layers hook
from alfasim_sdk._internal.types import AddLayer
from alfasim_sdk._internal.types import UpdateLayer

# Plugins: Types  for UI customization
from alfasim_sdk._internal.types import BaseField
from alfasim_sdk._internal.types import Boolean
from alfasim_sdk._internal.types import Enum
from alfasim_sdk._internal.types import FileContent
from alfasim_sdk._internal.types import MultipleReference
from alfasim_sdk._internal.types import Quantity
from alfasim_sdk._internal.types import Reference
from alfasim_sdk._internal.types import String
from alfasim_sdk._internal.types import Table
from alfasim_sdk._internal.types import TableColumn
from alfasim_sdk._internal.types import TracerType

# Plugins: Type for alfasim_get_additional_variables hook
from alfasim_sdk._internal.variables import SecondaryVariable

# Plugins: Constants used on SecondaryVariable
from alfasim_sdk._internal.variables import Visibility
from alfasim_sdk._internal.variables import Scope
from alfasim_sdk._internal.variables import Type
from alfasim_sdk._internal.variables import Location

__all__ = [
    "AddField",
    "AddLayer",
    "AddPhase",
    "AnnulusDescription",
    "AnnulusEquipmentDescription",
    "BUBBLE_FIELD",
    "BaseField",
    "BipDescription",
    "Boolean",
    "CaseDescription",
    "CaseOutputDescription",
    "CasingDescription",
    "CasingSectionDescription",
    "CompositionDescription",
    "CompressorEquipmentDescription",
    "CompressorPressureTableDescription",
    "CompressorSpeedType",
    "ControllerInputSignalPropertiesDescription",
    "ControllerNodePropertiesDescription",
    "ControllerOutputSignalPropertiesDescription",
    "ControllerTrendDescription",
    "ControllerType",
    "CorrelationPackage",
    "CorrelationPackageType",
    "CorrelationsOilViscosity",
    "CorrelationsGasViscosity",
    "CorrelationsSurfaceTension",
    "CvTableDescription",
    "DEFAULT_TEMPERATURE_IN_K",
    "DROPLET_FIELD",
    "DrainageRateMode",
    "EXTRAS_REQUIRED_VERSION_KEY",
    "EmulsionModelType",
    "EnergyModel",
    "EnergyModelPrimaryVariable",
    "Enum",
    "EnvironmentDescription",
    "EnvironmentPropertyDescription",
    "EquationOfStateType",
    "EquipmentAttachmentLocation",
    "EquipmentDescription",
    "EquipmentTrendDescription",
    "ErrorMessage",
    "EvaluationStrategyType",
    "FLUID_GAS",
    "FLUID_OIL",
    "FLUID_PHASE_NAMES",
    "FLUID_WATER",
    "FileContent",
    "FlashModel",
    "FlowDirection",
    "FlowPatternModel",
    "CompositionalFluidDescription",
    "CombinedFluidDescription",
    "FormationDescription",
    "FormationLayerDescription",
    "GAS_FIELD",
    "GAS_LAYER",
    "GAS_PHASE",
    "GasLiftValveEquipmentDescription",
    "GasLiftValveOpeningType",
    "GlobalTrendDescription",
    "HeatSourceEquipmentDescription",
    "HeavyComponentDescription",
    "HydrodynamicModelType",
    "IPRCurveDescription",
    "IPRModelsDescription",
    "InitialConditionStrategyType",
    "InitialConditionsDescription",
    "InitialPressuresDescription",
    "InitialTemperaturesDescription",
    "InitialTracersMassFractionsDescription",
    "InitialVelocitiesDescription",
    "InitialVolumeFractionsDescription",
    "InternalNodePropertiesDescription",
    "InterpolationType",
    "LeakEquipmentDescription",
    "LeakLocation",
    "LeakModel",
    "LeakType",
    "LengthAndElevationDescription",
    "LightComponentDescription",
    "LinearIPRDescription",
    "Location",
    "MassInflowSplitType",
    "MassSourceEquipmentDescription",
    "MassSourceNodePropertiesDescription",
    "MassSourceType",
    "MaterialDescription",
    "MaterialType",
    "MultiInputType",
    "MultipleReference",
    "NodeCellType",
    "NodeDescription",
    "NonlinearSolverType",
    "NumericalOptionsDescription",
    "OIL_FIELD",
    "OIL_LAYER",
    "OIL_PHASE",
    "OpenHoleDescription",
    "OutputAttachmentLocation",
    "OverallPipeTrendDescription",
    "PVTCompositionalViscosityModel",
    "PackerDescription",
    "PhysicsDescription",
    "PigEquipmentDescription",
    "PigRoutingMode",
    "PigTrappingMode",
    "PipeDescription",
    "PipeEnvironmentHeatTransferCoefficientModelType",
    "PipeSegmentsDescription",
    "PipeThermalModelType",
    "PipeThermalPositionInput",
    "PositionalPipeTrendDescription",
    "PressureContainerDescription",
    "PressureNodePropertiesDescription",
    "ProfileDescription",
    "ProfileOutputDescription",
    "PumpEquipmentDescription",
    "PumpType",
    "PvtModelCombinedDescription",
    "PvtModelCompositionalDescription",
    "PvtModelCorrelationDescription",
    "PvtModelTableParametersDescription",
    "PvtModelsDescription",
    "Quantity",
    "Reference",
    "ReferencedPressureContainerDescription",
    "ReferencedTemperaturesContainerDescription",
    "ReferencedTracersMassFractionsContainerDescription",
    "ReferencedVelocitiesContainerDescription",
    "ReferencedVolumeFractionsContainerDescription",
    "ReservoirInflowEquipmentDescription",
    "SOLID_PHASE",
    "Scope",
    "SecondaryVariable",
    "SeparatorGeometryType",
    "SeparatorNodePropertiesDescription",
    "SeparatorTrendDescription",
    "SimulationModeType",
    "SimulationRegimeType",
    "SolidsModelType",
    "SpeedCurveDescription",
    "String",
    "SurfaceTensionType",
    "SurgeVolumeOptionsDescription",
    "SurgeVolumeTimeMode",
    "Table",
    "TableColumn",
    "TableIPRDescription",
    "TableInputType",
    "TablePumpDescription",
    "TemperaturesContainerDescription",
    "TimeOptionsDescription",
    "TracerModelConstantCoefficientsDescription",
    "TracerModelType",
    "TracerType",
    "TracersDescription",
    "TracersMassFractionsContainerDescription",
    "TrendsOutputDescription",
    "TubingDescription",
    "Type",
    "UpdateLayer",
    "UpdatePhase",
    "ValveEquipmentDescription",
    "ValveOpeningType",
    "ValveType",
    "VelocitiesContainerDescription",
    "Visibility",
    "VolumeFractionsContainerDescription",
    "WATER_DROPLET_IN_OIL_FIELD",
    "WATER_FIELD",
    "WATER_LAYER",
    "WATER_PHASE",
    "WallDescription",
    "WallLayerDescription",
    "WarningMessage",
    "WellConnectionPort",
    "WellDescription",
    "WellIndexPhaseType",
    "XAndYDescription",
    "console_main",
    "container_model",
    "convert_alfacase_to_description",
    "convert_description_to_alfacase",
    "data_model",
    "generate_alfacase_file",
    "generate_alfatable_file",
    "get_metadata",
    "group",
    "load_pvt_model_table_parameters_description_from_alfatable",
    "tab",
    "tabs",
]
