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
            //splines=polylines
            // splines=polyline
            // splines=ortho
            // splines=polyline
            node [
                peripheries="1",
                fillcolor="#FAAC2C"
                style="rounded, filled"
                color="#FAAC2C"
                fontcolor="#ffffff"
                shape="rectangular"
            ];
            edge [ color="#8699A3", fontcolor="#2c3e50" ];

            init [label="Initialize Simulation", shape=""]
            end [label="End of Simulation", shape=""]
            config [label="Solver Configuration"]
            solver [shape=point, width=0, peripheries="0"]

            time [
                    fixedsize=true,
                    label="Time Step",
                    width="1.0",
                    shape="circle",
                    ];

            hook_initialize_point [shape = point, width = 0, peripheries="2"]
            hook_finalize_point [shape = point, width = 0, peripheries="2" ]
            decision [label="Final \n Time?",shape="diamond" fixedsize=true width=2.0 height=1.0 labelcolor="#8699A3" style="filled"]
            hook_initialize [peripheries="0" label="HOOK_INITIALIZE", shape="cds", color="#DA5961", fontcolor="#DA5961", style=""
                URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.initialize", target="_top"
            ]
            hook_finalize [peripheries="0" label="HOOK_FINALIZE", shape="cds", color="#DA5961",  fontcolor="#DA5961" , style=""
                URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.finalize", target="_top"
            ]
            hyd_solver [label="Hydrodynamic Solver" URL="../07_lifecycle.html#hydrodynamic-solver", target="_top"]
            tracer_solver [label="Tracer Solver" URL="../07_lifecycle.html#tracer-solver", target="_top"]
            output [label="Output Variables"]

            {rank = same; hook_initialize_point; hook_initialize}
            {rank = same; hook_finalize_point; hook_finalize; }

            init -> config;
            config -> hook_initialize_point [arrowhead= none];

            hook_initialize_point -> solver [arrowhead=none];
            hook_initialize_point -> hook_initialize [style=dotted, color="#DA5961"];
            subgraph cluster_a{
                label="Transient Solver"
                style="dashed, rounded"
                shape="reactangular"
                color="#8699A3"
                fontcolor="#2c3e50"
                labeljust="l"

                {rank=same; time;tracer_solver}
                {rank=same; solver;hyd_solver}
                solver -> time;
                time:ne -> hyd_solver:w [style=dashed];

                hyd_solver -> tracer_solver [weight=999];
                tracer_solver -> output [weight=999];

                node[group=x]
                time;decision

                node[group=a]
                hyd_solver;tracer_solver;output

                output:nw -> time:se [style=dashed];
                time:s -> decision:n [weight=999];
                decision:w -> time:sw [label="No", weight=99];
            }
            decision -> hook_finalize_point [arrowhead= none, label="Yes"];
            hook_finalize_point ->  hook_finalize [style=dotted, color="#DA5961"];
            hook_finalize_point ->  end;

        }

.. _hyd_solver:

Hydrodynamic Solver
-------------------

