import pytest

from alfasim_sdk._internal.alfacase import case_description
from alfasim_sdk._internal.alfacase.generate_case_description_docstring import (
    generate_definition,
)
from alfasim_sdk._internal.alfacase.generate_schema import (
    get_all_classes_that_needs_schema,
)


ALL_CLASSES_THAT_NEEDS_SCHEMA = get_all_classes_that_needs_schema(
    case_description.CaseDescription
)

# # Useful for debugging
# ALL_CLASSES_THAT_NEEDS_SCHEMA = [case_description.TrendOutputDescription]


@pytest.mark.parametrize("class_", ALL_CLASSES_THAT_NEEDS_SCHEMA)
def test_generate_case_description_docstring(class_, file_regression):
    output = generate_definition(class_)
    file_regression.check(output, encoding="utf-8")
