import pytest


@pytest.mark.parametrize(
    "version, expected",
    [
        ("0.1.0", ">=0.1.0"),
        ("2024.1", ">=2024.1"),
        ("2024.1.dev", ">=2024.1.dev"),
    ],
)
def test_get_extras_default_required_version(mocker, version, expected):
    from alfasim_sdk._internal.alfasim_sdk_utils import (
        get_required_sdk_version,
    )

    mock_version = mocker.patch(
        "alfasim_sdk._internal.alfasim_sdk_utils.get_current_version", autospec=True
    )
    mock_version.return_value = version
    assert get_required_sdk_version() == expected


def test_get_metadata() -> None:
    from alfasim_sdk import data_model
    from alfasim_sdk._internal.alfasim_sdk_utils import get_metadata

    @data_model(icon="model.png", caption="PLUGIN DEV MODEL")
    class Model: ...

    assert get_metadata(Model)["caption"] == "PLUGIN DEV MODEL"
    assert get_metadata(Model)["icon"] == "model.png"
