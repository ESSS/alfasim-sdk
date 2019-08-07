from enum import Enum
from typing import List
from typing import Optional

import attr
from attr.validators import deep_iterable
from attr.validators import instance_of
from attr.validators import optional
from barril.units import Scalar

from alfasim_sdk._validators import list_of_strings
from alfasim_sdk._validators import non_empty_str


@attr.s(frozen=True)
class PluginInfo:
    """
    PluginInfo provides information about the plugin name, its current state (either enabled or not) and all
    models defined from this plugin.
    """

    caption = attr.attrib(validator=non_empty_str)
    name = attr.attrib(validator=non_empty_str)
    enabled = attr.attrib(validator=instance_of(bool))
    models = attr.attrib(validator=list_of_strings)


@attr.s(frozen=True)
class PipelineSegmentInfo:
    """
    The PipelineSegmentInfo provides information about a segments associated with a pipeline.

    PipelineSegmentInfo provides the following attributes:
        edge_name: name of the edge that the segment is associated with

        start_position: Defines point where this segment starts in MD (measured depth).

        inner_diameter: Inner diameter of pipe annulus.

        roughness: Absolute roughness of the wall of this segment.
            When ```is_custom``` is true, the reported roughness is customized for this segment,
            otherwise the reported roughness is the original reported by the wall.

        is_custom: Informs either the roughness value is custom or original from the wall
    """

    inner_diameter = attr.attrib(validator=instance_of(Scalar))
    start_position = attr.attrib(validator=instance_of(Scalar))
    is_custom = attr.attrib(validator=instance_of(bool))
    roughness = attr.attrib(validator=instance_of(Scalar))


list_of_segments = deep_iterable(
    member_validator=instance_of(PipelineSegmentInfo),
    iterable_validator=instance_of(list),
)


@attr.s(frozen=True)
class PipelineInfo:
    """
    The PipelineInfo provides information about the geometry of a pipeline.

    PipelineSegmentInfo provides the following attributes:
        name: Name associated with this ``Pipeline`` on ALFAsim

        edge_name: Name of the edge that this ``Pipeline`` is associated with.

        segments: List of segments associates with this ``Pipeline``
        For more information check `alfasim_sdk.context.PipelineSegmentInfo`

        total_length: Total length of the pipeline.

    """

    name = attr.attrib(type=str, validator=non_empty_str)
    edge_name = attr.attrib(type=str, validator=non_empty_str)
    segments = attr.attrib(type=List[PipelineSegmentInfo], validator=list_of_segments)
    total_length = attr.attrib(type=Scalar, validator=instance_of(Scalar))


@attr.s(frozen=True)
class NodeInfo:
    """
    The ``NodeInfo`` provides information about a ``Node`` from ``ALFAsim``, it provides the name of the Node and the number of
    phases that the associate pvt model has.
    """

    name = attr.attrib(validator=non_empty_str)
    number_of_phases_from_associated_pvt = attr.attrib(
        validator=optional(instance_of(int))
    )


@attr.s(frozen=True)
class EdgeInfo:
    """
    The ``EdgeInfo`` provides information about a ``Edge`` from ``ALFAsim``, it provides the name of the Node and the number of
    phases that the associate pvt model has.
    """

    name = attr.attrib(validator=non_empty_str)
    number_of_phases_from_associated_pvt = attr.attrib(
        validator=optional(instance_of(int))
    )


class EmulsionModelType(Enum):
    """
    Options for emulsion properties calculation.
    """

    no_model = "EmulsionModelType.no_model"
    boxall2012 = "EmulsionModelType.boxall2012"
    brauner2001 = "EmulsionModelType.brauner2001"
    brinkman1952 = "EmulsionModelType.brinkman1952"
    brinkman1952_and_yeh1964 = "EmulsionModelType.brinkman1952_and_yeh1964"
    hinze1955 = "EmulsionModelType.hinze1955"
    model_default = "EmulsionModelType.model_default"
    mooney1951a = "EmulsionModelType.mooney1951a"
    mooney1951b = "EmulsionModelType.mooney1951b"
    sleicher1962 = "EmulsionModelType.sleicher1962"
    taylor1932 = "EmulsionModelType.taylor1932"


class SolidsModelType(Enum):
    """
    Informs which solid model should be used:

    - no_model - None:
        Without slip velocity and slurry viscosity

    - mills1985_equilibrium - Mills (1985):
        Employs the equilibrium slip velocity model and the Mills (1985) effective dynamic viscosity expression.

    - santamaria2010_equilibrium - Santamaría-Holek (2010):
        This model is more appropriate to use when the solid phase has properties similar to or equal to hydrate.
        It was fitted by Qin et al. (2018) for hydrates.

    - thomas1965_equilibrium - Thomas (1965):
        Employs the equilibrium slip velocity model and the Thomas (1965) effective dynamic viscosity expression.
    """

    no_model = "SolidsModelType.no_model"
    mills1985_equilibrium = "SolidsModelType.mills1985_equilibrium"
    santamaria2010_equilibrium = "SolidsModelType.santamaria2010_equilibrium"
    thomas1965_equilibrium = "SolidsModelType.thomas1965_equilibrium"


@attr.s(frozen=True)
class HydrodynamicModelInfo:
    """
    HydrodynamicModelInfo provides information about which layer, fields and phases the currently Hydrodynamic model is using.
    """

    phases = attr.attrib(validator=list_of_strings)
    fields = attr.attrib(validator=list_of_strings)
    layers = attr.attrib(validator=list_of_strings)
    has_water_phase = attr.attrib(type=bool, validator=instance_of(bool))


@attr.s(frozen=True)
class PhysicsOptionsInfo:
    """
    PhysicsOptionsInfo provides information about the ``Physics Options`` available at ``ALFAsim``.

    The following option can be accessed:

    Emulsion Model: Informs which emulsion model the application is currently using.
    For more information about all options available check ``alfasim_sdk.context.EmulsionModelType``

    Solids Model: Informs the current solid model being used by the application
    For more information about all options available check ``alfasim_sdk.context.SolidsModelType``

    Hydrodynamic Model: Provides a ``alfasim_sdk.context.HydrodynamicModelInfo`` informing which layers, fields and phases
    the application is currently using.
    For more information about all options available check ``alfasim_sdk.context.HydrodynamicModelInfo``
    """

    emulsion_model = attr.attrib(validator=instance_of(EmulsionModelType))
    solids_model = attr.attrib(validator=instance_of(SolidsModelType))
    hydrodynamic_model = attr.attrib(validator=instance_of(HydrodynamicModelInfo))


class Context:
    """
    The context class provides information about the current state of the application
    and the models implemented by the user.
    """

    def GetModel(self, model_name: str) -> Optional[type]:
        """
        Returns a model defined from a plugin.
        The parameter ``model_name`` must be the name of models defined within the plugin.

        Ex.:
        You can access a class "Acme" defined from ``alfasim_get_data_model_type()`` by typing
        ``ctx.GetModel("Acme")`` as exemplified in the code bellow.


        @hookimpl
        def alfasim_get_data_model_type():
            @model_class(caption="Acme")
            class Acme:
                name = String(value="acme", caption="Acme")

            return [Acme]

        @hookimpl
        def alfasim_get_status(ctx):
            model = ctx.GetModel('Acme')
            assert model.name == 'acme'

        It also possible to use ``alfasim_sdk.context.PluginInfo.models`` to check models available for a given Plugin
        For more information check ``alfasim_sdk.context.Context.GetPluginInfoByName``

        The values from the returned Model are read-only, they cannot be modified.
        If the model informed cannot be found, a  :class:`TypeError` exception is raised.
        """

    def GetPipelines(self) -> Optional[List[PipelineInfo]]:
        """
        Return a list with all Pipes available on ALFAsim.
        Each Pipe is represented by an instance of ``alfasim_sdk.status.PipelineInfo``.

        The values from PipelineInfo are read-only, they cannot be modified.
        For more information about the options available check ``alfasim_sdk.context.PipelineInfo``
        """

    def GetPluginsInfos(self) -> List[PluginInfo]:
        """
        Return a list of all plugins available on ALFAsim.
        Each plugin is represented by an instance of  ``alfasim_sdk.context.PluginInfo``.

        The values from PluginInfo are read-only, they cannot be modified
        For more information about the options available check ``alfasim_sdk.context.PluginInfo``
        """

    def GetPluginInfoByName(self, plugin_name: str) -> PluginInfo:
        """
        Return a instance of ``alfasim_sdk.context.PluginInfo`` for the given ``plugin_name``.
        If the plugin informed cannot be found, a  :class:`ValueError` exception is raised.

        The values from PluginInfo are read-only, they cannot be modified
        For more information about the options available check ``alfasim_sdk.context.PluginInfo``
        """

    def GetEdges(self) -> Optional[List[EdgeInfo]]:
        """
        Return a list of all Edges available on ALFAsim.
        Each Edge is represented by an instance of ``alfasim_sdk.context.EdgeInfo``.

        The values from EdgeInfo are read-only, they cannot be modified.
        For more information about the options available check ``alfasim_sdk.context.EdgeInfo``
        """

    def GetNodes(self) -> Optional[List[NodeInfo]]:
        """
        Return a list of all Nodes available on ALFAsim.
        Each Node is represented by an instance of ``alfasim_sdk.context.NodeInfo``.

        The values from NodeInfo are read-only, they cannot be modified
        For more information about the options available check ``alfasim_sdk.context.NodeInfo``
        """

    def GetPhysicsOptions(self) -> PhysicsOptionsInfo:
        """
        Return the physics options available on ALFAsim study.

        The values from PhysicsOptionsInfo are read-only, they cannot be modified.
        For more information about the options available check ``alfasim_sdk.context.PhysicsOptionsInfo``
        """
