=======
History
=======

0.7.0 (2020-11-20)
==================

* Add support for alfacase.
* Released with ALFAsim 1.8.0.


0.6.1 (2020-10-30)
==================

* Internal release only.


0.6.0 (2020-10-29
=================

* Invalid release due to packaging error.

0.5.0
======

* Remove api functions `get_wall_layer_id` and `set_wall_layer_property`.
* Add `thickness`, `density`, `heat_capacity`, `thermal_conductivity` parameters on `update_internal_deposition_layer`

0.4.0
======

* Add new API functions related unit cell model friction factor hooks.

* Add two new hooks to calculate the unit cell model friction factor for stratified and annular flows.

0.3.0
======

* Adopt terminology gas-oil-water

* Add a new hook to evaluate the thickness of the deposited layer at the inside of the pipeline walls and it accounts for the diameter reduction.

* Rename HydrodynamicModelType items from snake_case to CamelCase, a backward compatibility option is kept.

0.2.0
======

* Add "required-alfasim-sdk" key on plugin.yaml to identify the required version of alfasim-sdk.

0.1.0
======

* First release.
