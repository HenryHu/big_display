#include <Arduino.h>

#include "headers.h"

#include "config.h"
#include "util.h"
#include "cmds.h"
#include "display.h"

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
