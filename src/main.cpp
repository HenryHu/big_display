#include <Arduino.h>

#include "headers.h"

#include "constants.h"
#include "main.h"
#include "util.h"
#include "cmds.h"
#include "display.h"

const uint16_t BLACK = MatrixPanel_I2S_DMA::color565(0, 0, 0);
const uint16_t WHITE = MatrixPanel_I2S_DMA::color565(255, 255, 255);
const uint16_t RED = MatrixPanel_I2S_DMA::color565(255, 0, 0);
const uint16_t GREEN = MatrixPanel_I2S_DMA::color565(0, 255, 0);
const uint16_t BLUE = MatrixPanel_I2S_DMA::color565(0, 0, 255);

AsyncWebServer server(SERVER_PORT);

void InitWifi() {
    PrintStatus(WIFI_SSID);
    WiFi.setHostname(HOSTNAME);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        PrintStatus("Connecting");
    }
    PrintStatus(std::string("IP: ") + WiFi.localIP().toString().substring(8).c_str());
}

void setup() {
    Serial.begin(115200);

    InitDisplay();
    InitWifi();
    SetupServer(server);
}

void loop() {}
