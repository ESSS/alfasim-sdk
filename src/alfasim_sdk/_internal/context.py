from typing import List
from typing import Optional

import attr
from attr.validators import deep_iterable
from attr.validators import in_
from attr.validators import instance_of
from attr.validators import optional
from barril.units import Scalar

from alfasim_sdk._internal.constants import EmulsionModelType
from alfasim_sdk._internal.constants import HydrodynamicModelType
from alfasim_sdk._internal.constants import SolidsModelType
from alfasim_sdk._internal.validators import list_of_strings
from alfasim_sdk._internal.validators import non_empty_str


@attr.s(frozen=True)
class PluginInfo:
    """
    PluginInfo provides information about the plugin name, its current state (either enabled or not) and all
    models defined from this plugin.
    """

    caption: str = attr.attrib(validator=non_empty_str)
    name: str = attr.attrib(validator=non_empty_str)
    enabled: bool = attr.attrib(validator=instance_of(bool))
    models: List[str] = attr.attrib(validator=list_of_strings)


@attr.s(frozen=True)
class PipelineSegmentInfo:
    """
    The PipelineSegmentInfo provides information about segments associated with a pipeline.

    PipelineSegmentInfo provides the following attributes:

    :ivar start_position: Defines point where this segment starts in MD (measured depth).

    :ivar inner_diameter: Inner diameter of pipe annulus.

    :ivar roughness: Absolute roughness of the wall of this segment.
        When ```is_custom``` is true, the reported roughness is customized for this segment,
        otherwise, the reported roughness is the original reported by the wall.

    :ivar is_custom: Informs either the roughness value is custom or original from the wall

    """

    inner_diameter: Scalar = attr.attrib(validator=instance_of(Scalar))
    start_position: Scalar = attr.attrib(validator=instance_of(Scalar))
    is_custom: bool = attr.attrib(validator=instance_of(bool))
    roughness: Scalar = attr.attrib(validator=instance_of(Scalar))


list_of_segments = deep_iterable(
    member_validator=instance_of(PipelineSegmentInfo),
    iterable_validator=instance_of(list),
)


@attr.s(frozen=True)
class PipelineInfo:
    """
    The PipelineInfo provides information about the geometry of a pipeline.

    PipelineSegmentInfo provides the following attributes:
    :ivar name: Name associated with this ``Pipeline`` on ALFAsim

    :ivar edge_name: Name of the edge that this ``Pipeline`` is associated with.

    :ivar segments: List of segments associates with this ``Pipeline``
        For more information check :class:`~PipelineSegmentInfo`

    :ivar total_length: Total length of the pipeline.
    """

    name = attr.attrib(type=str, validator=non_empty_str)
    edge_name = attr.attrib(type=str, validator=non_empty_str)
    segments = attr.attrib(type=List[PipelineSegmentInfo], validator=list_of_segments)
    total_length = attr.attrib(type=Scalar, validator=instance_of(Scalar))


@attr.s(frozen=True)
class NodeInfo:
    """
    The ``NodeInfo`` provides information about a ``Node`` from ``ALFAsim``, it provides the name of the Node and the number of
    phases that the associate PVT model has.
    """

    name: str = attr.attrib(validator=non_empty_str)
    number_of_phases_from_associated_pvt: Optional[int] = attr.attrib(
        validator=optional(instance_of(int))
    )


@attr.s(frozen=True)
class EdgeInfo:
    """
    The ``EdgeInfo`` provides information about a ``Edge`` from ``ALFAsim``, it provides the name of the Node and the number of
    phases that the associate pvt model has.
    """

    name: str = attr.attrib(validator=non_empty_str)
    number_of_phases_from_associated_pvt: Optional[int] = attr.attrib(
        validator=optional(instance_of(int))
    )


