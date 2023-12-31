#include "headers.h"

#include "display.h"
#include "constants.h"
#include "util.h"

void HandleClear(AsyncWebServerRequest *request) {
    int x = 0, y = 0, w = 0, h = 0;
    if (request->hasParam("x")) {
        x = request->getParam("x")->value().toInt();
    }
    if (request->hasParam("y")) {
        y = request->getParam("y")->value().toInt();
    }
    if (request->hasParam("w")) {
        w = request->getParam("w")->value().toInt();
    } else {
        w = display->width();
    }
    if (request->hasParam("h")) {
        h = request->getParam("h")->value().toInt();
    } else {
        w = display->height();
    }
    if (x < 0 || y < 0 || w < 0 || h < 0 || x >= display->width() || y >= display->height()) {
        request->send(400, "text/plain", "input args out of range");
        return;
    }
    display->fillRect(x, y, w, h, BLACK);
    request->send(200, "text/plain", "ok");
}

void HandleText(AsyncWebServerRequest *request) {
    if (!request->hasParam("text")) {
        request->send(404, "text/plain", "text param missing");
        return;
    }
    const std::string text = request->getParam("text")->value().c_str();

    int x = 0, y = 0, r = 0, g = 0, b = 0;
    if (request->hasParam("x")) {
        x = request->getParam("x")->value().toInt();
    }
    if (request->hasParam("y")) {
        y = request->getParam("y")->value().toInt();
    }
    if (request->hasParam("r")) {
        r = request->getParam("r")->value().toInt();
    }
    if (request->hasParam("g")) {
        g = request->getParam("g")->value().toInt();
    }
    if (request->hasParam("b")) {
        b = request->getParam("b")->value().toInt();
    }
    if (x < 0 || y < 0 || x >= display->width() || y >= display->height()) {
        request->send(400, "text/plain", "input args out of range");
        return;
    }

    uint16_t color = display->color565(r, g, b);
    if (color == BLACK) color = WHITE;

    TextOut(x, y, text, color);

    request->send(200, "text/plain", "ok");
}

void HandleDot(AsyncWebServerRequest *request) {
    int x = 0, y = 0, r = 0, g = 0, b = 0;
    if (request->hasParam("x")) {
        x = request->getParam("x")->value().toInt();
    }
    if (request->hasParam("y")) {
        y = request->getParam("y")->value().toInt();
    }
    if (request->hasParam("r")) {
        r = request->getParam("r")->value().toInt();
    }
    if (request->hasParam("g")) {
        g = request->getParam("g")->value().toInt();
    }
    if (request->hasParam("b")) {
        b = request->getParam("b")->value().toInt();
    }
    if (x < 0 || y < 0 || x >= display->width() || y >= display->height()) {
        request->send(400, "text/plain", "input args out of range");
        return;
    }

    const uint16_t color = display->color565(r, g, b);
    display->drawPixel(x, y, color);

    request->send(200, "text/plain", "ok");
}

void HandleBitmap(AsyncWebServerRequest *request, uint8_t *data, size_t len,
        size_t index, size_t total) {
    Serial.printf("Body handler: %d %d %d\n\r", len, index, total);
    int x = 0, y = 0, w = 0, h = 0;
    if (request->hasParam("x")) {
        x = request->getParam("x")->value().toInt();
    }
    if (request->hasParam("y")) {
        y = request->getParam("y")->value().toInt();
    }
    if (request->hasParam("w")) {
        w = request->getParam("w")->value().toInt();
    } else {
        w = display->width();
    }
    if (request->hasParam("h")) {
        h = request->getParam("h")->value().toInt();
    } else {
        w = display->height();
    }
    if (x < 0 || y < 0 || w < 0 || h < 0 || x >= display->width() || y >= display->height()) {
        if (index == 0) {
            request->send(400, "text/plain", "input args out of range");
        }
        return;
    }

    if (total < w * h * 2) {
        if (index == 0) {
            request->send(400, "text/plain", String("body too short: ") + String(len));
        }
        return;
    }

    if (request->_tempObject == nullptr) {
        request->_tempObject = malloc(total);
    }

    char* buf = (char*)request->_tempObject;
    for (int i = 0; i < len; ++i) {
        buf[i + index] = data[i];
    }

    if (len + index == total) {
        for (int dy = 0; dy < h; ++dy) {
            for (int dx = 0; dx < w; ++dx) {
                const int offset = (dy * w + dx) * 2;
                const uint16_t pixel = buf[offset] << 8 | buf[offset + 1];
                display->drawPixel(x + dx, y + dy, pixel);
            }
        }

        request->send(200, "text/plain", "ok");
    }
}

void SetupServer(AsyncWebServer& server) {
    server.on("/text", HTTP_ANY, HandleText);
    server.on("/clear", HTTP_ANY, HandleClear);
    server.on("/dot", HTTP_ANY, HandleDot);
    server.on("/bitmap", HTTP_POST, [](AsyncWebServerRequest * request){
            request->send(400, "text/plain", "incorrect request content type");
            }, nullptr, HandleBitmap);

    server.begin();
}
