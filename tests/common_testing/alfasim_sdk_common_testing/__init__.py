from pathlib import Path


def get_acme_tab_file_path() -> Path:
    """ Return a full path for the acme.tab file """
    return Path(__file__).parent / "acme.tab"
