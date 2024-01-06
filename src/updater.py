#!/usr/bin/env python3
"""Updater to keep updating the big display."""
# pylint: disable=too-many-instance-attributes,too-few-public-methods

import time
import datetime
import random

import local_config
from PIL import Image

import align
import sensor
import widget
import weather
import display

class Gui:
    def __init__(self):
        self.background = widget.ImageWidget(0, 0)

        self.date_widget = widget.TextWithDotWidget(1, 0, widget.ColorPicker())
        self.wday_widget = widget.TextWidget(0, 56)

        self.hour_widget = widget.TextWidget(38, 0)
        self.time_dot1_widget = widget.DotWidget(50, 3)
        self.time_dot2_widget = widget.DotWidget(50, 5)
        self.min_widget = widget.TextWidget(52, 0)

        self.tic_widget = widget.TextWidget(48, 56)
        self.sec_widget = widget.TextWidget(52, 56)

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
        self.temp_widget = widget.TextWithDotWidget(1, 8, temp_color_picker)
        self.humid_widget = widget.TextWithDotWidget(38, 8, widget.RangedColorPicker({
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
        self.weather_icon_widget = widget.ImageWidget(46, 28, 18, 28, align.HAlign.TOP)
        self.ext_temp_widget = widget.ColoredTextWidget(0, 16, ext_temp_color_picker)
        self.weather_icon_widget.add_child(self.ext_temp_widget)

    def repaint(self):
        self.date_widget.repaint()
        self.wday_widget.repaint()

        self.hour_widget.repaint()
        self.time_dot1_widget.repaint()
        self.time_dot2_widget.repaint()
        self.min_widget.repaint()

        self.tic_widget.repaint()
        self.sec_widget.repaint()

        self.temp_widget.repaint()
        self.humid_widget.repaint()

        self.weather_icon_widget.repaint()
        self.ext_temp_widget.repaint()

def pick_background():
    return Image.open(random.choice(local_config.BACKGROUND_IMAGES))

def main():
    sensor_data = sensor.SensorData()
    sensor_data.restore()
    _mqtt_client = sensor.SensorMqttClient(local_config.MQTT_SERVER, local_config.MQTT_USER,
                                           local_config.MQTT_PASS, local_config.MQTT_TOPIC,
                                           sensor_data)

    display.clear()
    gui = Gui()

    background_update_time = None

    weather_tracker = weather.WeatherTracker()

    while True:
        now = datetime.datetime.now()

        if (background_update_time is None or
            now - background_update_time > local_config.BACKGROUND_CYCLE_TIME):
            gui.background.update(pick_background())
            gui.repaint()
            background_update_time = now

        gui.date_widget.update(now.strftime("%m.%d"), 0)
        gui.wday_widget.update(now.strftime("%a"))

        gui.hour_widget.update(now.strftime("%H"))
        gui.time_dot1_widget.update()
        gui.time_dot2_widget.update()
        gui.min_widget.update(now.strftime("%M"))

        gui.tic_widget.update(":")
        gui.sec_widget.update(now.strftime("%S"))

        if sensor_data.temp is not None:
            gui.temp_widget.update(sensor_data.temp_str(), sensor_data.temp)
        if sensor_data.humid is not None:
            gui.humid_widget.update(sensor_data.humid_str(), sensor_data.humid)

        weather_tracker.update_weather(gui.ext_temp_widget, gui.weather_icon_widget)

        time.sleep(0.1)

if __name__ == "__main__":
    main()
