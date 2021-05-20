#ifndef _H_ASIM_SDK_COMMON
#define _H_ASIM_SDK_COMMON

/*! @file */

/*!
    It holds the possible returning error code from ALFAsim-SDK-API functions.
*/
enum error_code
{
    REFERENCE_NOT_SET=-8, /*!< Some reference from input data wasn't set.*/
    UNKNOWN_REFERENCE_TYPE=-7, /*!< Reference type is unknown.*/
    OUT_OF_BOUNDS=-6, /*!< Index out of array bounds.*/
    UNKNOWN_CONTEXT=-5, /*!< The context is unknown.*/
    NOT_AVAILABLE_DATA=-4, /*!< Data from ALFAsim is not available.*/
    BUFFER_SIZE_INSUFFICIENT=-3, /*!< Buffer size is insufficient.*/
    UNDEFINED_DATA=-2, /*!< Plugin internal data is undefined.*/
    NOT_IMPLEMENTED=-1, /*!< A feature is not implemented in an API function.*/
    OK = 0 /*!< Everything was fine.*/
};

/*!
    It holds the variable scope in the grid to retrieve a simulation array.
*/
enum GridScope
{
    CENTER=0, /*!< Variable located in the control volume center*/
    FACE=1 /*!< Variable located in the control volume face*/
};

/*!
    It holds the variable scope in the Multifield description (phases/fields/layers)
    to retrieve a simulation array.
*/
enum MultiFieldDescriptionScope
{
    MIXTURE=0, /*!< Variable associated to the mixture*/
    GLOBAL=0, /*!< Global variable*/
    FIELD=1, /*!< Variable associated to the field*/
    LAYER=2, /*!< Variable associated to the layer*/
    PHASE=3 /*!< Variable associated to the phase*/
};

/*!
    It holds the two phase system ids for Unit Cell Model related API functions.
*/
enum TwoPhaseSystem {
    GAS=0, /*!< Gas phase.*/
    LIQUID=1, /*!< Liquid phase (sum of all phases).*/
};

/*!
    It holds the liquid-liquid system ids for Liquid-Liquid related API functions.
*/
enum LiquidLiquidSystem {
    OIL=0, /*!< Oil phase.*/
    WATER=1, /*!< Water phase.*/
};

/*!
    It holds the variable scope in the time level to retrieve a simulation array.
*/
enum TimestepScope
{
    CURRENT=0, /*!< Variable in the current time step*/
    PREVIOUS=1 /*!< Variable in the previous (old) time step*/
};


/*!
    It holds the possible state variables that can be computed to a phase inside the plugin.
    See solver hooks ``calculate_state_variable`` and ``calculate_phase_pair_state_variable``
*/
enum StateVariable {
    RHO, /*!< Density*/
    MU, /*!< Viscosity*/
    CP, /*!< Heat Capacity*/
    DRHO_DP, /*!< Partial derivative of density in relation to pressure*/
    DRHO_DT, /*!< Partial derivative of density in relation to temperature*/
    H, /*!< Enthalpy*/
    K, /*!< Thermal Conductivity*/
    SIGMA, /*!< Interfacial tension*/
    RS, /*!< gas mass fraction w.r.t. to hydrocarbon system*/
    RSW /*!< vapor mass fraction w.r.t. to gas system*/
};

/*!
    It holds all variable scopes (grid, multifield and timestep)
*/
struct VariableScope
{
    /*!
        Which grid scope of the variable
    */
    enum GridScope grid_scope;
    /*!
        Which multifield scope of the variable
    */
    enum MultiFieldDescriptionScope mfd_scope;
    /*!
        Which timestep scope of the variable
    */
    enum TimestepScope ts_scope;
};

/*!
    It holds the possible returning error code when trying to open ALFAsim-SDK API.
*/
enum sdk_load_error_code {
    SDK_DLL_PATH_TOO_LONG=-2, /*!< Path to SDK dll too long (Windows limitation).*/
    SDK_ALREADY_OPEN_ERROR=-1, /*!< SDK dll already Opened.*/
    SDK_OK=0 /*!< Everything was fine.*/
};

#ifndef DOXYGEN_SHOULD_SKIP_THIS

#define FIELD_GAS "gas"
#define FIELD_OIL "oil"
#define FIELD_WATER "water"
#define FIELD_WATER_DROPLET_IN_OIL "water in oil"
#define FIELD_DROPLET "droplet"
#define FIELD_BUBBLE "bubble"

#define PHASE_GAS "gas"
#define PHASE_OIL "oil"
#define PHASE_WATER "water"

#define LAYER_GAS "gas"
#define LAYER_OIL "oil"
#define LAYER_WATER "water"

#endif // DOXYGEN_SHOULD_SKIP_THIS

#endif
