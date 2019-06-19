import re

import pytest

from alfasim_sdk.status import EdgesInfo
from alfasim_sdk.status import EmulsionModelType
from alfasim_sdk.status import ErrorMessage
from alfasim_sdk.status import HydrodynamicModelInfo
from alfasim_sdk.status import NodesInfo
from alfasim_sdk.status import PhysicsOptionsInfo
from alfasim_sdk.status import SolidsModelType
from alfasim_sdk.status import WarningMessage


@pytest.mark.parametrize("status_class", [WarningMessage, ErrorMessage])
def test_status(status_class):
    out = status_class(model_name="Test1", message="Message From test")
    assert out.model_name == "Test1"
    assert out.message == "Message From test"

    with pytest.raises(ValueError, match='The field "model_name" cannot be empty'):
        status_class(model_name="", message="Message From test")

    with pytest.raises(ValueError, match='The field "message" cannot be empty'):
        status_class(model_name="Test", message="")

    with pytest.raises(
        TypeError,
        match=re.escape("'model_name' must be 'str' (got 42 that is a 'int')"),
    ):
        status_class(model_name=42, message="Foo")

    with pytest.raises(
        TypeError, match=re.escape("'message' must be 'str' (got 42 that is a 'int')")
    ):
        status_class(model_name="Foo", message=42)


def test_plugin_info():
    from alfasim_sdk.status import PluginInfo

    error_msg = "'name' must be 'str' (got 1 that is a 'int')"
    with pytest.raises(TypeError, match=re.escape(error_msg)):
        PluginInfo(name=1, enabled="True", models="Anything")

    error_msg = "'enabled' must be <class 'bool'> (got 'True' that is a <class 'str'>)."
    with pytest.raises(TypeError, match=re.escape(error_msg)):
        PluginInfo(name="Acme", enabled="True", models="Anything")

    error_msg = (
        "'models' must be <class 'list'> (got 'Anything' that is a <class 'str'>)."
    )
    with pytest.raises(TypeError, match=re.escape(error_msg)):
        PluginInfo(name="Acme", enabled=True, models="Anything")

    error_msg = "'models' must be <class 'str'> (got 1 that is a <class 'int'>)."
    with pytest.raises(TypeError, match=re.escape(error_msg)):
        PluginInfo(name="Acme", enabled=True, models=[1, 2, 3])

    PluginInfo(name="Acme", enabled=True, models=["1", "2"])


def test_pipeline_segments():
    from alfasim_sdk.status import PipelineSegmentInfo

    error_msg = "'edge_name' must be 'str' (got 1 that is a 'int')"
    with pytest.raises(TypeError, match=re.escape(error_msg)):
        PipelineSegmentInfo(edge_name=1, inner_diameter=1, start_position=1)

    error_msg = "'inner_diameter' must be <class 'barril.units._scalar.Scalar'> (got 1 that is a <class 'int'>)."
    with pytest.raises(TypeError, match=re.escape(error_msg)):
        PipelineSegmentInfo(edge_name="Foo", inner_diameter=1, start_position=1)

    error_msg = "'start_position' must be <class 'barril.units._scalar.Scalar'> (got 1 that is a <class 'int'>)."
    from barril.units import Scalar

    with pytest.raises(TypeError, match=re.escape(error_msg)):
        PipelineSegmentInfo(
            edge_name="Foo", inner_diameter=Scalar(0.15, "m"), start_position=1
        )

    PipelineSegmentInfo(
        edge_name="Foo",
        inner_diameter=Scalar(0.15, "m"),
        start_position=Scalar(0.0, "m"),
    )


@pytest.mark.parametrize("class_with_info", [NodesInfo, EdgesInfo])
def test_nodes_and_edges_info(class_with_info):
    assert class_with_info(name="Foo", number_of_phases=1)
    assert class_with_info(name="Foo", number_of_phases=None)

    # number_of_phases must be int or None
    with pytest.raises(TypeError):
        class_with_info(name="Foo", number_of_phases="1")

    # name must be string and not empty
    with pytest.raises(TypeError):
        class_with_info(name=None, number_of_phases=1)

    # name must be string and not empty
    with pytest.raises(ValueError):
        class_with_info(name="", number_of_phases=1)


def test_physics_option():
    assert PhysicsOptionsInfo(
        emulsion_model=EmulsionModelType.boxall2012,
        solids_model=SolidsModelType.no_model,
        hydrodynamic_model=HydrodynamicModelInfo(
            phases=["1", "2"], fields=["3", "4"], layers=["5", "6"]
        ),
    )
