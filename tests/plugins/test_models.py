import pytest


@pytest.fixture
def user_data_model():
    from alfasim_sdk.models import data_model
    from alfasim_sdk.types import BaseField

    class ValidType(BaseField):
        pass

    @data_model(icon="model.png", caption="PLUGIN DEV MODEL")
    class Model:
        valid_attribute = ValidType(caption="valid")

    return Model


@pytest.fixture
def user_data_container(user_data_model):
    from alfasim_sdk.models import container_model
    from alfasim_sdk.types import BaseField

    class ValidType(BaseField):
        pass

    @container_model(
        model=user_data_model, icon="container.png", caption="PLUGIN DEV CONTAINER"
    )
    class Container:
        container_valid_attribute = ValidType(caption="valid")

    return Container


def test_data_model(user_data_model):
    import attr

    # Attributes from the class, should be accessed by _alfasim_metadata
    assert user_data_model._alfasim_metadata["caption"] == "PLUGIN DEV MODEL"
    assert user_data_model._alfasim_metadata["icon"] == "model.png"

    # "data_model" should not have references to others model
    assert user_data_model._alfasim_metadata["model"] is None

    # Attributes defined from the user should be accessed by attr fields
    assert attr.fields(user_data_model).valid_attribute is not None


def test_data_container(user_data_container):
    import attr

    assert user_data_container._alfasim_metadata["model"] is not None
    assert "Model" in str(user_data_container._alfasim_metadata["model"])

    assert user_data_container._alfasim_metadata["caption"] == "PLUGIN DEV CONTAINER"
    assert user_data_container._alfasim_metadata["icon"] == "container.png"

    assert attr.fields(user_data_container).container_valid_attribute is not None


def test_invalid_attribute():
    from alfasim_sdk.models import data_model
    from alfasim_sdk.types import BaseField

    class ValidType(BaseField):
        pass

    error_msg = "Error defining _invalid_attribute, attributes starting with '_' are not allowed"

    with pytest.raises(TypeError, match=error_msg):

        @data_model(icon="model.png", caption="PLUGIN DEV MODEL")
        class ModelPrivateAttribute:  # pylint: disable=unused-variable
            _invalid_attribute = ValidType(caption="invalid")

    class Invalid(object):
        pass

    error_msg = (
        "Error defining invalid, attributes must be a valid type defined by alfasim_sdk"
    )
    with pytest.raises(TypeError, match=error_msg):

        @data_model(icon="model.png", caption="PLUGIN DEV MODEL")
        class Model:  # pylint: disable=unused-variable
            invalid = Invalid()


def test_attribute_order():
    from alfasim_sdk.models import data_model
    from alfasim_sdk.types import Boolean, Reference, TracerType, Enum, String, Quantity

    @data_model(icon="", caption="caption")
    class Model:
        boolean = Boolean(value=True, caption="caption")
        data_reference = Reference(ref_type=TracerType, caption="caption")
        enum = Enum(values=["value_1", "value_2"], caption="caption")
        string = String(value="value", caption="caption")
        quantity = Quantity(value=1, unit="m", caption="caption")

    expected_order = ["boolean", "data_reference", "enum", "string", "quantity"]
    assert [attr.name for attr in Model.__attrs_attrs__] == expected_order
