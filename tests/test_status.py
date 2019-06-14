import re

import pytest

from alfasim_sdk.status import ErrorMessage
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