.. graphviz::

    digraph {
        nodesep = 0.9;
        ratio=autor;
        newrank=true;
        node [
            peripheries="1",
            fillcolor="#FAAC2C"
            style="rounded, filled"
            color="#FAAC2C"
            fontcolor="#ffffff"
            shape="rectangular"
        ];
        edge [ color="#8699A3" fontcolor="#2c3e50" ];

        hydrodynamic_1 [label="Primary Variables \n (Solver Unknowns)"];
        hydrodynamic_2 [label="Calculate \n State Variables"];

        hydrodynamic_3 [label="Calculate \n Secondary Variables"];
        hydrodynamic_4 [label="Calculate \n Source Terms"];


        // Align Notes
        subgraph cluster2{
            labeljust="l"
            style="rounded, dashed"
            fontcolor="#2c3e50"
            color="#8699A3"
            note_1 [label="α, P, U, T", shape=box, color="#FAAC2C",fillcolor="#FFFFFF", fontcolor="#FAAC2C"]
            note_2 [label="ρ, μ, Cₚ, ... = ƒ(P,T)", shape=box, color="#FAAC2C",fillcolor="#FFFFFF", fontcolor="#FAAC2C"]
            note_3 [label="Mass Flow Rate, Flow Pattern ...", shape=box, color="#FAAC2C",fillcolor="#FFFFFF", fontcolor="#FAAC2C"]
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

        hook_update_variables_point [shape = point, width = 0, peripheries="2"]
        hook_calculate_source_terms_point [shape = point, width = 0, peripheries="2" ]



        hook_update_variables [peripheries="0"
            label="HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES", shape="cds", color="#DA5961", fontcolor="#DA5961", style=""
            URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.update_plugins_secondary_variables", target="_top"
        ]
        subgraph a{
            rankdir=LR;
        //nodesep=0.1;
        //mindist=0.1;
        hook_calculate_mass_source_terms [peripheries="0"
            label="HOOK_CALCULATE_MASS_SOURCE_TERM", shape="cds", color="#DA5961",  fontcolor="#DA5961" , style=""
            URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.calculate_mass_source_term", target="_top"
        ]
        hook_calculate_momentum_source_terms [peripheries="0"
            label="HOOK_CALCULATE_MOMENTUM_SOURCE_TERM", shape="cds", color="#DA5961",  fontcolor="#DA5961" , style=""
            URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.calculate_momentum_source_term", target="_top"
        ]
        hook_calculate_energy_source_terms [peripheries="0"
            label="HOOK_CALCULATE_ENERGY_SOURCE_TERM", shape="cds", color="#DA5961",  fontcolor="#DA5961" , style=""
            URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.calculate_energy_source_term", target="_top"
        ]
        }
        {rank = same; hook_update_variables_point; hook_update_variables        }
        {rank = same; hook_calculate_source_terms_point; hook_calculate_momentum_source_terms; }

        // Align all hooks
        hook_calculate_mass_source_terms -> hook_calculate_momentum_source_terms -> hook_calculate_energy_source_terms [constraint=true, style=invis]

        subgraph cluster1{
            labeljust="l"
            style="rounded, dashed"
            color="#8699A3"
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

.. _tracer_solver:

Tracer Solver
-------------

.. graphviz::

    digraph {
        //nodesep = 0.8
        newrank=true
        node [fillcolor="#FAAC2C" style="rounded, filled" color="#FAAC2C" fontcolor="#ffffff" shape="rectangular"]
        edge [ color="#8699A3" fontcolor="#2c3e50" ]

        tracer_1 [label="Primary Variables \n (Solver Unknowns, ϕ) "]
        tracer_2 [label="Calculate \n Secondary Variables"]
        tracer_3 [label="Calculate \n Source Terms"]

        invisible_init [shape=point, style=invis]
        invisible_end [shape=point, style=invis]

        node[shape = point, width = 0, peripheries="2" ]
        hook_initialize_user_defined_tracer_point
        hook_set_bc_user_defined_tracer_point
        hook_update_variables_point
        hook_calculate_source_terms_point

        node[peripheries="0" shape="cds", color="#DA5961",  fontcolor="#DA5961" , style="" target="_top"]
        hook_initialize_user_defined_tracer [label="HOOK_INITIALIZE_MASS_FRACTION_OF_TRACER" URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.calculate_tracer_source_term"]
        hook_set_bc_user_defined_tracer [label="HOOK_SET_PRESCRIBED_BOUNDARY_CONDITION_OF_MASS_FRACTION_OF_TRACER", URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.calculate_tracer_source_term"]
        hook_update_variables [label="HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES_ON_TRACER_SOLVER", URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.update_plugins_secondary_variables"]
        hook_calculate_tracer_source_terms [label="HOOK_CALCULATE_TRACER_SOURCE_TERM" URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.calculate_tracer_source_term"]
        hook_update_bc_user_defined_tracer [label="HOOK_UPDATE_BOUNDARY_CONDITION_OF_MASS_FRACTION_OF_TRACER" URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.update_boundary_condition_of_mass_fraction_of_tracer"]
        hook_calculate_mass_fraction_of_tracer_in_field [label="HOOK_CALCULATE_MASS_FRACTION_OF_TRACER_IN_FIELD \n HOOK_CALCULATE_MASS_FRACTION_OF_TRACER_IN_PHASE" URL="../06_solver_hooks.html#alfasim_sdk.hook_specs.calculate_mass_fraction_of_tracer_in_phase" ]

        {rank = same   hook_update_variables_point   hook_update_variables}
        {rank = same   hook_calculate_source_terms_point   hook_calculate_tracer_source_terms   }
        {rank = same   hook_initialize_user_defined_tracer_point   hook_initialize_user_defined_tracer   }
        {rank = same   hook_set_bc_user_defined_tracer_point   hook_set_bc_user_defined_tracer   }
        {rank = same   tracer_1   hook_update_bc_user_defined_tracer   }
        {rank = same   tracer_2   hook_calculate_mass_fraction_of_tracer_in_field}

        // Main Flow
        invisible_init -> hook_initialize_user_defined_tracer_point [arrowhead=none]
        hook_calculate_source_terms_point -> invisible_end

        subgraph cluster1{
            labeljust="l"
            style="rounded, dashed"
            color="#8699A3"

            hook_initialize_user_defined_tracer_point -> hook_set_bc_user_defined_tracer_point [arrowhead=none]
            hook_set_bc_user_defined_tracer_point-> tracer_1
            tracer_1 -> tracer_2
            tracer_2 -> hook_update_variables_point [arrowhead=none]
            hook_update_variables_point -> tracer_3
            tracer_3 -> hook_calculate_source_terms_point [arrowhead=none]
        }

        edge[constraint=false, style=dotted, color="#DA5961"]

        subgraph cluster2{
            label="Hooks for User Defined Tracers"
            labeljust="l"
            fontcolor="#2c3e50"
            style="rounded, dashed"
            color="#8699A3"

            hook_initialize_user_defined_tracer_point -> hook_initialize_user_defined_tracer
            hook_set_bc_user_defined_tracer_point -> hook_set_bc_user_defined_tracer
            tracer_1 -> hook_update_bc_user_defined_tracer
            tracer_2 -> hook_calculate_mass_fraction_of_tracer_in_field
        }

        hook_calculate_source_terms_point -> hook_calculate_tracer_source_terms
        hook_update_variables_point -> hook_update_variables

    }
