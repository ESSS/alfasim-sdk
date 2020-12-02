.. _alfacase-quick-start-section:

ALFAcase Quick Start
====================

In this section, it is shown how to create an :program:`ALFAcase` from an existent project, with this exported project
you can easily modify your project and reintroduce it, with the modification, back to |alfasim|.

Open an ALFAsim Project
-----------------------

Open the |alfasim| application and create a project that includes some elements on the network, after that
export the project using the option :code:`Export ALFAsim Case file...` as illustrated on the figure bellow

.. image:: /_static/images/alfacase/export_alfacase.png

The generated file will have all its settings made in the project, plus the default settings used by ALFAsim.
Note that the default values can be omitted, so deleting this entry on the :program:`ALFAcase` will not affect your project.

For illustration, the project from the above could be easily expressed as:

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
