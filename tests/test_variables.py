import pytest


def test_additional_variable():
    from alfasim_sdk.variables import Variable, Visibility, Location, Scope

    with pytest.raises(ValueError, match='The field "name" cannot be empty'):
        Variable(name='', caption='caption', unit='m')

    with pytest.raises(ValueError, match='The field "caption" cannot be empty'):
        Variable(name='name', caption='  ', unit='m')

    with pytest.raises(TypeError, match="'visibility' must be <enum 'Visibility'>"):
        Variable(name='name', caption='caption', unit='m', visibility='')

    with pytest.raises(TypeError, match="'location' must be <enum 'Location'>"):
        Variable(name='name', caption='caption', unit='m', location='')

    with pytest.raises(TypeError, match="'multifield_scope' must be <enum 'Scope'>"):
        Variable(name='name', caption='caption', unit='m', multifield_scope='')

    with pytest.raises(ValueError, match="foo is not a valid unit"):
        Variable(name='name', caption='caption', unit='foo')

    variable = Variable(
        name='var_name',
        caption='Var Name',
        unit='m',
        visibility=Visibility.Output,
        location=Location.Center,
        multifield_scope=Scope.Global,
        checked_on_gui_default=False,
    )

    assert variable.category == 'length'
    assert variable.default_value == None

    with pytest.raises(TypeError, match="'default_value' must be <class 'numbers.Real'>"):
        Variable(name='name', caption='caption', unit='m', default_value='1')

    var2 = Variable(name='name', caption='caption', unit='m', default_value=1)
    assert var2.default_value == 1
