import pytest


@pytest.mark.parametrize(
    "attr, expected_type_error, expected_message",
    [
        (dict(name=""), ValueError, 'The field "name" cannot be empty'),
        (dict(caption=""), ValueError, 'The field "caption" cannot be empty'),
        (dict(unit="foo"), ValueError, "foo is not a valid unit"),
        (dict(visibility=""), TypeError, "'visibility' must be <enum 'Visibility'>"),
        (dict(location=""), TypeError, "'location' must be <enum 'Location'>"),
        (
            dict(multifield_scope=""),
            TypeError,
            "'multifield_scope' must be <enum 'Scope'>",
        ),
        (
            dict(default_value="1"),
            TypeError,
            "'default_value' must be <class 'numbers.Real'>",
        ),
        (dict(type=""), TypeError, "'type' must be <enum 'Type'>"),
    ],
)
def test_validation(attr, expected_type_error, expected_message):
    from alfasim_sdk._internal.variables import (
        Location,
        Scope,
        SecondaryVariable,
        Type,
        Visibility,
    )

    attrs = dict(
        name="var_name",
        caption="Var Name",
        type=Type.Int,
        unit="m",
        visibility=Visibility.Output,
        location=Location.Center,
        multifield_scope=Scope.Global,
        checked_on_gui_default=False,
    )
    assert SecondaryVariable(**attrs).category == "length"

    attrs.update(attr)
    with pytest.raises(expected_type_error, match=expected_message):
        SecondaryVariable(**attrs)


def test_variable_with_custom_category():
    from barril.units import UnitDatabase

    from alfasim_sdk._internal.variables import (
        Location,
        Scope,
        SecondaryVariable,
        Type,
        Visibility,
    )

    db = UnitDatabase.GetSingleton()
    length_units = ["mm", "cm", "um", "nm", "in"]
    db.AddCategory(
        "film thickness",
        quantity_type="length",
        valid_units=length_units,
        override=True,
        default_unit="mm",
    )

    attrs = dict(
        name="wax_thickness",
        caption="Wax Thickness",
        type=Type.Double,
        unit="mm",
        category="film thickness",
        visibility=Visibility.Output,
        location=Location.Center,
        multifield_scope=Scope.Global,
        checked_on_gui_default=False,
    )
    assert SecondaryVariable(**attrs).category == "film thickness"
