.. _plugin_structure-section:

Plugins Structure
=================

As mentioned in :ref:`quick-start-section`, the |sdk| package has some utilities to help in the process to create
a new plugin project and to create a plugin file.

At any moment, it is possible to invoke the ``help`` command to list all commands available.

.. code-block:: bash

   >>> alfasim-sdk --help


You can also learn about the available options of each command invoking the :guilabel:`--help` option for each command:

.. code-block:: bash

   >>> alfasim-sdk template --help
   >>> alfasim-sdk package --help
   >>> alfasim-sdk compile --help

.. _alfasim_sdk_cli_template_section:

.. click:: alfasim_sdk.cli:template
    :prog: alfasim-sdk template
    :show-nested:


.. _alfasim_sdk_cli_package_section:

.. click:: alfasim_sdk.cli:package
    :prog: alfasim-sdk package
    :show-nested:


.. click:: alfasim_sdk.cli:package_only
    :prog: alfasim-sdk package_only
    :show-nested:

.. click:: alfasim_sdk.cli:_compile
    :prog: alfasim-sdk compile
    :show-nested:
