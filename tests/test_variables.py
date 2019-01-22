import pytest


def test_additional_variable():
    from alfasim_sdk.variables import Variable, Visibility, Location, Scope

    with pytest.raises(TypeError, match="'visibility' must be <enum 'Visibility'>"):
        Variable(name='', caption='', unit='', visibility='')

    with pytest.raises(TypeError, match="'location' must be <enum 'Location'>"):
        Variable(name='', caption='', unit='', location='')

    with pytest.raises(TypeError, match="'multifield_scope' must be <enum 'Scope'>"):
        Variable(name='', caption='', unit='', multifield_scope='')

    variable = Variable(
        name='var_name',
        caption='Var Name',
        unit='?',
        visibility=Visibility.Output,
        location=Location.Center,
        multifield_scope=Scope.Global,
        checked_on_gui_default=False,
    )

    assert variable
