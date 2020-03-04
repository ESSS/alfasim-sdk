import re

import pytest
from barril.units import Scalar

from alfasim_sdk.constants import EmulsionModelType
from alfasim_sdk.constants import HydrodynamicModelType
from alfasim_sdk.constants import SolidsModelType
from alfasim_sdk.context import EdgeInfo
from alfasim_sdk.context import HydrodynamicModelInfo
from alfasim_sdk.context import NodeInfo
from alfasim_sdk.context import PhysicsOptionsInfo
from alfasim_sdk.context import PipelineInfo
from alfasim_sdk.context import PipelineSegmentInfo


def test_plugin_info():
    from alfasim_sdk.context import PluginInfo

    error_msg = "'name' must be 'str' (got 1 that is a 'int')"
    with pytest.raises(TypeError, match=re.escape(error_msg)):
        PluginInfo(name=1, caption="Caption", enabled="True", models="Anything")

    error_msg = "'enabled' must be <class 'bool'> (got 'True' that is a <class 'str'>)."
    with pytest.raises(TypeError, match=re.escape(error_msg)):
        PluginInfo(name="Acme", caption="Caption", enabled="True", models="Anything")

    error_msg = (
        "'models' must be <class 'list'> (got 'Anything' that is a <class 'str'>)."
    )
    with pytest.raises(TypeError, match=re.escape(error_msg)):
        PluginInfo(name="Acme", caption="Caption", enabled=True, models="Anything")

    error_msg = "'models' must be <class 'str'> (got 1 that is a <class 'int'>)."
    with pytest.raises(TypeError, match=re.escape(error_msg)):
        PluginInfo(name="Acme", caption="Caption", enabled=True, models=[1, 2, 3])

    PluginInfo(name="Acme", caption="Caption", enabled=True, models=["1", "2"])


def test_pipeline_info():
    pipeline_segment_info = PipelineSegmentInfo(
        inner_diameter=Scalar(0.15, "m"),
        start_position=Scalar(0.0, "m"),
        is_custom=True,
        roughness=Scalar(0.0, "m"),
    )

    pipeline_info = PipelineInfo(
        name="Foo",
        edge_name="Foo 2",
        segments=[pipeline_segment_info],
        total_length=Scalar(0.0, "m"),
    )
    assert pipeline_info


def test_pipeline_segments():
    pipeline_segment_info = PipelineSegmentInfo(
        inner_diameter=Scalar(0.15, "m"),
        start_position=Scalar(0.0, "m"),
        is_custom=True,
        roughness=Scalar(0.0, "m"),
    )

    assert pipeline_segment_info

    diameter_msg = "'inner_diameter' must be <class 'barril.units._scalar.Scalar'> (got 1 that is a <class 'int'>)."
    position_msg = "'start_position' must be <class 'barril.units._scalar.Scalar'> (got 1 that is a <class 'int'>)."
    is_custom_msg = (
        "'is_custom' must be <class 'bool'> (got None that is a <class 'NoneType'>)."
    )
    roughness_msg = "'roughness' must be <class 'barril.units._scalar.Scalar'> (got 1 that is a <class 'int'>)."

    with pytest.raises(TypeError, match=re.escape(diameter_msg)):
        PipelineSegmentInfo(
            inner_diameter=1, start_position=1, is_custom=None, roughness=1
        )

    with pytest.raises(TypeError, match=re.escape(position_msg)):
        PipelineSegmentInfo(
            inner_diameter=Scalar(0.15, "m"),
            start_position=1,
            is_custom=None,
            roughness=1,
        )

    with pytest.raises(TypeError, match=re.escape(is_custom_msg)):
        PipelineSegmentInfo(
            inner_diameter=Scalar(0.15, "m"),
            start_position=Scalar(0.0, "m"),
            is_custom=None,
            roughness=1,
        )

    with pytest.raises(TypeError, match=re.escape(roughness_msg)):
        PipelineSegmentInfo(
            inner_diameter=Scalar(0.15, "m"),
            start_position=Scalar(0.0, "m"),
            is_custom=True,
            roughness=1,
        )


@pytest.mark.parametrize("class_with_info", [NodeInfo, EdgeInfo])
def test_nodes_and_edges_info(class_with_info):
    assert class_with_info(name="Foo", number_of_phases_from_associated_pvt=1)
    assert class_with_info(name="Foo", number_of_phases_from_associated_pvt=None)

    # number_of_phases_from_associated_pvt must be int or None
    with pytest.raises(TypeError):
        class_with_info(name="Foo", number_of_phases_from_associated_pvt="1")

    # name must be string and not empty
    with pytest.raises(TypeError):
        class_with_info(name=None, number_of_phases_from_associated_pvt=1)

    # name must be string and not empty
    with pytest.raises(ValueError):
        class_with_info(name="", number_of_phases_from_associated_pvt=1)


def test_physics_option():
    assert PhysicsOptionsInfo(
        emulsion_model=EmulsionModelType.Boxall2012,
        solids_model=SolidsModelType.NoModel,
        hydrodynamic_model=HydrodynamicModelInfo(
            selected_base_type=HydrodynamicModelType.ThreeLayersGasOilWater,
            phases=["1", "2"],
            fields=["3", "4"],
            layers=["5", "6"],
            has_water_phase=True,
        ),
    )
