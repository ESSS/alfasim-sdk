API
===

This page contains the full reference to ``ALFAsim-SDK`` API.

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

Models are the primary elements fro creating user interfaces on |alfasim|, models can display data, receive user input,
and provide a container for other fields that should be grouped together.

Types is a module which supplies UI elements for creating user interfaces with the classic desktop-style.

.. autoclass:: alfasim_sdk.types.BaseField()

.. autoclass:: alfasim_sdk.types.String()

.. autoclass:: alfasim_sdk.types.Enum()

.. autoclass:: alfasim_sdk.types.Reference()

.. _api-layout-section:

Layout
------

.. automodule:: alfasim_sdk.layout
    :members:

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

.. _api-mfd-section:

Hydrodymaic Model Customization
-------------------------------

.. autoclass:: alfasim_sdk.types.AddField()

.. autoclass:: alfasim_sdk.types.AddPhase()

.. autoclass:: alfasim_sdk.types.UpdatePhase()

.. autoclass:: alfasim_sdk.types.AddLayer()

.. autoclass:: alfasim_sdk.types.UpdateLayer()

.. _api-variables-section:

Variables
---------

.. automodule:: alfasim_sdk.variables
    :members:



.. _api-constants-section:

Constants
---------

.. automodule:: alfasim_sdk.constants
    :members:
