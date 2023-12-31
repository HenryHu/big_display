#!/usr/bin/env python3
"""Updater to keep updating the big display."""
# pylint: disable=too-few-public-methods,broad-except,too-many-arguments,too-many-locals

import sys
import time
import json
import io
import datetime
import logging

import requests
import local_config
import imagelib
import paho.mqtt.client as mqtt
from PIL import Image

WHITE_COLOR = (255, 255, 255)

class SensorData:
    temp = None
    humid = None

    def temp_str(self):
        return f"{self.temp:.1f}C"

    def humid_str(self):
        return f"{self.humid:.1f}%"

class DotWidget:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, r=255, g=255, b=255):
        try:
            r = requests.post(
                f"{local_config.DISPLAY_URL}/dot?x={self.x}&y={self.y}&r={r}&g={g}&b={b}",
                timeout=local_config.DISPLAY_TIMEOUT)
            r.close()
        except Exception:
            logging.exception("error drawing dot")

class ImageWidget:
    x = 0
    y = 0
    w = 0
    h = 0
    filename = None

    def __init__(self, x, y, w=local_config.WIDTH, h=local_config.HEIGHT):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def image(self, data):
        try:
            r = requests.post(
                f"{local_config.DISPLAY_URL}/bitmap?x={self.x}&y={self.y}&w={self.w}&h={self.h}",
                data=data, timeout=local_config.DISPLAY_TIMEOUT)
            if r.content != b'ok':
                logging.error("fail to set image: %r", r.content)
            r.close()
        except Exception:
            logging.exception("error drawing image")

    def update(self, img):
        data = imagelib.img_to_565(img, self.w, self.h)
        self.image(data)

class TextWidget:
    x = 0
    y = 0
    text = ''

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def text_out(self, x, y, text, r=255, g=255, b=255):
        try:
            r = requests.get(
                f"{local_config.DISPLAY_URL}/text?x={x}&y={y}&text={text}&r={r}&g={g}&b={b}",
                timeout=1)
            r.close()
        except Exception:
            logging.exception("error drawing text")

    def update(self, text, r=255, g=255, b=255):
        if text != self.text:
            if self.text and len(text) != len(self.text):
                self.text_out(self.x, self.y, ' ' * len(self.text))
            self.text_out(self.x, self.y, text, r, g, b)
            self.text = text

class ColorPicker:
    def pick(self, _value):
        return WHITE_COLOR

    def current_color(self):
        return WHITE_COLOR

class RangedColorPicker(ColorPicker):
    color_map = None
    current_color = None
    def __init__(self, color_map):
        self.color_map = color_map
        self.current_color = (255, 255, 255)

    def pick(self, value):
        for entry in sorted(self.color_map):
            if value < entry:
                color = self.color_map[entry]
                self.current_color = color
                return color
        return None

class ColoredTextWidget:
    text_widget = None
    picker = None
    def __init__(self, x, y, picker):
        self.text_widget = TextWidget(x, y)
        self.picker = picker

    def update(self, text, value):
        color = self.picker.pick(value)
        if color is not None:
            self.text_widget.update(text, *color)
        else:
            self.text_widget.update(text)

class TextWithDotWidget:
    first_part = None
    second_part = None
    dot_widget = None
    picker = None
    x = 0
    y = 0
    def __init__(self, x, y, picker):
        self.picker = picker
        self.x = x
        self.y = y

        self.first_part = TextWidget(x, y)
        self.dot_widget = DotWidget(x + 12, y + 6)
        self.second_part = TextWidget(x + 14, y)

    def update(self, text, value):
        color = self.picker.pick(value)
        if color is None:
            color = WHITE_COLOR

        if '.' in text:
            (first, second) = text.split('.', 1)
            self.first_part.update(first, *color)
            self.dot_widget.update(*color)
            self.second_part.update(second, *color)
        else:
            self.second_part.update('')
            self.first_part.update(text, *color)

class SensorMqttClient:
    client = None
    topic = None
    sensor_data = None

    def __init__(self, server, user, password, topic, sensor_data):
        self.topic = topic
        self.sensor_data = sensor_data

        self.client = mqtt.Client(client_id=local_config.MQTT_CLIENT_ID,
                                  clean_session=False)
        self.client.username_pw_set(user, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(server)
        self.client.loop_start()

    def on_connect(self, client, _userdata, _flags, rc):
        if rc != 0:
            logging.error("MQTT connect error! rc=%d", rc)
            return
        logging.info("MQTT connected.")
        client.subscribe(self.topic)

    def on_message(self, _client, _userdata, msg):
        payload = msg.payload.decode('utf-8')
        logging.info(msg.topic, payload.split('&'))
        for part in payload.split('&'):
            (key, value) = part.split('=')
            if key == 'TEMP':
                self.sensor_data.temp = float(value)
            if key == 'HUM':
                self.sensor_data.humid = float(value)

def update_weather(temp_widget, weather_icon_widget):
    try:
        req = requests.get(
            "http://api.weatherapi.com/v1/current.json?" +
            f"key={local_config.WEATHER_API_KEY}&q={local_config.WEATHER_ZIPCODE}&aqi=no",
            timeout=local_config.WEATHER_TIMEOUT)
        data_raw = req.content
        req.close()

        data = json.loads(data_raw)

        temp = data['current']['temp_c']
        temp_widget.update(f"{int(temp):2d}C", temp)

        icon_url = data['current']['condition']['icon']
        req = requests.get(f"http:{icon_url}", timeout=local_config.WEATHER_TIMEOUT)
        icon_raw = req.content
        req.close()

        icon_img = Image.open(io.BytesIO(icon_raw))

        weather_icon_widget.update(icon_img)

    except Exception:
        logging.exception("error updating weather")

def main():
    sensor = SensorData()
    _mqtt_client = SensorMqttClient(local_config.MQTT_SERVER, local_config.MQTT_USER,
                                    local_config.MQTT_PASS, local_config.MQTT_TOPIC,
                                    sensor)

    requests.get(f"{local_config.DISPLAY_URL}/clear",
                 timeout=local_config.DISPLAY_TIMEOUT)
    background = ImageWidget(0, 0)
    background.update(Image.open(sys.argv[1]))

    date_widget = TextWithDotWidget(1, 0, ColorPicker())
    wday_widget = TextWidget(0, 56)

    hour_widget = TextWidget(38, 0)
    time_dot1_widget = DotWidget(50, 3)
    time_dot2_widget = DotWidget(50, 5)
    min_widget = TextWidget(52, 0)

    tic_widget = TextWidget(48, 56)
    sec_widget = TextWidget(52, 56)

    temp_color_picker = RangedColorPicker({
        15: (3, 86, 252),
        18: (3, 194, 252),
        20: (3, 252, 232),
        23: (3, 252, 148),
        25: (3, 252, 57),
        27: (123, 252, 3),
        29: (248, 252, 3),
        31: (252, 182, 3),
        35: (252, 82, 3),
        40: (252, 15, 3),
    })
    temp_widget = TextWithDotWidget(1, 8, temp_color_picker)
    humid_widget = TextWithDotWidget(38, 8, RangedColorPicker({
        10: (255, 0, 0),
        20: (0, 255, 255),
        70: (0, 255, 0),
        90: (255, 255, 0),
        100: (0, 0, 255),
    }))

    ext_temp_color_picker = RangedColorPicker({
        0: (3, 152, 252),
        5: (3, 194, 252),
        10: (3, 252, 227),
        15: (3, 252, 169),
        20: (3, 252, 82),
        25: (123, 252, 3),
        27: (211, 252, 3),
        30: (252, 215, 3),
        35: (252, 123, 3),
        40: (252, 44, 3),
    })
    ext_temp_widget = ColoredTextWidget(46, 48, ext_temp_color_picker)
    last_weather_update = None
    weather_icon_widget = ImageWidget(48, 32, 16, 16)

    while True:
        now = datetime.datetime.now()

        date_widget.update(now.strftime("%m.%d"), 0)
        wday_widget.update(now.strftime("%a"))

        hour_widget.update(now.strftime("%H"))
        time_dot1_widget.update()
        time_dot2_widget.update()
        min_widget.update(now.strftime("%M"))

        tic_widget.update(":")
        sec_widget.update(now.strftime("%S"))

        if sensor.temp is not None:
            temp_widget.update(sensor.temp_str(), sensor.temp)
        if sensor.humid is not None:
            humid_widget.update(sensor.humid_str(), sensor.humid)

        if (last_weather_update is None or
            now - last_weather_update > datetime.timedelta(minutes=5)):
            update_weather(ext_temp_widget, weather_icon_widget)
            last_weather_update = now

        time.sleep(0.1)

if __name__ == "__main__":
    main()
