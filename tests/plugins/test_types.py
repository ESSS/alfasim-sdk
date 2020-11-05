import re

import pytest

from alfasim_sdk.types import MultipleReference
from alfasim_sdk.types import Reference


@pytest.mark.parametrize("expression_type", ["enable_expr", "visible_expr"])
def test_enable_expr_and_visible_expr(expression_type):
    from alfasim_sdk.types import String

    inputs = {"value": "value", "caption": "caption", expression_type: ""}
    with pytest.raises(TypeError, match=f"'{expression_type}' must be callable"):
        String(**inputs)

    def function_definition():
        pass

    valid_input_1 = {"value": "value", "caption": "caption", expression_type: None}
    valid_input_2 = {
        "value": "value",
        "caption": "caption",
        expression_type: function_definition,
    }
    String(**valid_input_1)
    String(**valid_input_2)


def test_string():
    from alfasim_sdk.types import String

    with pytest.raises(
        TypeError, match="missing 1 required keyword-only argument: 'caption'"
    ):
        String(value="acme")

    with pytest.raises(
        TypeError, match=re.escape("'caption' must be 'str' (got 1 that is a 'int')")
    ):
        String(value="acme", caption=1)

    with pytest.raises(
        TypeError, match=re.escape("'value' must be 'str' (got 1 that is a 'int')")
    ):
        String(value=1, caption="caption")


def test_enum():
    from alfasim_sdk.types import Enum

    with pytest.raises(
        TypeError, match="missing 1 required keyword-only argument: 'caption'"
    ):
        Enum(values=["s"], initial="")

    with pytest.raises(TypeError, match="values must be a list, got a 'str'."):
        Enum(values="", caption="caption")

    with pytest.raises(
        TypeError, match="values must be a list of strings, the item '1' is a 'int'"
    ):
        Enum(values=[1], caption="caption")

    with pytest.raises(
        ValueError, match='Enum type cannot have an empty string on field "values"'
    ):
        Enum(values=[""], caption="caption")

    enum = Enum(values=["value"], caption="caption")
    assert enum.initial is None

    enum = Enum(values=["value"], initial="value", caption="caption")
    assert enum.initial == "value"

    with pytest.raises(
        TypeError, match="The initial condition must be within the declared values"
    ):
        Enum(values=["value1, value2"], initial="", caption="caption")


@pytest.mark.parametrize("class_", [Reference, MultipleReference])
def test_reference(class_):
    from alfasim_sdk.types import TracerType
    from alfasim_sdk.models import data_model, container_model

    @data_model(caption="caption")
    class Data:
        pass

    @container_model(caption="caption", model=Data, icon="")
    class DataContainer:
        pass

    class InvalidClass:
        pass

    with pytest.raises(
        TypeError, match="missing 1 required keyword-only argument: 'caption'"
    ):
        class_(ref_type="")

    with pytest.raises(TypeError, match="ref_type must be a class"):
        class_(ref_type="", caption="caption")

    with pytest.raises(
        TypeError,
        match="ref_type must be an ALFAsim type or a class decorated with 'data_model'",
    ):
        class_(ref_type=InvalidClass, caption="caption")

    error_msg = "ref_type must be an ALFAsim type or a class decorated with 'data_model', got a class decorated with 'container_model'"
    with pytest.raises(TypeError, match=error_msg):
        class_(ref_type=DataContainer, caption="caption")

    error_msg = "The container_type field must be given when ref_type is a class decorated with 'data_model'"
    with pytest.raises(TypeError, match=error_msg):
        class_(ref_type=Data, caption="caption")

    with pytest.raises(ValueError, match='The field "container_type" cannot be empty'):
        class_(ref_type=Data, container_type="", caption="caption")

    assert (
        class_(ref_type=Data, container_type="DataContainer", caption="caption")
        is not None
    )
    assert class_(ref_type=TracerType, caption="caption") is not None


def test_quantity():
    from alfasim_sdk.types import Quantity

    with pytest.raises(
        TypeError, match="missing 1 required keyword-only argument: 'caption'"
    ):
        Quantity(value="", unit="")

    with pytest.raises(TypeError, match="'value' must be <class 'numbers.Real'>"):
        Quantity(value="", unit="", caption="caption")

    with pytest.raises(
        TypeError, match=re.escape("'unit' must be 'str' (got 1 that is a 'int')")
    ):
        Quantity(value=1, unit=1, caption="caption")


def test_table():
    from alfasim_sdk.types import Table

    with pytest.raises(
        TypeError, match="missing 1 required keyword-only argument: 'caption'"
    ):
        Table(rows=[])

    with pytest.raises(TypeError, match="rows must be a list with TableColumn."):
        Table(rows=[], caption="caption")

    with pytest.raises(TypeError, match="rows must be a list of TableColumn."):
        Table(rows=[""], caption="caption")


def test_table_column():
    from alfasim_sdk.types import TableColumn, Quantity

    with pytest.raises(
        TypeError, match="value must be a Quantity, got a <class 'str'>."
    ):
        TableColumn(id="id", value="")

    column = TableColumn(
        id="id", value=Quantity(value=1, unit="m", caption="CAPTION FOR COLUMN")
    )
    assert column.caption == column.value.caption


def test_boolean():
    from alfasim_sdk.types import Boolean

    with pytest.raises(
        TypeError, match="missing 1 required keyword-only argument: 'caption'"
    ):
        Boolean(value="")

    with pytest.raises(TypeError, match="'value' must be <class 'bool'"):
        Boolean(value=1, caption="caption")


def test_file_content():
    from alfasim_sdk.types import FileContent

    FileContent(caption="Test")


def test_tooltips():
    from alfasim_sdk.types import Boolean

    field = Boolean(value=True, caption="caption")
    assert field.tooltip == ""

    field = Boolean(value=True, caption="caption", tooltip="Test123")
    assert field.tooltip == "Test123"

    expected_msg = re.escape(
        "'tooltip' must be <class 'str'> (got 2 that is a <class 'int'>)."
    )
    with pytest.raises(TypeError, match=expected_msg):
        Boolean(value=True, caption="caption", tooltip=2)

    field = Boolean(value=True, caption="caption", tooltip="∩ ∪ ∫ ∬ ∭ ∮")
    assert field.tooltip == "∩ ∪ ∫ ∬ ∭ ∮"
