"""Gets weather data"""
# pylint: disable=broad-except

import datetime
import json
import logging
import io
import os

import requests
from PIL import Image

import local_config

class WeatherTracker:
    weather_data_timestamp = None
    weather_data = None

    def __init__(self):
        (self.weather_data, self.weather_data_timestamp) = self.load_weather_from_cache()
        self.need_repaint = True

    def load_weather_from_cache(self):
        try:
            modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(local_config.WEATHER_PERSIST_PATH))
            with open(local_config.WEATHER_PERSIST_PATH, encoding='utf-8') as cachef:
                return (json.loads(cachef.read()), modified)
        except Exception:
            return None

    def fetch_weather(self):
        try:
            req = requests.get(
                "http://api.weatherapi.com/v1/current.json?" +
                f"key={local_config.WEATHER_API_KEY}&q={local_config.WEATHER_ZIPCODE}&aqi=no",
                timeout=local_config.WEATHER_TIMEOUT)
            data_raw = req.content
            req.close()

            with open(local_config.WEATHER_PERSIST_PATH, 'wb') as cachef:
                cachef.write(data_raw)

            return (json.loads(data_raw), datetime.datetime.now())
        except Exception:
            logging.exception("error fetching weather")
            return None

    def update_weather(self, temp_widget, weather_icon_widget):
        if (self.weather_data_timestamp is None or
            datetime.datetime.now() - self.weather_data_timestamp >
            local_config.WEATHER_UPDATE_TIME):
            (self.weather_data, self.weather_data_timestamp) = self.fetch_weather()
            self.need_repaint = True

        if not self.need_repaint:
            return

        try:
            if self.weather_data is None:
                logging.error("fail to get weather")
                return

            icon_url = self.weather_data['current']['condition']['icon']
            req = requests.get(f"http:{icon_url}", timeout=local_config.WEATHER_TIMEOUT)
            icon_raw = req.content
            req.close()

            icon_img = Image.open(io.BytesIO(icon_raw))
            icon_img = icon_img.crop(icon_img.getbbox())

            temp = self.weather_data['current']['temp_c']
            temp_widget.update(f"{int(temp):2d}C", temp, force=True)

            if weather_icon_widget.update(icon_img):
                self.need_repaint = False

        except Exception:
            logging.exception("error updating weather")
