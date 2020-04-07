Configuration API
=================

Here is listed the completed API available to implement the :ref:`solver_config_hooks-section`.

.. contents::
    :depth: 3
    :local:

.. _api-mfd-section:

Hydrodynamic Model
------------------

.. autoclass:: alfasim_sdk.types.AddField()

.. autoclass:: alfasim_sdk.types.AddPhase()

.. autoclass:: alfasim_sdk.types.UpdatePhase()

.. autoclass:: alfasim_sdk.types.AddLayer()

.. autoclass:: alfasim_sdk.types.UpdateLayer()


.. _api-variables-section:

Secondary Variables
-------------------

.. autoclass:: alfasim_sdk.variables.SecondaryVariable()

.. autoclass:: alfasim_sdk.variables.Type()

.. autoclass:: alfasim_sdk.variables.Visibility()

.. autoclass:: alfasim_sdk.variables.Location()

.. autoclass:: alfasim_sdk.variables.Scope()


.. _api-constants-section:

Constants
---------

.. autodata:: alfasim_sdk.constants.GAS_PHASE

.. autodata:: alfasim_sdk.constants.OIL_PHASE

.. autodata:: alfasim_sdk.constants.WATER_PHASE

.. autodata:: alfasim_sdk.constants.GAS_LAYER

.. autodata:: alfasim_sdk.constants.OIL_LAYER

.. autodata:: alfasim_sdk.constants.WATER_LAYER
