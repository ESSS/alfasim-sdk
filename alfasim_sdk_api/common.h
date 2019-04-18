enum error_code
{
    OUT_OF_BOUNDS=-6,
    UNKNOWN_CONTEXT=-5,
    NOT_AVAILABLE_DATA=-4,
    BUFFER_SIZE_INSUFFICIENT=-3,
    UNDEFINED_DATA=-2,
    NOT_IMPLEMENTED=-1,
    OK = 0
};

enum GridScope
{
    CENTER=0,
    FACE=1
};

enum MultiFieldDescriptionScope
{
    MIXTURE=0,
    GLOBAL=0,
    FIELD=1,
    LAYER=2,
    PHASE=3
};

enum TimestepScope
{
    CURRENT=0,
    PREVIOUS=1
};

struct VariableScope
{
    enum GridScope grid_scope;
    enum MultiFieldDescriptionScope mfd_scope;
    enum TimestepScope ts_scope;
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
