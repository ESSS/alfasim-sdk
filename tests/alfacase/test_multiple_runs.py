from pathlib import Path

from alfasim_sdk._internal.alfacase.alfacase_to_case import (
    DescriptionDocument,
    load_case_description,
)


def test_alcase_to_case_with_multiple_runs(datadir: Path) -> None:
    alfacase_file = datadir / "test_multiple_runs.alfacase"

    case = load_case_description(DescriptionDocument.from_file(alfacase_file))

    assert case.multiple_runs.variables == {"A": 1.0, "B": 2.0, "C": 3.0}
    assert case.multiple_runs.variations == {
        "1": {"A": 1.1, "B": 2.1, "C": 3.1},
        "2": {"A": 1.11, "B": 2.11, "C": 3.11},
    }
