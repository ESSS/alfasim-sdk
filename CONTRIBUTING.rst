.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.


Developing inside the ESSS
--------------------------

Here's how to set up `alfasim_sdk` for local development, when developing inside ESSS


#. Create a branch for local development from your main project::

    $ mu checkout -b fb-[PROJECT-KEY]-[ISSUE-NUMBER]-name-of-your-bugfix-or-feature

#. Install pre-commit::

    $ pre-commit install

#. When you're done making changes, run the tests::

    $ pytest

#. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin fb-[PROJECT-KEY]-[ISSUE-NUMBER]-name-of-your-bugfix-or-feature

    Notice that after the commit, the hooks from pre-commit will be run automatically, 
    if a fix it's required you need to add the modification to the stage area again.
    $ git add .
    
#. Submit a pull request through the GitHub website.


Get Started!
------------

Ready to contribute? Here's how to set up `alfasim_sdk` for local development.

#. Fork the `alfasim_sdk` repo on GitHub.
#. Clone your fork locally::

    $ git clone git@github.com:your_github_username_here/alfasim-sdk.git

#. Create a virtual environment and activate it::

    $ python -m virtualenv .env

    $ .env\Scripts\activate  # For Windows
    $ source .env/bin/activate  # For Linux

#. Install the development dependencies for setting up your fork for local development::

    $ cd alfasim_sdk/
    $ pip install -e .[testing,docs]

   .. note::

       If you use ``conda``, you can install ``virtualenv`` in the root environment::

           $ conda install -n root virtualenv

       Don't worry as this is safe to do.

#. Install pre-commit::

    $ pre-commit install

#. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

#. When you're done making changes, run the tests::

    $ pytest

#. If you want to check the modification made on the documentation, you can generate the docs locally::

    $ tox -e docs

   The documentation files will be generated in ``docs/_build``.

#. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

#. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated.
