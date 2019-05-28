#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["Click>=6.0", "barril>=1.5.0"]

setup(
    author="ESSS",
    author_email="foss@esss.co",
    classifiers=[
        "Development Status :: 3 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="ALFAsim API/SDK",
    entry_points={
        "console_scripts": [
            "alfasim-sdk=alfasim_sdk.cli:main",
            "alfasim_sdk=alfasim_sdk.cli:main",
        ]
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="alfasim-sdk",
    name="alfasim-sdk",
    packages=find_packages(include=["alfasim-sdk"]),
    url="https://github.com/esss/alfasim-sdk",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    zip_safe=False,
)
