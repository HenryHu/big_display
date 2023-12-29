#include "display.h"

#define R1_PIN 27
#define G1_PIN 26
#define B1_PIN 25
#define R2_PIN 33
#define G2_PIN -1
#define B2_PIN -1
#define A_PIN 12
#define B_PIN 13
#define C_PIN 15
#define D_PIN 2
#define E_PIN 32 // required for 1/32 scan panels, like 64x64px. Any available pin would do, i.e. IO32
#define CLK_PIN 17
#define LAT_PIN 22
#define OE_PIN 21

MatrixPanel_I2S_DMA* GetDisplay() {
    HUB75_I2S_CFG::i2s_pins _pins={R1_PIN, G1_PIN, B1_PIN, R2_PIN, G2_PIN, B2_PIN, A_PIN, B_PIN, C_PIN, D_PIN, E_PIN, LAT_PIN, OE_PIN, CLK_PIN};
    HUB75_I2S_CFG mxconfig(
            64, // Module width
            64, // Module height
            1, // chain length
            _pins // pin mapping
            );
    return new MatrixPanel_I2S_DMA(mxconfig);
}
