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
