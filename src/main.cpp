#include <Arduino.h>

#include <string>
#include <memory>

#define ARDUINO_HTTP_SERVER_NO_BASIC_AUTH

#include <ESP32-HUB75-MatrixPanel-I2S-DMA.h>
#include <InterruptButton.h>
#include <ArduinoHttpServer.h>
#include <WiFi.h>

#include "constants.h"
#include "util.h"
#include "cmds.h"
#include "display.h"

MatrixPanel_I2S_DMA *display = nullptr;

using HttpRequest = ArduinoHttpServer::StreamHttpRequest<16384>;
using HttpReply = ArduinoHttpServer::StreamHttpReply;

const uint16_t BLACK = MatrixPanel_I2S_DMA::color565(0, 0, 0);
const uint16_t WHITE = MatrixPanel_I2S_DMA::color565(255, 255, 255);
const uint16_t RED = MatrixPanel_I2S_DMA::color565(255, 0, 0);
const uint16_t GREEN = MatrixPanel_I2S_DMA::color565(0, 255, 0);
const uint16_t BLUE = MatrixPanel_I2S_DMA::color565(0, 0, 255);

InterruptButton button0(0, LOW);
InterruptButton button1(35, LOW);

WiFiServer server(SERVER_PORT);

int brightness = 31;

void InitDisplay() {
    display = GetDisplay();
    display->begin();
    display->clearScreen();
    display->fillScreen(display->color565(0, 0, 0));
    display->setBrightness8(brightness);
    display->setTextWrap(false); // Don't wrap at end of line - will do ourselves
}

void InitWifi() {
    PrintStatus(WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        PrintStatus("Connecting");
    }
    PrintStatus(std::string("IP: ") + WiFi.localIP().toString().substring(8).c_str());
    delay(500);

    server.begin();
}

void button1_press() {
    brightness = (brightness + 16) % 256;
    display->setBrightness8(brightness);
}

void button0_press() {
}

void setup() {
    Serial.begin(115200);

    InitDisplay();
    InitWifi();
    button0.bind(Event_KeyPress, &button0_press);
    button1.bind(Event_KeyPress, &button1_press);
}

std::string HandleGet(const HttpRequest& request) {
    const ArduinoHttpServer::HttpResource& resource = request.getResource();
    const auto cmd = resource[0];
    if (cmd == "text") {
        return HandleText(resource);
    } else if (cmd == "dot") {
        return HandleDot(resource);
    } else if (cmd == "clear") {
        return HandleClear(resource);
    }
    return "unknown function";
}

std::string HandlePost(const HttpRequest& request) {
    const ArduinoHttpServer::HttpResource& resource = request.getResource();
    if (resource[0] == "bitmap") {
        return HandleBitmap(resource, request.getBody(), request.getContentLength());
    }

    return "unknown function";
}

void HandleClient(WiFiClient& client) {
    std::unique_ptr<HttpRequest> request(new HttpRequest(client));
    const bool success = request->readRequest();
    if (!success) return;

    const ArduinoHttpServer::Method method = request->getMethod();

    std::string status = "unknown method";
    if (method == ArduinoHttpServer::Method::Get) {
        status = HandleGet(*request);
    } else if (method == ArduinoHttpServer::Method::Post) {
        status = HandlePost(*request);
    }

    if (status == "ok") {
        HttpReply reply(client, "text/plain");
        reply.send(status.c_str());
    } else {
        ArduinoHttpServer::StreamHttpErrorReply reply(client, "text/plain", "500");
        reply.send(status.c_str());
    }
}

void loop() {
    WiFiClient client = server.available();

    if (client) {
        HandleClient(client);
        client.stop();
    }
    delay(20);
}

