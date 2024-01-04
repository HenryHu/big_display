#!/usr/bin/env python3
"""Updater to keep updating the big display."""
# pylint: disable=broad-except,too-many-locals

import sys
import time
import datetime

import requests
import local_config
from PIL import Image

import align
import sensor
import widget
import weather


def main():
    sensor_data = sensor.SensorData()
    sensor_data.restore()
    _mqtt_client = sensor.SensorMqttClient(local_config.MQTT_SERVER, local_config.MQTT_USER,
                                           local_config.MQTT_PASS, local_config.MQTT_TOPIC,
                                           sensor_data)

    requests.get(f"{local_config.DISPLAY_URL}/clear",
                 timeout=local_config.DISPLAY_TIMEOUT)
    background = widget.ImageWidget(0, 0)
    background.update(Image.open(sys.argv[1]))

    date_widget = widget.TextWithDotWidget(1, 0, widget.ColorPicker())
    wday_widget = widget.TextWidget(0, 56)

    hour_widget = widget.TextWidget(38, 0)
    time_dot1_widget = widget.DotWidget(50, 3)
    time_dot2_widget = widget.DotWidget(50, 5)
    min_widget = widget.TextWidget(52, 0)

    tic_widget = widget.TextWidget(48, 56)
    sec_widget = widget.TextWidget(52, 56)

    temp_color_picker = widget.RangedColorPicker({
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
    temp_widget = widget.TextWithDotWidget(1, 8, temp_color_picker)
    humid_widget = widget.TextWithDotWidget(38, 8, widget.RangedColorPicker({
        10: (255, 0, 0),
        20: (0, 255, 255),
        70: (0, 255, 0),
        90: (255, 255, 0),
        100: (0, 0, 255),
    }))

    ext_temp_color_picker = widget.RangedColorPicker({
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
    last_weather_update = None
    weather_icon_widget = widget.ImageWidget(46, 36, 18, 24, align.HAlign.TOP)
    ext_temp_widget = widget.ColoredTextWidget(0, 9, ext_temp_color_picker)
    weather_icon_widget.add_child(ext_temp_widget)

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

        if sensor_data.temp is not None:
            temp_widget.update(sensor_data.temp_str(), sensor_data.temp)
        if sensor_data.humid is not None:
            humid_widget.update(sensor_data.humid_str(), sensor_data.humid)

        if (last_weather_update is None or
            now - last_weather_update > datetime.timedelta(minutes=5)):
            weather.update_weather(ext_temp_widget, weather_icon_widget)
            last_weather_update = now

        time.sleep(0.1)

if __name__ == "__main__":
    main()
