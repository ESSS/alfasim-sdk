.. _alfacase-reference-section:

Full API Reference
==================

This page is a detailed reference guide to |sdk| API.
It includes a catalog of all supported CaseDescription and :program:`ALFAcase` capabilities.


Case
----

.. autoclass:: alfasim_sdk.CaseDescription()

.. _alfacase-reference-options-section:

Options
-------

.. autoclass:: alfasim_sdk.PhysicsDescription()

.. autoclass:: alfasim_sdk.TimeOptionsDescription()

.. autoclass:: alfasim_sdk.NumericalOptionsDescription()

.. _alfacase-reference-output-section:

Outputs
-------

.. autoclass:: alfasim_sdk.CaseOutputDescription()

.. autoclass:: alfasim_sdk.ProfileOutputDescription()

.. autoclass:: alfasim_sdk.TrendsOutputDescription()

.. autoclass:: alfasim_sdk.PositionalPipeTrendDescription()

.. autoclass:: alfasim_sdk.EquipmentTrendDescription()

.. autoclass:: alfasim_sdk.SeparatorTrendDescription()

.. autoclass:: alfasim_sdk.GlobalTrendDescription()

.. autoclass:: alfasim_sdk.OverallPipeTrendDescription()

.. _alfacase-reference-pvt-section:

PVTs
----

.. autoclass:: alfasim_sdk.PvtModelsDescription()

.. autoclass:: alfasim_sdk.PvtModelCorrelationDescription()

.. autoclass:: alfasim_sdk.PvtModelTableParametersDescription()


PVT Compositional
-----------------

.. autoclass:: alfasim_sdk.PvtModelCompositionalDescription()

.. autoclass:: alfasim_sdk.HeavyComponentDescription()

.. autoclass:: alfasim_sdk.LightComponentDescription()

.. autoclass:: alfasim_sdk.FluidDescription()

.. autoclass:: alfasim_sdk.CompositionDescription()

.. autoclass:: alfasim_sdk.BipDescription()


IPR
---

.. autoclass:: alfasim_sdk.IPRModelsDescription()

.. autoclass:: alfasim_sdk.LinearIPRDescription()

.. autoclass:: alfasim_sdk.TableIPRDescription()

.. autoclass:: alfasim_sdk.IPRCurveDescription()

Tracer
------

.. autoclass:: alfasim_sdk.TracersDescription()

.. autoclass:: alfasim_sdk.TracerModelConstantCoefficientsDescription()

Initial Conditions
-------------------

.. autoclass:: alfasim_sdk.InitialConditionsDescription()

.. autoclass:: alfasim_sdk.InitialPressuresDescription()

.. autoclass:: alfasim_sdk.ReferencedPressureContainerDescription()

.. autoclass:: alfasim_sdk.PressureContainerDescription()

.. autoclass:: alfasim_sdk.InitialVolumeFractionsDescription()

.. autoclass:: alfasim_sdk.ReferencedVolumeFractionsContainerDescription()

.. autoclass:: alfasim_sdk.VolumeFractionsContainerDescription()

.. autoclass:: alfasim_sdk.InitialTracersMassFractionsDescription()

.. autoclass:: alfasim_sdk.ReferencedTracersMassFractionsContainerDescription()

.. autoclass:: alfasim_sdk.TracersMassFractionsContainerDescription()

.. autoclass:: alfasim_sdk.InitialVelocitiesDescription()

.. autoclass:: alfasim_sdk.ReferencedVelocitiesContainerDescription()

.. autoclass:: alfasim_sdk.VelocitiesContainerDescription()

.. autoclass:: alfasim_sdk.InitialTemperaturesDescription()

.. autoclass:: alfasim_sdk.ReferencedTemperaturesContainerDescription()

.. autoclass:: alfasim_sdk.TemperaturesContainerDescription()

.. _alfacase-reference-pipe-section:

Pipe
----

.. autoclass:: alfasim_sdk.PipeDescription()

.. autoclass:: alfasim_sdk.PipeSegmentsDescription()


.. _alfacase-reference-node-section:

Node
----

.. autoclass:: alfasim_sdk.NodeDescription()

.. autoclass:: alfasim_sdk.PressureNodePropertiesDescription()

.. autoclass:: alfasim_sdk.MassSourceNodePropertiesDescription()

.. autoclass:: alfasim_sdk.InternalNodePropertiesDescription()

.. autoclass:: alfasim_sdk.SeparatorNodePropertiesDescription()

.. autoclass:: alfasim_sdk.ControllerInputSignalPropertiesDescription()

.. autoclass:: alfasim_sdk.ControllerOutputSignalPropertiesDescription()

.. autoclass:: alfasim_sdk.ControllerNodePropertiesDescription()


Well
----

.. autoclass:: alfasim_sdk.WellDescription()

.. autoclass:: alfasim_sdk.CasingDescription()

.. autoclass:: alfasim_sdk.CasingSectionDescription()

.. autoclass:: alfasim_sdk.TubingDescription()

.. autoclass:: alfasim_sdk.PackerDescription()

.. autoclass:: alfasim_sdk.OpenHoleDescription()

.. autoclass:: alfasim_sdk.AnnulusDescription()

.. autoclass:: alfasim_sdk.GasLiftValveEquipmentDescription()

.. autoclass:: alfasim_sdk.FormationDescription()

.. autoclass:: alfasim_sdk.FormationLayerDescription()


Material
--------

.. autoclass:: alfasim_sdk.MaterialDescription()

Wall
----

.. autoclass:: alfasim_sdk.WallDescription()

.. autoclass:: alfasim_sdk.WallLayerDescription()

Profile
-------

.. autoclass:: alfasim_sdk.ProfileDescription()

.. autoclass:: alfasim_sdk.XAndYDescription()

.. autoclass:: alfasim_sdk.LengthAndElevationDescription()


Environment
-----------

.. autoclass:: alfasim_sdk.EnvironmentDescription()

.. autoclass:: alfasim_sdk.EnvironmentPropertyDescription()


Equipment
----------

.. autoclass:: alfasim_sdk.EquipmentDescription()

.. autoclass:: alfasim_sdk.MassSourceEquipmentDescription()

.. autoclass:: alfasim_sdk.PumpEquipmentDescription()

.. autoclass:: alfasim_sdk.ValveEquipmentDescription()

.. autoclass:: alfasim_sdk.ReservoirInflowEquipmentDescription()

.. autoclass:: alfasim_sdk.HeatSourceEquipmentDescription()

.. autoclass:: alfasim_sdk.CompressorEquipmentDescription()

.. autoclass:: alfasim_sdk.SpeedCurveDescription()

.. autoclass:: alfasim_sdk.CompressorPressureTableDescription()


Tables
------

.. autoclass:: alfasim_sdk.TablePumpDescription()

.. autoclass:: alfasim_sdk.CvTableDescription()
