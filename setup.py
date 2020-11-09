from pathlib import Path

from setuptools import setup

version_content = Path("src/_alfasim_sdk/version.py").read_text()
version_number = next(
    line.split("=")[1].strip().replace('"', "")
    for line in version_content.splitlines()
    if "__version__" in line
)
setup(version=version_number)
