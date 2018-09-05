import pytest


@pytest.fixture
def user_data_model():
    from alfasim_sdk.data_model import data_model
    from alfasim_sdk.data_types import BaseField

    class ValidType(BaseField):
        pass

    @data_model(ICON="model.png", CAPTION='PLUGIN DEVELOPER MODEL')
    class Model:
        valid_attribute = ValidType(CAPTION="valid")
        _invalid_attribute = ValidType(CAPTION="invalid")

    return Model

@pytest.fixture
def user_data_container(user_data_model):
    from alfasim_sdk.data_model import container_model
    from alfasim_sdk.data_types import BaseField

    class ValidType(BaseField):
        pass

    @container_model(model=user_data_model, ICON="container.png", CAPTION='PLUGIN DEVELOPER CONTAINER')
    class Container:
        container_valid_attribute = ValidType(CAPTION="valid")
        _container_invalid_attribute = ValidType(CAPTION="invalid")

    return Container

def test_data_model(user_data_model):
    import attr

    # data_model should not have another reference to another model
    assert attr.fields(user_data_model).model.default is None

    assert attr.fields(user_data_model).CAPTION.default == 'PLUGIN DEVELOPER MODEL'
    assert attr.fields(user_data_model).ICON.default == 'model.png'

    assert attr.fields(user_data_model).valid_attribute is not None

    # Attributes with "_" at the beginning are reserved
    assert not hasattr(attr.fields(user_data_model),'_invalid_attribute')

def test_data_container(user_data_container):
    import attr

    assert attr.fields(user_data_container).model.default is not None
    assert 'Model' in str(attr.fields(user_data_container).model.default)

    assert attr.fields(user_data_container).CAPTION.default == 'PLUGIN DEVELOPER CONTAINER'
    assert attr.fields(user_data_container).ICON.default == 'container.png'

    assert attr.fields(user_data_container).container_valid_attribute is not None
    assert not hasattr(attr.fields(user_data_container), '_container_invalid_attribute')
