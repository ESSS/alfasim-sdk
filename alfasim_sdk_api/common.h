enum error_code
{
    OUT_OF_BOUNDS=-6,
    UNKNOWN_CONTEXT=-5,
    NOT_AVAILABLE_DATA=-4,
    BUFFER_SIZE_INSUFFICIENT=-3,
    UNDEFINED_DATA=-2,
    NOT_IMPLEMENTED=-1,
    OK = 0,
};

#define FIELD_GAS "gas"
#define FIELD_LIQUID "liquid"
#define FIELD_WATER "water"
#define FIELD_DROPLET "droplet"
#define FIELD_BUBBLE "bubble"

#define PHASE_GAS "gas"
#define PHASE_LIQUID "liquid"
#define PHASE_WATER "water"

#define LAYER_GAS "gas"
#define LAYER_LIQUID "liquid"
#define LAYER_WATER "water"

#define TIMESTEP_CURRENT 0
#define TIMESTEP_OLD 1
