.. _plugin_structure-section:

Plugins Structure
=================

.. |sdk| replace:: :program:`ALFAsim-SDK`

|sdk| has CLI utilities to help in the process to create a plugin.
At any moment, it's possible to invoke the help command to list all commands available.

.. code-block:: bash
   >>> alfasim-sdk --help
   ...


As mentioned on

.. _alfasim_sdk_cli_template_section:

.. click:: alfasim_sdk.cli:template
    :prog: alfasim-sdk template
    :show-nested:


.. click:: alfasim_sdk.cli:package
    :prog: alfasim-sdk package
    :show-nested:


