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
    WiFi.onEvent([](WiFiEvent_t event, WiFiEventInfo_t info){
            Serial.printf("WiFi disconnected, reconnect, reason: %d\r\n",
                          info.wifi_sta_disconnected.reason);
            WiFi.begin(WIFI_SSID, WIFI_PASS);
            },
            WiFiEvent_t::ARDUINO_EVENT_WIFI_STA_DISCONNECTED);
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

void loop() {
    Serial.printf("Free mem: %d\r\n", esp_get_free_heap_size());
    delay(5000);
}
