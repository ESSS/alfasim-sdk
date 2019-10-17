.. _life_cycle_section:

Life Cycle
==========


.. _main_overview:

Main Overview
-------------

.. f [label=" x ", shape="note", color="#ffffff" ,fontcolor="#ffffff"];

.. graphviz::

    digraph {
            splines=line
            nodesep = 0.6;
            node [fillcolor="#3AB882" style=filled color="#3AB882" fontcolor="#ffffff" shape=""];
            edge [ color="#8699A3" ];

            init [label="Run Simulation", shape=""];
            end [label="End", shape=""];
            config [label="Solver Configuration"];
            solver [label="Solver (Transient)"];
            time [label="Time Step Solver"];

            hook_initialize_point [shape = point, width = 0 ]
            invisible [shape = point, width = 0 ]
            hook_finalize_point [shape = point, width = 0 ]
            hook_initialize [label="HOOK_INITIALIZE", shape="cds", color="#DA5961",  fontcolor="#DA5961" , style=""]
            hook_finalize [label="HOOK_FINALIZE", shape="cds", color="#DA5961",  fontcolor="#DA5961" , style=""]

           node[group=a];
           hyd_solver; tracer_solver; output
           node[group=b];
           init; config; hook_initialize_point; solver; time; hook_finalize_point;end

           {rank = same; hook_initialize_point; hook_initialize}
           {rank = same; hook_finalize_point; hook_finalize; }
           {rank=same; time;tracer_solver}
           {rank=same; solver;hyd_solver}


            init -> config;
            config -> hook_initialize_point [arrowhead= none];

            hook_initialize_point -> solver;
            hook_initialize_point -> hook_initialize [style=dotted, color="#DA5961", nodesep = 1.5;];

            solver -> time;
            time -> hyd_solver [style=dashed];

            hyd_solver -> tracer_solver;
            tracer_solver -> output;
            output -> time [style=dashed];
            time -> invisible [arrowhead= none];
            invisible -> hook_finalize_point [arrowhead= none];
            //time -> hook_finalize_point [arrowhead= none];
            hook_finalize_point ->  hook_finalize [style=dotted, color="#DA5961", nodesep = 1.5;];
            hook_finalize_point ->  end;

        }

.. _hyd_solver:

Hydrodynamic Solver
-------------------

.. graphviz::
 digraph {
    hydrodynamic_1 [label="Primary Variables"];
        hydrodynamic_2 [label="State Variables"];
        hydrodynamic_3 [label="Secondary Variables"];
        hydrodynamic_4 [label="Source Terms"];
        tracer_1 [label="j Primary Variables"];
        tracer_2 [label="Secondary Variables"];
        tracer_3 [label="Source Terms"];
    subgraph cluster_hyd{
            hydrodynamic_1 -> hydrodynamic_2;
            hydrodynamic_2 -> hydrodynamic_3;
            hydrodynamic_3 -> hydrodynamic_4;
        }

        hyd_solver -> tracer_solver;
        tracer_solver -> tracer_1;
        tracer_1 -> tracer_2;
        tracer_2 -> tracer_3;
        tracer_3 -> tracer_solver;

}
