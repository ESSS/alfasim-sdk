import pytest


@pytest.mark.parametrize('attr, expected_type_error, expected_message', [
    (dict(name=''), ValueError, 'The field "name" cannot be empty'),
    (dict(caption=''), ValueError, 'The field "caption" cannot be empty'),
    (dict(unit='foo'), ValueError, 'foo is not a valid unit'),
    (dict(visibility=''), TypeError, "'visibility' must be <enum 'Visibility'>"),
    (dict(location=''), TypeError, "'location' must be <enum 'Location'>"),
    (dict(multifield_scope=''), TypeError, "'multifield_scope' must be <enum 'Scope'>"),
    (dict(default_value='1'), TypeError, "'default_value' must be <class 'numbers.Real'>"),

])
def test_validation(attr, expected_type_error, expected_message):
    from alfasim_sdk.variables import Visibility, Location, Scope, SecondaryVariable
    attrs = dict(
        name='var_name',
        caption='Var Name',
        unit='m',
        visibility=Visibility.Output,
        location=Location.Center,
        multifield_scope=Scope.Global,
        checked_on_gui_default=False,
    )
    attrs.update(attr)
    with pytest.raises(expected_type_error, match=expected_message):
        SecondaryVariable(**attrs)
