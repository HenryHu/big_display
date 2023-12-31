#include "display.h"

MatrixPanel_I2S_DMA *display = nullptr;
int brightness = 31;

/*
 * For ESP32 TTGO
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
*/

// For ESP32 Dev Board
#define R1_PIN 15
#define G1_PIN 2
#define B1_PIN 0
// GND
#define R2_PIN 4
#define G2_PIN 16
#define B2_PIN 17
#define E_PIN 5
#define A_PIN 18
#define B_PIN 19
#define C_PIN 14
#define D_PIN 27
#define CLK_PIN 26
#define LAT_PIN 25
#define OE_PIN 23
// GND

MatrixPanel_I2S_DMA* GetDisplay() {
    HUB75_I2S_CFG::i2s_pins _pins={R1_PIN, G1_PIN, B1_PIN, R2_PIN, G2_PIN,
        B2_PIN, A_PIN, B_PIN, C_PIN, D_PIN, E_PIN, LAT_PIN, OE_PIN, CLK_PIN};
    HUB75_I2S_CFG mxconfig(
            64, // Module width
            64, // Module height
            1, // chain length
            _pins // pin mapping
            );
    return new MatrixPanel_I2S_DMA(mxconfig);
}

void InitDisplay() {
    display = GetDisplay();
    display->begin();
    display->clearScreen();
    display->fillScreen(display->color565(0, 0, 0));
    display->setBrightness8(brightness);
    display->setTextWrap(false); // Don't wrap at end of line - will do ourselves
}
