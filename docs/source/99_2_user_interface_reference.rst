Application API
===============

Here is listed the completed API available to implement the :ref:`user_interface_hooks-section`.

.. contents::
    :depth: 3
    :local:


.. _api-models-section:

Models
------

.. autofunction:: alfasim_sdk.models.data_model

.. autofunction:: alfasim_sdk.models.container_model


.. _api-types-section:

Types
-----

The ``types`` module supplies UI elements for creating user interfaces with the classic desktop-style, each type
has a related model.

Models are the primary elements to create user interfaces on |alfasim|, models can display data, receive user input,
and provide a container for other fields that should be grouped together.


.. autoclass:: alfasim_sdk.types.BaseField()

.. autoclass:: alfasim_sdk.types.String()

.. autoclass:: alfasim_sdk.types.Enum()

.. autoclass:: alfasim_sdk.types.Reference()

.. autoclass:: alfasim_sdk.types.MultipleReference()

.. autoclass:: alfasim_sdk.types.Quantity()

.. autoclass:: alfasim_sdk.types.Table()

.. autoclass:: alfasim_sdk.types.TableColumn()

.. autoclass:: alfasim_sdk.types.Boolean()

.. autoclass:: alfasim_sdk.types.FileContent()


.. _api-layout-section:

Layout
------

.. autofunction:: alfasim_sdk.layout.group()

.. autofunction:: alfasim_sdk.layout.tabs()

.. autofunction:: alfasim_sdk.layout.tab()


.. _api-status-section:

Status
------

.. automodule:: alfasim_sdk.status
    :members:


.. _api-context-section:

Context
-------

.. automodule:: alfasim_sdk.context
    :members:
