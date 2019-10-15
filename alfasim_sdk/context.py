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


class HydrodynamicModelType(Enum):
    """
    Informs which base Hydrodynamic model is being used, without any modification from plugins:

    - two_phase_four_field_ucm - 'Multi-field, Unit Cell (gas-liquid)':
        Two phase (gas and liquid) with four fields (continuous gas, continuous liquid, dispersed gas bubble and dispersed liquid droplet).

    - three_phase_five_field_ucm - 'Multi-field, Unit Cell (gas-liquid-water)':
        Three phase (gas, liquid and water) with five fields (continuous gas, continuous liquid, continuous water,dispersed gas bubble and dispersed liquid droplet).

    - two_phase_two_field_slug_capturing - 'Two-fluid, Regime Capturing (gas-liquid)':
        Two phase (gas and liquid) with two fields (continuous gas and continuous liquid) using Regime Capturing strategy.

    """

    two_phase_four_field_ucm = "hydrodynamic_model_4_fields"
    three_phase_five_field_ucm = "hydrodynamic_model_3_layers_gas_oil_water"
    two_phase_two_field_slug_capturing = "hydrodynamic_model_2_fields"


@attr.s(frozen=True)
class HydrodynamicModelInfo:
    """
    HydrodynamicModelInfo provides information about which layer, fields and phases the currently Hydrodynamic model is using.
    """

    selected_base_type = attr.attrib(validator=instance_of(HydrodynamicModelType))
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

    The following methods provides an instance of :func:`~alfasim_sdk.context.Context` to inform the currently state
    of the application:

    - :ref:`visible-expression-section` parameter from all fields
    - :ref:`enable-expression-section` parameter from all fields
    - :func:`~alfasim_sdk.hook_specs_gui.alfasim_get_status` hook
    """

    def GetModel(self, model_name: str) -> Optional[type]:
        """
        Returns an instance of the given ``model_name``.

        The parameter ``model_name`` must be the name of a model defined within the plugin.

        In the example below, the Context is used to access a property from the model "MyModel"

        ``ctx.GetModel("Acme")`` as exemplified in the code bellow.

        .. rubric:: Setting up the model

        .. code-block:: python

            @data_model(caption="MyPlugin", icon="")
            class MyModel:
                name = String(value="ALFAsim", caption="Field")
                scalar = Quantity(value=1, unit="degC", caption="Field")

            @alfasim_sdk.hookimpl
            def alfasim_get_data_model_type():
                return [MyModel]

        .. rubric:: Accessing the context

        .. code-block:: console


            >>> ctx.GetModel('MyModel')
            MyModel(name='ALFAsim', scalar=Scalar(1.0, 'degC', 'temperature'))

            >>> ctx.GetModel('MyModel').name
            'ALFAsim'

        At runtime, you can also verify the names of the models defined by a given plugin. For this, you need to
        For more information check :func:`~alfasim_sdk.context.Context.GetPluginInfoById`

        .. note::

            The model returned by the GetModel is read-only, they cannot be modified.

        :raises TypeError: When the given ``model_name`` does not exist.
        :raises FrozenInstanceError: When trying to modify a value

        """

    def GetPipelines(self) -> Optional[List[PipelineInfo]]:
        """
        Return a list with all Pipes available on the Network from the Project.
        Each Pipe is represented by an instance of :func:`~alfasim_sdk.context.PipelineInfo`.

        .. rubric:: Usage Example of GetPipelines

        .. image:: _static/context_access_network.png

        The image above has two Pipelines configured, you can access this information by using the method ``GetPipelines`` as
        demonstrated below.

        .. code-block:: console

            >>> ctx.GetPipelines()[0]
            PipelineInfo(name='Pipe 1 > Pipeline', [ ... ])

            >>> ctx.GetPipelines()[0].edge_name
            'Pipe 1'

            >>> ctx.GetPipelines()[0].total_length
            Scalar(1000.0, 'm', 'length')

            >>> len(ctx.GetPipelines()[0].segments)
            1


        .. note::

            The values from PipelineInfo are read-only, they cannot be modified.

        Checkout the :func:`~alfasim_sdk.context.PipelineInfo` section to know more about the properties available.
        """

    def GetPluginsInfos(self) -> List[PluginInfo]:
        """
        Return a list of all plugins available on ALFAsim.
        Each plugin is represented by an instance of :func:`~alfasim_sdk.context.PluginInfo`.

        .. rubric:: Usage Example of GetPluginsInfos

        The example demonstrated how you can access information about the plugin from using the :func:`~alfasim_sdk.context.GetPluginsInfos`
        method.

        .. rubric:: Setting up the model

        .. code-block:: python

            @data_model(caption="MyPlugin", icon="")
            class MyModel:
                name = String(value="ALFAsim", caption="Field")
                scalar = Quantity(value=1, unit="degC", caption="Field")

            @alfasim_sdk.hookimpl
            def alfasim_get_data_model_type():
                return [MyModel]

        .. rubric:: Accessing the context

        .. code-block:: console


            >>> ctx.GetPluginsInfos()
            [PluginInfo(caption='myplugin', name='myplugin', enabled=True, models=['MyModel'])]

            >>> ctx.GetPluginsInfos()[0].enabled
            True

            >>> ctx.GetPluginsInfos()[0].models
            ['MyModel']


        .. note::

          The values from PluginInfo are read-only, they cannot be modified

        Checkout the :func:`~alfasim_sdk.context.PluginInfo` section to know more about the properties available.
        """

    def GetPluginInfoById(self, plugin_id: str) -> PluginInfo:
        """
        Similar to :func:`~alfasim_sdk.context.GetPluginsInfos` but returns a single instance of :func:`~alfasim_sdk.context.PluginInfo`
        from the given ``plugin_id`` parameter.

        Checkout the :func:`~alfasim_sdk.context.PluginInfo` section to know more about the properties available.

        :raises ValueError: When the plugin informed by ``plugin_id`` it's not available.

        .. note::

            The values from PluginInfo are read-only, they cannot be modified

        """

    def GetEdges(self) -> Optional[List[EdgeInfo]]:
        """
        Return a list of all Edges available on ALFAsim.
        Each Edge is represented by an instance of :func:`~alfasim_sdk.context.EdgeInfo`.

        .. rubric:: Usage Example of GetEdges

        .. image:: _static/context_access_network.png

        The image above has two Edges configured, you can access this information by using the method ``GetEdges`` as
        demonstrated below.

        .. code-block:: console

            >>> ctx.GetEdges()[0]
            EdgeInfo(name='Pipe 1', number_of_phases_from_associated_pvt=2)

            >>> ctx.GetPipelines()[0].number_of_phases_from_associated_pvt
            'Pipe 1'

        .. note::

            The values from EdgeInfo are read-only, they cannot be modified.

        Checkout the :func:`~alfasim_sdk.context.EdgeInfo` section to know more about the properties available.
        """

    def GetNodes(self) -> Optional[List[NodeInfo]]:
        """
        Return a list of all Nodes available on ALFAsim.
        Each Node is represented by an instance of :func:`alfasim_sdk.context.NodeInfo`.

        .. rubric:: Usage Example of GetNodes

        .. image:: _static/context_access_network.png

        The image above has three nodes configured, you can access this information by using the method ``GetNodes`` as
        demonstrated below.

        .. code-block:: console

            >>> ctx.GetNodes()[0]
            EdgeInfo(name='Pipe 1', number_of_phases_from_associated_pvt=2)

            >>> ctx.GetNodes()[0].name
            'Node 1'

        .. note::

            The values from NodeInfo are read-only, they cannot be modified.

        Checkout the :func:`~alfasim_sdk.context.NodeInfo` section to know more about the properties available.
        """

    def GetPhysicsOptions(self) -> PhysicsOptionsInfo:
        """
        Return the physics options from the current project from ALFAsim.

        .. note:

          The values from PhysicsOptionsInfo are read-only, they cannot be modified.

        .. image:: _static/context_get_advanced_options_example_2.png
            :scale: 80%

        .. image:: _static/context_get_advanced_options_example_1.png
            :scale: 80%

        .. rubric:: Usage Example of GetPhysicsOptions

        The image above shows the current configuration of a study, you can access this information by using the method
        ``GetPhysicsOptions`` as demonstrated below.

        .. code-block:: python

            >>> ctx.GetPhysicsOptions()
            PhysicsOptionsInfo( [...] )

            >>> ctx.GetPhysicsOptions().emulsion_model.value
            'EmulsionModelType.brinkman1952'

            >>> ctx.GetPhysicsOptions().hydrodynamic_model
            HydrodynamicModelInfo( [ ... ] )

            >>> ctx.GetPhysicsOptions().hydrodynamic_model.fields
            ['gas', 'liquid', 'droplet', 'bubble']

            >>> ctx.GetPhysicsOptions().hydrodynamic_model.layers
            ['gas', 'liquid']

            >>> ctx.GetPhysicsOptions().hydrodynamic_model.phases
            ['gas', 'liquid']

        Checkout the :func:`~alfasim_sdk.context.PhysicsOptionsInfo` section to know more about the properties available.

        """
