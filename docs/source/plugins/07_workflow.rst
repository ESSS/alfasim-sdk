.. _workflow_section:

Simulator WorkFlow
===================

Here are shown some graphs of the |alfasim| simulator workflow. In those graphs, it is possible to identify when
the :ref:`solver_hooks` are called during the simulation. Some of them, like :ref:`hyd_solver` and  :ref:`tracer_solver`,
have their graphs expanded to make it possible to see more internal `hooks`.

.. _main_overview:

Main Overview
-------------

.. graphviz:: _static/graphviz/main_flow.dot


.. _hyd_solver:

Hydrodynamic Solver
-------------------

.. graphviz:: _static/graphviz/hydrodynamic_solver.dot



.. _state_var:

State Variable Calculator
-------------------------

.. graphviz:: _static/graphviz/state_variable_calculator.dot


.. _tracer_solver:

Tracer Solver
-------------

.. graphviz:: _static/graphviz/tracer_solver.dot
