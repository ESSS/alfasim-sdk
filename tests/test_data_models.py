import pytest


@pytest.fixture
def user_data_model():
    from alfasim_sdk.data_model import data_model
    from alfasim_sdk.data_types import BaseField

    class ValidType(BaseField):
        pass

    @data_model(icon="model.png", caption='PLUGIN DEV MODEL')
    class Model:
        valid_attribute = ValidType(caption="valid")
        _invalid_attribute = ValidType(caption="invalid")

    return Model


@pytest.fixture
def user_data_container(user_data_model):
    from alfasim_sdk.data_model import container_model
    from alfasim_sdk.data_types import BaseField

    class ValidType(BaseField):
        pass

    @container_model(model=user_data_model, icon="container.png", caption='PLUGIN DEV CONTAINER')
    class Container:
        container_valid_attribute = ValidType(caption="valid")
        _container_invalid_attribute = ValidType(caption="invalid")

    return Container


def test_data_model(user_data_model):
    import attr

    # Attributes from the class, should be accessed by _alfasim_metadata
    assert user_data_model._alfasim_metadata['caption'] == 'PLUGIN DEV MODEL'
    assert user_data_model._alfasim_metadata['icon'] == 'model.png'

    # "data_model" should not have references to others model
    assert user_data_model._alfasim_metadata['model'] is None

    # Attributes defined from the user should be accessed by attr fields
    assert attr.fields(user_data_model).valid_attribute is not None

    # Attributes with "_" at the beginning are reserved for application usage
    assert not hasattr(attr.fields(user_data_model), '_invalid_attribute')


def test_data_container(user_data_container):
    import attr

    assert user_data_container._alfasim_metadata['model'] is not None
    assert 'Model' in str(user_data_container._alfasim_metadata['model'])

    assert user_data_container._alfasim_metadata['caption'] == 'PLUGIN DEV CONTAINER'
    assert user_data_container._alfasim_metadata['icon'] == 'container.png'

    assert attr.fields(user_data_container).container_valid_attribute is not None
    assert not hasattr(attr.fields(user_data_container), '_container_invalid_attribute')
