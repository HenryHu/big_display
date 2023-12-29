#include <Arduino.h>

#include <ESP32-HUB75-MatrixPanel-I2S-DMA.h>
#include <InterruptButton.h>

#include "constants.h"

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

MatrixPanel_I2S_DMA *display = nullptr;

uint16_t myBLACK = display->color565(0, 0, 0);
uint16_t myWHITE = display->color565(255, 255, 255);
uint16_t myRED = display->color565(255, 0, 0);
uint16_t myGREEN = display->color565(0, 255, 0);
uint16_t myBLUE = display->color565(0, 0, 255);

InterruptButton button0(0, LOW);
InterruptButton button1(35, LOW);

int brightness = 1;

void button1_press() {
    brightness = (brightness + 16) % 256;
    display->setBrightness8(brightness);
}

void button0_press() {
}

void setup() {

    Serial.begin(115200);

    HUB75_I2S_CFG::i2s_pins _pins={R1_PIN, G1_PIN, B1_PIN, R2_PIN, G2_PIN, B2_PIN, A_PIN, B_PIN, C_PIN, D_PIN, E_PIN, LAT_PIN, OE_PIN, CLK_PIN};
    HUB75_I2S_CFG mxconfig(
            64, // Module width
            64, // Module height
            1, // chain length
            _pins // pin mapping
            );
    display = new MatrixPanel_I2S_DMA(mxconfig);
    display->begin();
    display->clearScreen();
    display->fillScreen(display->color565(0, 0, 0));
    display->setBrightness8(31);
    display->setTextWrap(false); // Don't wrap at end of line - will do ourselves

    display->println("HelloWorld!");

    button0.bind(Event_KeyPress, &button0_press);
    button1.bind(Event_KeyPress, &button1_press);
}

void loop() {
    button0.processSyncEvents();
    button1.processSyncEvents();

    delay(20);
}

