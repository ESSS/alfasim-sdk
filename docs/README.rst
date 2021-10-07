=========================
alfasim-sdk documentation
=========================

**Some advice when creating the documentation.**

When referencing a function or class inside the same module, you don't have to pass the complete path.
::
    def data_model():
        pass

    def container_model():
    """
    [..]  defined by the plugin and allows developers to build
    user interfaces in a declarative way similar to :func:`~data_model`.
    """
*Note:* `~` is used to show a reduced link to the user.

When documenting parameters, the type must be in a separated line:
::
    class Test:
    """
    :param model_name: Name of the model that issues the error.
    :type model_name: str
    """

When the type is from an external library, you must pass full path:
::
    class Test:
    """
    :param velocity: How fast we are going.
    :type velocity: ~barril.units.Scalar
    """


Building
--------

To build the docs, execute from the repository root:

.. code-block::

    $ conda devenv --file dev-environment.devenv.yml
    $ conda activate alfasim-sdk-dev
    $ inv docs
