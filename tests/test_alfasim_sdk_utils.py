import pytest


@pytest.mark.parametrize(
    "version, expected",
    [
        ("0.1.0", ">=0.1"),
        ("1.0.0", ">=1.0"),
        ("1.1.1", ">=1.1"),
        ("2.0.1", ">=2.0"),
        ("2.0.2", ">=2.0"),
    ],
)
def test_get_extras_default_required_version(mocker, version, expected):
    from alfasim_sdk._internal.alfasim_sdk_utils import (
        get_extras_default_required_version,
    )

    mock_version = mocker.patch(
        "alfasim_sdk._internal.alfasim_sdk_utils.get_current_version", autospec=True
    )
    mock_version.return_value = version
    assert get_extras_default_required_version() == expected


def test_get_metadata() -> None:
    from alfasim_sdk import data_model
    from alfasim_sdk._internal.alfasim_sdk_utils import get_metadata

    @data_model(icon="model.png", caption="PLUGIN DEV MODEL")
    class Model:
        ...

    assert get_metadata(Model)["caption"] == "PLUGIN DEV MODEL"
    assert get_metadata(Model)["icon"] == "model.png"
