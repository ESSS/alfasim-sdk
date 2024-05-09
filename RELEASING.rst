=========
Releasing
=========

When releasing a new branch should be created to update the release date for the version in ``CHANGELOG.str``.

The version being released is listed in https://github.com/ESSS/alfasim-sdk/blob/master/src/alfasim_sdk/_internal/version.py, if needed this value should be changed to match accordingly.

Any other required changes related to the release should also be included in the same branch.

When all changes are ready the branch should be tagged ``v<release-number>`` and merged.

After released, update `version.py <src/alfasim_sdk/_internal/version.py>`__ with the next release version planned for ALFAsim and add a new *unreleased* section to the ``CHANGELOG.rst``. Note that this version number appears on ALFAsim's About window, so should be done **before** the next ALFAsim planned release.
