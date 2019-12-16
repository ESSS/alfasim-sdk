import pytest


@pytest.mark.parametrize(
    "version, expected",
    [
        ("0.1.0", ">=0.1, <1"),
        ("1.0.0", ">=1.0, <2"),
        ("1.1.1", ">=1.1, <2"),
        ("2.0.1", ">=2.0, <3"),
        ("2.0.2", ">=2.0, <3"),
    ],
)
def test_get_extras_default_required_version(mocker, version, expected):
    from alfasim_sdk._alfasim_sdk_utils import get_extras_default_required_version

    mock_version = mocker.patch(
        "alfasim_sdk._alfasim_sdk_utils.get_current_version", autospec=True
    )
    mock_version.return_value = version
    assert get_extras_default_required_version() == expected