@attr.s(frozen=True)
class HydrodynamicModelInfo:
    """
    HydrodynamicModelInfo provides information about which layer, fields, and phases the currently Hydrodynamic model is using.
    """

    selected_base_type: HydrodynamicModelType = attr.attrib(
        validator=in_(HydrodynamicModelType)
    )
    phases: List[str] = attr.attrib(validator=list_of_strings)
    fields: List[str] = attr.attrib(validator=list_of_strings)
    layers: List[str] = attr.attrib(validator=list_of_strings)
    has_water_phase = attr.attrib(type=bool, validator=instance_of(bool))


@attr.s(frozen=True)
class PhysicsOptionsInfo:
    """
    ``PhysicsOptionsInfo`` provides information about the physics options available at ``ALFAsim``.

    The following option can be accessed:

    Emulsion Model: Informs which emulsion model the application is currently using.
    For more information about all options available check :py:class:`~alfasim_sdk._internal.constants.EmulsionModelType`

    Solids Model: Informs the current solid model being used by the application
    For more information about all options available check :py:class:`~alfasim_sdk._internal.constants.SolidsModelType`

    Hydrodynamic Model: Provides a :class:`HydrodynamicModelInfo` informing which layers, fields and phases
    the application is currently using.
    """

    emulsion_model: EmulsionModelType = attr.attrib(validator=in_(EmulsionModelType))
    solids_model: SolidsModelType = attr.attrib(validator=in_(SolidsModelType))
    hydrodynamic_model: HydrodynamicModelInfo = attr.attrib(
        validator=instance_of(HydrodynamicModelInfo)
    )


