=========
Releasing
=========

1. Create a new branch.

2. Update the version in `version.py`_.

3. Update the release date in `CHANGELOG.rst`_.

4. Open a PR and add reviewers.

5. Once the PR has been **approved** and **all tests are passing**:

   1. Push a tag named ``v<release-version>``.
   2. Merge the PR -- make sure  to **merge** (as opposed to squash), as we want to preserve the commit where the tag was applied.

6. Create a new branch and:

   1. Update `version.py`_ to the next release version, adding the suffix `.dev`. For example, if the release just made was ``1.2.0``, change the version to ``1.3.0.dev``.
   2. Add a new *unreleased* section to `CHANGELOG.rst`_.
   3. Open a PR.


.. _version.py: src/alfasim_sdk/_internal/version.py
.. _CHANGELOG.rst: CHANGELOG.rst
