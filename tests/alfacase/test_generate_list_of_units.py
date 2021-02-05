import pytest

from alfasim_sdk._alfasim_sdk.alfacase.generate_case_description_docstring import (
    CATEGORIES_USED_ON_DESCRIPTION,
)
from alfasim_sdk._alfasim_sdk.alfacase.generate_case_description_docstring import (
    generate_list_of_units,
)


@pytest.mark.parametrize("category", CATEGORIES_USED_ON_DESCRIPTION)
def test_generate_list_of_units(category, file_regression):
    output = generate_list_of_units(category)
    file_regression.check(output, encoding="utf-8")
