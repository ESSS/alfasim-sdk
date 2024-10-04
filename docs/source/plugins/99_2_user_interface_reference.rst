Application API
===============

Here is listed the complete API available to implement the :ref:`user_interface_hooks-section`.

.. contents::
    :depth: 3
    :local:


.. _api-models-section:

Models
------

.. autofunction:: alfasim_sdk.data_model

.. autofunction:: alfasim_sdk.container_model


.. _api-types-section:

Types
-----

The ``types`` module supplies UI elements for creating user interfaces with the classic desktop-style, each type
related to a model.

Models are the primary elements to create user interfaces on |alfasim|. They can display data, receive user input,
and provide a container for other fields that should be grouped together.


.. autoclass:: alfasim_sdk.BaseField()

.. autoclass:: alfasim_sdk.String()

.. autoclass:: alfasim_sdk.Enum()

.. autoclass:: alfasim_sdk.Reference()

.. autoclass:: alfasim_sdk.MultipleReference()

.. autoclass:: alfasim_sdk.Quantity()

.. autoclass:: alfasim_sdk.Table()

.. autoclass:: alfasim_sdk.TableColumn()

.. autoclass:: alfasim_sdk.Boolean()

.. autoclass:: alfasim_sdk.FileContent()


.. _api-layout-section:

Layout
------

.. autofunction:: alfasim_sdk.group()

.. autofunction:: alfasim_sdk.tabs()

.. autofunction:: alfasim_sdk.tab()


.. _api-status-section:

Status
------

.. autoclass:: alfasim_sdk.ErrorMessage()

.. autoclass:: alfasim_sdk.WarningMessage()


.. _api-context-section:

Context
-------

.. automodule:: alfasim_sdk._internal.context
    :members:
