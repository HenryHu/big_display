#include "headers.h"

#include "main.h"
#include "display.h"

void TextOut(const int x, const int y, const std::string& text, const uint64_t color = WHITE) {
    display->fillRect(x, y, 6 * text.length(), 8, BLACK);
    display->setCursor(x, y);
    display->setTextColor(color);
    display->print(text.c_str());
}

void PrintStatus(const std::string& status) {
    display->fillRect(0, 56, display->width(), 8, BLACK);
    TextOut(0, 56, status);
}
