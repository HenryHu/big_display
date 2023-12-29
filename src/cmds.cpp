#include <string>

#include "main.h"
#include "util.h"
#include "cmds.h"

std::string HandleClear(const ArduinoHttpServer::HttpResource& resource) {
    const String x_str = resource[1];
    const String y_str = resource[2];
    const String w_str = resource[3];
    const String h_str = resource[4];

    int w = w_str.toInt();
    int h = h_str.toInt();
    if (w == 0) w = display->width();
    if (h == 0) w = display->height();
    display->fillRect(x_str.toInt(), y_str.toInt(), w, h, BLACK);
    return "ok";
}

std::string HandleText(const ArduinoHttpServer::HttpResource& resource) {
    const String x_str = resource[1];
    const String y_str = resource[2];
    const String text = resource[3];

    const String r_str = resource[4];
    const String g_str = resource[5];
    const String b_str = resource[6];
    uint16_t color = display->color565(r_str.toInt(), g_str.toInt(), b_str.toInt());
    if (color == BLACK) color = WHITE;

    TextOut(x_str.toInt(), y_str.toInt(), text.c_str(), color);

    return "ok";
}

std::string HandleDot(const ArduinoHttpServer::HttpResource& resource) {
    const String x_str = resource[1];
    const String y_str = resource[2];

    const String r_str = resource[3];
    const String g_str = resource[4];
    const String b_str = resource[5];
    uint16_t color = display->color565(r_str.toInt(), g_str.toInt(), b_str.toInt());
    display->drawPixel(x_str.toInt(), y_str.toInt(), color);

    return "ok";
}

std::string HandleBitmap(const ArduinoHttpServer::HttpResource& resource, const char* body, const int length) {
    const String x_str = resource[1];
    const String y_str = resource[2];
    const String w_str = resource[3];
    const String h_str = resource[4];

    const int w = w_str.toInt();
    const int h = h_str.toInt();

    if (length < w * h * 2) return std::string("body too short: ") + String(length).c_str();

    std::vector<int> *bitmap = new std::vector<int>();
    bitmap->reserve(w * h);
    for (int x = 0; x < w; ++x) {
        for (int y = 0; y < h; ++y) {
            const int offset = (x * h + y) * 2;
            bitmap->push_back(body[offset] << 8 | body[offset + 1]);
        }
    }

    display->drawIcon(bitmap->data(), x_str.toInt(), y_str.toInt(), w, h);
    delete bitmap;

    return "ok";
}
