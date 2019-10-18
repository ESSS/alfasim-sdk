.. _life_cycle_section:

Life Cycle
==========


.. _main_overview:

Main Overview
-------------

.. f [label=" x ", shape="note", color="#ffffff" ,fontcolor="#ffffff"];

.. graphviz::

    digraph {
            nodesep = 0.7;
            node [peripheries="2", fillcolor="#3AB882" style=filled color="#3AB882" fontcolor="#ffffff" shape=""];
            edge [ color="#8699A3" ];

            init [label="Initialize Simulation", shape=""];
            end [label="End of Simulation", shape=""];
            config [label="Solver Configuration"];
            solver [label="Solver (Transient)"];
            time [
                    fixedsize=true,
                    label="Time Step",
                    //height="1.0",
                    width="1.0",
                    shape="circle",
                    //regular="true",
                    ];

            hook_initialize_point [shape = point, width = 0 ]
            decision [
                    label="Final \n Time?",
                    shape="diamond"
                    fixedsize=true
                    width=2.0
                    height=1.0
                    ]
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
            decision -> hook_finalize_point [arrowhead= none, label="Yes"];
            decision:w -> time:w [label="No"];
            hook_finalize_point ->  hook_finalize [style=dotted, color="#DA5961"];
            hook_finalize_point ->  end;

        }

.. _hyd_solver:

Hydrodynamic Solver
-------------------

.. graphviz::

    digraph {

        nodesep = 0.9;
        newrank=true;
        node [
            peripheries="1",
            fillcolor="#3AB882"
            color="#3AB882"
            fontcolor="#ffffff"
            shape="reactangle",
            style="rounded, filled",
            ];
        edge [ color="#8699A3" ];

        hydrodynamic_1 [label="Primary Variables"];
        hydrodynamic_2 [label="State Variables"];

        hydrodynamic_3 [label="Secondary Variables"];
        hydrodynamic_4 [label="Source Terms"];



        // Align Notes
        subgraph cluster2{
            labeljust="l"
            style="rounded, dashed"
            color="#8699A3"
            label="Notes"
        note_1 [label="P, U", shape=box, color="#3AB882",fillcolor="#FFFFFF", fontcolor="#3AB882"]
        note_2 [label="P, mi = f(P,T)", shape=box, color="#3AB882",fillcolor="#FFFFFF", fontcolor="#3AB882"]
        note_3 [label="Mass Flow Rate, \n Flow Pattern", shape=box, color="#3AB882",fillcolor="#FFFFFF", fontcolor="#3AB882"]
        }
        hydrodynamic_1 -> note_1 [arrowhead=none, style=dashed, constraint=false,];
        hydrodynamic_2 -> note_2 [arrowhead=none, style=dashed, constraint=false,];
        hydrodynamic_3 -> note_3 [arrowhead=none, style=dashed, constraint=false,];

        {rank=same; hydrodynamic_1; note_1}
        {rank=same; hydrodynamic_2; note_2}
        {rank=same; hydrodynamic_3; note_3}

        note_1->note_2->note_3[ style = invis ]

        invisible_init [shape=point, style=invis]
        invisible_end [shape=point, style=invis]

        invisible_init -> hydrodynamic_1
        hook_calculate_source_terms_point -> invisible_end ;

        // Align Hooks

        hook_update_variables_point [shape = point, width = 0 ]
        hook_calculate_source_terms_point [shape = point, width = 0 ]

        hook_update_variables [
            peripheries="0"
            label="HOOK_UPDATE_SECONDARY_VARIABLES", shape="cds", color="#DA5961", fontcolor="#DA5961", style=""
            URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.initialize", target="_top"
        ]
        hook_calculate_mass_source_terms [peripheries="0"
            label="HOOK_CALCULATE_MASS_SOURCE_TERM", shape="cds", color="#DA5961",  fontcolor="#DA5961" , style=""
            URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.finalize", target="_top"
        ]
        hook_calculate_momentum_source_terms [peripheries="0"
            label="HOOK_CALCULATE_MOMENTUM_SOURCE_TERM", shape="cds", color="#DA5961",  fontcolor="#DA5961" , style=""
            URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.finalize", target="_top"
        ]
        hook_calculate_energy_source_terms [peripheries="0"
            label="HOOK_CALCULATE_ENERGY_SOURCE_TERM", shape="cds", color="#DA5961",  fontcolor="#DA5961" , style=""
            URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.finalize", target="_top"
        ]
        {rank = same; hook_update_variables_point; hook_update_variables        }
        {rank = same; hook_calculate_source_terms_point; hook_calculate_momentum_source_terms; }


        // node[group=a, shape="circle", color=""]
        // hook_calculate_mass_source_terms; hook_calculate_momentum_source_terms; hook_calculate_energy_source_terms

        hook_calculate_mass_source_terms -> hook_calculate_momentum_source_terms -> hook_calculate_energy_source_terms [constraint=true, style=invis]
        // Define Main Flow
        subgraph cluster1{
            labeljust="l"
            style="rounded, dashed"
            color="#8699A3"
            label="Hydrodynamic Solver"
        hydrodynamic_1 -> hydrodynamic_2 -> hydrodynamic_3
        hydrodynamic_3 -> hook_update_variables_point [arrowhead=none, ltail=cluster1]
        hook_update_variables_point -> hydrodynamic_4
        hydrodynamic_4 -> hook_calculate_source_terms_point [arrowhead=none]
        }
        hook_update_variables_point -> hook_update_variables [constraint=false, style=dotted, color="#DA5961"]
        hook_calculate_source_terms_point -> hook_calculate_mass_source_terms:w [constraint=false, style=dotted, color="#DA5961"]
        hook_calculate_source_terms_point -> hook_calculate_momentum_source_terms [constraint=false, style=dotted, color="#DA5961"]
        hook_calculate_source_terms_point -> hook_calculate_energy_source_terms:w [constraint=false, style=dotted, color="#DA5961"]



        }
