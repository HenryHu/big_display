#include <string>

#define ARDUINO_HTTP_SERVER_NO_BASIC_AUTH
#include <ArduinoHttpServer.h>

std::string HandleClear(const ArduinoHttpServer::HttpResource& resource);
std::string HandleText(const ArduinoHttpServer::HttpResource& resource);
std::string HandleDot(const ArduinoHttpServer::HttpResource& resource);
std::string HandleBitmap(const ArduinoHttpServer::HttpResource& resource, const char* body, const int length);
