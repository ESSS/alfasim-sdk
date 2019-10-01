.. _plugin-by-example-section:

Plugin by Example
=================

In this section, it's showed how to customize the template plugin create from the previous section,
this plugin example will have a simple input on the graphical interface and issues a custom variable on
solver to be tracked during the simulation.

This allows you to experience the complete workflow in a short time.


.. contents::
    :depth: 3
    :local:



User interface customization
----------------------------

In order to add custom model on ALFAsim, that will be available on Tree and visualized on the Model Explorer you only need
implement the hook :ref:`alfasim_get_data_model_type <alfasim_get_data_model_type>`.
The hook :ref:`alfasim_get_data_model_type <alfasim_get_data_model_type>` expects a instance of container_model or



Pre-solver Customization
------------------------




Hooks for Solver
----------------
