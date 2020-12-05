.. _alfacase-quick-start-section:

Quick Start
===========

In this section, it is shown how to create an :program:`ALFAcase` from an existent project, with this exported project
you can easily modify your project and reintroduce it, with the modification, back to |alfasim|.

Open an ALFAsim Project
-----------------------

One of the easiest ways to get started is to export an existing project into a ``.alfascase`` file directly from the interface.
Open an existing project and export it using the option :code:`Export ALFAsim Case file...` as illustrated on the figure below:

.. image:: /_static/images/alfacase/export_alfacase.png

The generated file will contain all project settings, including the default values used by ALFAsim.

.. note::

    Note that in general default values can be omitted when producing ``.alfacase`` files manually.

For illustration, an ``.alfacase`` file looks like this:

.. code-block:: yaml
   :caption: project.alfacase

    pipes:
    - name: Conn 1
      source: Node 1
      target: Node 2
      segments:
        start_positions:
          values: [0.0]
          unit: m
        diameters:
          values: [0.1]
          unit: m
        roughnesses:
          values: [5e-05]
          unit: m
    nodes:
    - name: Node 1
      node_type: mass_source_boundary
    - name: Node 2
      node_type: pressure_boundary
