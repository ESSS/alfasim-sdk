import pytest


def test_string():
    from alfasim_sdk.data_types import String

    with pytest.raises(TypeError, match="missing 1 required positional argument: 'CAPTION'"):
        String(value='acme')

    with pytest.raises(TypeError, match="'value' must be <class 'str'>"):
        String(value=1, CAPTION='')


def test_enum():
    from alfasim_sdk.data_types import Enum

    with pytest.raises(TypeError, match="missing 1 required positional argument: 'CAPTION'"):
        Enum(value=['s'], initial='')

    with pytest.raises(TypeError,
        match="value must be a sequence type \(list or set only\), got a <class 'str'>."):
        Enum(value='', CAPTION='')

    with pytest.raises(TypeError, match="value must be a \(list or tuple\) of string."):
        Enum(value=[1], CAPTION='')

    enumerate = Enum(value=[''], CAPTION='')
    assert enumerate.initial is None

    enumerate = Enum(value=[''], initial='', CAPTION='')
    assert enumerate.initial == ''

    with pytest.raises(TypeError, match="The initial condition must be within the declared values"):
        Enum(value=['value1, value2'], initial='', CAPTION='')


def test_data_reference():
    from alfasim_sdk.data_types import DataReference, TracerType

    class Data1:
        pass


    with pytest.raises(TypeError, match="missing 1 required positional argument: 'CAPTION'"):
        DataReference(value='')

    with pytest.raises(TypeError, match="arg 1 must be a class"):
        DataReference(value='', CAPTION='')

    with pytest.raises(TypeError, match="value must be a valid AlfaSim type"):
        DataReference(value=Data1, CAPTION='')

    assert DataReference(value=TracerType, CAPTION='') is not None


def test_quantity():
    from alfasim_sdk.data_types import Quantity

    with pytest.raises(TypeError, match="missing 1 required positional argument: 'CAPTION'"):
        Quantity(value='', unit='')

    with pytest.raises(TypeError, match="'value' must be <class 'numbers.Real'>"):
        Quantity(value='', unit='', CAPTION='')

    with pytest.raises(TypeError, match="'unit' must be <class 'str'>"):
        Quantity(value=1, unit=1, CAPTION='')


def test_table():
    from alfasim_sdk.data_types import Table

    with pytest.raises(TypeError, match="missing 1 required positional argument: 'CAPTION'"):
        Table(value='')

    with pytest.raises(TypeError, match="value must be a sequence type \(list or set only\)"):
        Table(value='', CAPTION='')

    with pytest.raises(TypeError, match="value must be a \(list or tuple\) of Quantity."):
        Table(value=[''], CAPTION='')


def test_boolean():
    from alfasim_sdk.data_types import Boolean

    with pytest.raises(TypeError, match="missing 1 required positional argument: 'CAPTION'"):
        Boolean(value='')

    with pytest.raises(TypeError, match="'value' must be <class 'bool'"):
        Boolean(value=1, CAPTION='')
