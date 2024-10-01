Configuration API
=================

Here is listed the complete API available to implement the :ref:`solver_config_hooks-section`.

.. contents::
    :depth: 3
    :local:

.. _api-mfd-section:

Hydrodynamic Model
------------------

.. autoclass:: alfasim_sdk.AddField()

.. autoclass:: alfasim_sdk.AddPhase()

.. autoclass:: alfasim_sdk.UpdatePhase()

.. autoclass:: alfasim_sdk.AddLayer()

.. autoclass:: alfasim_sdk.UpdateLayer()


.. _api-variables-section:

Secondary Variables
-------------------

.. autoclass:: alfasim_sdk.SecondaryVariable()

.. autoclass:: alfasim_sdk.Type()

.. autoclass:: alfasim_sdk.Visibility()

.. autoclass:: alfasim_sdk.Location()

.. autoclass:: alfasim_sdk.Scope()


.. _api-constants-section:

Constants
---------

.. autodata:: alfasim_sdk.GAS_PHASE

.. autodata:: alfasim_sdk.OIL_PHASE

.. autodata:: alfasim_sdk.WATER_PHASE

.. autodata:: alfasim_sdk.GAS_LAYER

.. autodata:: alfasim_sdk.OIL_LAYER

.. autodata:: alfasim_sdk.WATER_LAYER
