import pytest


def test_enable_expr():
    from alfasim_sdk.types import String

    with pytest.raises(TypeError, match="enable_expr must be a function, got a <class 'str'>"):
        String(value="value", caption="caption", enable_expr="")

    def function_definition():
        pass

    String(value="value", caption="caption", enable_expr=None)
    String(value="value", caption="caption", enable_expr=function_definition)


def test_string():
    from alfasim_sdk.types import String

    with pytest.raises(TypeError):
        String(value="acme")

    with pytest.raises(TypeError, match="'value' must be <class 'str'>"):
        String(value=1, caption="caption")


def test_enum():
    from alfasim_sdk.types import Enum

    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'caption'"):
        Enum(values=["s"], initial="")

    with pytest.raises(TypeError, match="values must be a list, got a 'str'."):
        Enum(values="", caption="caption")

    with pytest.raises(TypeError, match="values must be a list of strings, the item '1' is a 'int'"):
        Enum(values=[1], caption="caption")

    with pytest.raises(ValueError, match='Enum type cannot have an empty string on field "values"'):
        Enum(values=[""], caption="caption")

    enum = Enum(values=["value"], caption="caption")
    assert enum.initial is None

    enum = Enum(values=["value"], initial="value", caption="caption")
    assert enum.initial == "value"

    with pytest.raises(TypeError, match="The initial condition must be within the declared values"):
        Enum(values=["value1, value2"], initial="", caption="caption")


def test_reference():
    from alfasim_sdk.types import Reference, TracerType

    class Data1:
        pass

    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'caption'"):
        Reference(ref_type="")

    with pytest.raises(TypeError, match="arg 1 must be a class"):
        Reference(ref_type="", caption="caption")

    with pytest.raises(TypeError, match="ref_type must be a valid ALFAsim type"):
        Reference(ref_type=Data1, caption="caption")

    assert Reference(ref_type=TracerType, caption="caption") is not None


def test_reference_selection():
    from alfasim_sdk.types import ReferenceSelection
    from alfasim_sdk.models import data_model, container_model

    @data_model(caption="Model")
    class DataModelClass:
        pass

    @container_model(model=DataModelClass, caption="Container", icon="")
    class ContainerModelClass:
        pass

    class FooClass:
        pass

    with pytest.raises(TypeError, match="list_type must be a class, got list"):
        ReferenceSelection(list_type=[], caption="test_reference_selection")

    with pytest.raises(TypeError, match="list_type must be a class decorated with 'container_model'"):
        ReferenceSelection(list_type=FooClass, caption="test_reference_selection")

    with pytest.raises(TypeError, match="list_type must be a class decorated with 'container_model'"):
        ReferenceSelection(list_type=DataModelClass, caption="test_reference_selection")

    ReferenceSelection(list_type=ContainerModelClass, caption="test_reference_selection")


def test_quantity():
    from alfasim_sdk.types import Quantity

    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'caption'"):
        Quantity(value="", unit="")

    with pytest.raises(TypeError, match="'value' must be <class 'numbers.Real'>"):
        Quantity(value="", unit="", caption="caption")

    with pytest.raises(TypeError, match="'unit' must be <class 'str'>"):
        Quantity(value=1, unit=1, caption="caption")


def test_table():
    from alfasim_sdk.types import Table

    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'caption'"):
        Table(rows=[])

    with pytest.raises(TypeError, match="rows must be a list, got a <class 'str'>."):
        Table(rows="", caption="caption")

    with pytest.raises(TypeError, match="rows must be a list with TableColumn."):
        Table(rows=[], caption="caption")

    with pytest.raises(TypeError, match="rows must be a list of TableColumn."):
        Table(rows=[""], caption="caption")


def test_table_column():
    from alfasim_sdk.types import TableColumn, Quantity

    with pytest.raises(TypeError, match="value must be a Quantity, got a <class 'str'>."):
        TableColumn(id="id", value="")

    column = TableColumn(id="id", value=Quantity(value=1, unit="m", caption="CAPTION FOR COLUMN"))
    assert column.caption == column.value.caption


def test_boolean():
    from alfasim_sdk.types import Boolean

    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'caption'"):
        Boolean(value="")

    with pytest.raises(TypeError, match="'value' must be <class 'bool'"):
        Boolean(value=1, caption="caption")
