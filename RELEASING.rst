=========
Releasing
=========

When releasing a new branch should be created to update the release date for the version in ``CHANGELOG.str``.

The version being released is listed in https://github.com/ESSS/alfasim-sdk/blob/master/src/alfasim_sdk/_internal/version.py, if needed this value should be changed to match accordingly.

Any other required changes related to the release should also be included in the same branch.

When all changes are ready the branch should be tagged ``v<release-number>`` and merged.

After released it is advisable to update https://github.com/ESSS/alfasim-sdk/blob/master/src/alfasim_sdk/_internal/version.py with the next release version (increase minor version, for example ``0.6.0`` to ``0.7.0``) and ``HISTORY.rst`` to add a section to next unreleased version.
