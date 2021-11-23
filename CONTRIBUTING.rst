============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and a credit will always be given.


Developing inside the ESSS
--------------------------

Here's how to set up `alfasim_sdk` for local development, when developing inside ESSS.

You don't need to create a new environment for ALFAsim-SDK, the workflow proceded, as usual, go to the app repository and activate the app environment.

The only thing that nows you need to execute ``pre-commit install`` from inside the alfasim-SDK repository to enable the git commit hook. commit, notice that this only needs to be executed once.

#. Install pre-commit::

    $ pre-commit install

Afterward, you can follow the same workflow as always.

#. Create a branch for local development from your main project::

    $ mu checkout -b fb-[PROJECT-KEY]-[ISSUE-NUMBER]-name-of-your-bugfix-or-feature

#. When you're done making changes, run the tests::

    $ pytest

#. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin fb-[PROJECT-KEY]-[ISSUE-NUMBER]-name-of-your-bugfix-or-feature

#. Submit a pull request through the GitHub website.

An important note here it's that when committing, ``pre-commit`` will re-format the files if necessary.

After the re-format, you need to add the modifications to the stage area again before proceeding with the commit, otherwise, the check will still fail.

Just as a side note, the pre-commit runs by default when committing only against the currently staged files.

You can run it at any time by typing ``pre-commit`` and it will run against all staged files.

If you want to explicitly run against all the files (like on CI) you can execute ```pre-commit run --all-files``

FAQ for developing inside ESSS
------------------------------

How do I create the environment?
 - You don't need to create a new environment for ALFAsim-SDK, the workflow proceded, as usual, go to the app repository and activate the app environment.

Do I need to install any external dependency?
 - No, If you have the app environment activate everything will work smoothly because he has already the dependency installed on the requirements.


Developing outside the ESSS
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

Building the Docs
-----------------

See `README.rst` in /docs for instructions and tips about building the docs.
