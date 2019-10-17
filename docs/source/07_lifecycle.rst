.. _life_cycle_section:

Life Cycle
==========


.. _main_overview:

Main Overview
-------------

.. f [label=" x ", shape="note", color="#ffffff" ,fontcolor="#ffffff"];

.. graphviz::

    digraph {
            //splines=false
            nodesep = 0.7;
            node [peripheries="2", fillcolor="#3AB882" style=filled color="#3AB882" fontcolor="#ffffff" shape=""];
            edge [ color="#8699A3" ];

            init [label="Initialize Simulation", shape=""];
            end [label="End of Simulation", shape=""];
            config [label="Solver Configuration"];
            solver [label="Solver (Transient)"];
            time [  fixedsize=true,
                    label="Time Step",
                    height="1.0",
                    width="1.0",
                    shape="circle",
                    regular="true",
                    ];

            hook_initialize_point [shape = point, width = 0 ]
            decision [label="If \nFinal Time", shape="diamond"]
            hook_finalize_point [shape = point, width = 0 ]
            hook_initialize [peripheries="0"
                label="HOOK_INITIALIZE", shape="cds", color="#DA5961", fontcolor="#DA5961", style=""
                URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.initialize", target="_top"
            ]
            hook_finalize [peripheries="0"
                label="HOOK_FINALIZE", shape="cds", color="#DA5961",  fontcolor="#DA5961" , style=""
                URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.finalize", target="_top"
            ]
            hyd_solver [label="Hydrodynamic Solver"]
            tracer_solver [label="Tracer Solver"]
            output [label="Output Variables"]

            {rank = same; hook_initialize_point; hook_initialize}
            {rank = same; hook_finalize_point; hook_finalize; }
            {rank=same; time;tracer_solver}
            {rank=same; solver;hyd_solver}


            init -> config;
            config -> hook_initialize_point [arrowhead= none];

            hook_initialize_point -> solver;
            hook_initialize_point -> hook_initialize [style=dotted, color="#DA5961"];

            solver -> time;
            time:ne -> hyd_solver:sw [style=dashed];
            output:nw -> time:se [style=dashed];

            hyd_solver -> tracer_solver;
            tracer_solver -> output;
            time -> decision;
            decision -> hook_finalize_point [arrowhead= none, label="True"];
            decision:w -> time:w [label="False"];
            hook_finalize_point ->  hook_finalize [style=dotted, color="#DA5961"];
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