class Context:
    """
    The context class provides information about the current state of the application
    and the models implemented by the user.

    The following methods provide an instance of ``Context`` to inform the current state
    of the application:

    - :ref:`visible-expression-section` parameter from all fields
    - :ref:`enable-expression-section` parameter from all fields
    - :func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_get_status` hook
    """

    def get_model(self, model_name: str) -> Optional[type]:
        """
        Returns an instance of the given ``model_name``.

        :param model_name: must be the name of a model defined within the plugin.

        In the example below, the ``Context`` is used to access a property from the model ``MyModel``

        ``ctx.GetModel("Acme")`` as exemplified in the code below.

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


            >>> ctx.get_model('MyModel')
            MyModel(name='ALFAsim', scalar=Scalar(1.0, 'degC', 'temperature'))

            >>> ctx.get_model('MyModel').name
            'ALFAsim'

        At runtime, you can also verify the names of the models defined by a given plugin.
        For more information check cpp:func:`~alfasim_sdk.context.Context.GetPluginInfoById`

        :raises TypeError: When the given ``model_name`` does not exist.
        :raises FrozenInstanceError: When trying to modify a value

        """

    def get_pipelines(self) -> Optional[List[PipelineInfo]]:
        """
        Return a list with all Pipes available on the Network from the Project.
        Each Pipe is represented by an instance of :class:`~alfasim_sdk._internal.context.PipelineInfo`.

        .. rubric:: Usage Example of GetPipelines

        .. image:: /_static/images/api/context_access_network.png

        The image above has two Pipelines configured, you can access this information by using the method ``GetPipelines`` as
        demonstrated below.

        .. code-block:: console

            >>> ctx.get_pipelines()[0]
            PipelineInfo(name='Pipe 1 > Pipeline', [ ... ])

            >>> ctx.get_pipelines()[0].edge_name
            'Pipe 1'

            >>> ctx.get_pipelines()[0].total_length
            Scalar(1000.0, 'm', 'length')

            >>> len(ctx.get_pipelines()[0].segments)
            1


        .. note::

            The values from PipelineInfo are read-only, they cannot be modified.

        Checkout the :class:`~alfasim_sdk._internal.context.PipelineInfo` section to know more about the properties available.
        """

    def get_plugins_infos(self) -> List[PluginInfo]:
        """
        Return a list of all plugins available on ALFAsim.
        Each plugin is represented by an instance of :class:`PluginInfo`.

        .. rubric:: Usage Example of GetPluginsInfos

        The example demonstrated how you can access information about the plugin from using the cpp:func:`~alfasim_sdk.context.Context.GetPluginsInfos`
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


            >>> ctx.get_plugins_infos()
            [PluginInfo(caption='myplugin', name='myplugin', enabled=True, models=['MyModel'])]

            >>> ctx.get_plugins_infos()[0].enabled
            True

            >>> ctx.get_plugins_infos()[0].models
            ['MyModel']


        Checkout the :class:`PluginInfo` section to know more about the properties available.
        """

    def get_plugin_info_by_id(self, plugin_id: str) -> PluginInfo:
        """
        Similar to :func:`get_plugins_infos` but returns a single instance of :class:`PluginInfo`
        from the given ``plugin_id`` parameter.

        Checkout the :class:`PluginInfo` section to know more about the properties available.

        :raises ValueError: When the plugin informed by ``plugin_id`` it's not available.
        """

    def get_edges(self) -> Optional[List[EdgeInfo]]:
        """
        Return a list of all Edges available on ALFAsim.
        Each Edge is represented by an instance of :class:`EdgeInfo`.

        .. rubric:: Example of GetEdges

        .. image:: /_static/images/api/context_access_network.png

        The image above has two Edges configured, in order to access the available Edges, it's possible to use the method ``get_edges`` as
        demonstrated below.

        .. rubric:: Accessing GetEdges from the context

        .. code-block:: console

            >>> ctx.get_edges()[0]
            EdgeInfo(name='Pipe 1', number_of_phases_from_associated_pvt=2)

            >>> ctx.get_pipelines()[0].number_of_phases_from_associated_pvt
            'Pipe 1'

        Checkout the :class:`EdgeInfo` section to know more about the properties available.
        """

    def get_nodes(self) -> Optional[List[NodeInfo]]:
        """
        Return a list of all Nodes available on ALFAsim.
        Each Node is represented by an instance of :class:`NodeInfo`.

        .. rubric:: Usage Example of GetNodes

        .. image:: /_static/images/api/context_access_network.png

        The image above has three nodes configured, you can access this information by using the method ``get_nodes`` as
        demonstrated below.

        .. code-block:: console

            >>> ctx.get_nodes[0]
            NodeInfo(name='Node 1', number_of_phases_from_associated_pvt=2)

            >>> ctx.get_nodes[0].name
            'Node 1'

        .. note::

            The values from NodeInfo are read-only, they cannot be modified.

        Checkout the :class:`NodeInfo` section to know more about the properties available.
        """

    def get_physics_options(self) -> PhysicsOptionsInfo:
        """
        Return the physics options from the current project from ALFAsim.

        .. rubric:: Example of GetPhysicsOptions

        The image below shows a configuration from a given project.

        .. image:: /_static/images/api/context_get_advanced_options_example_2.png
            :scale: 80%

        .. image:: /_static/images/api/context_get_advanced_options_example_1.png
            :scale: 80%

        It's possible to access this information from inside the plugin, by using context api as demonstrate below.

        .. rubric:: Accessing GetPhysicsOptions from the context

        .. code-block:: python

            >>> ctx.get_physics_options()
            PhysicsOptionsInfo( [...] )

            >>> ctx.get_physics_options().emulsion_model.value
            'EmulsionModelType.brinkman1952'

            >>> ctx.get_physics_options().hydrodynamic_model
            HydrodynamicModelInfo( [ ... ] )

            >>> ctx.get_physics_options().hydrodynamic_model.fields
            ['gas', 'oil', 'droplet', 'bubble']

            >>> ctx.get_physics_options().hydrodynamic_model.layers
            ['gas', 'oil']

            >>> ctx.get_physics_options().hydrodynamic_model.phases
            ['gas', 'oil']

        Checkout the :class:`PhysicsOptionsInfo` section to know more about the properties available.

        """
