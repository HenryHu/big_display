"""Gets weather data"""
# pylint: disable=broad-except

import json
import logging
import io

import requests
from PIL import Image

import local_config

def update_weather(temp_widget, weather_icon_widget):
    try:
        req = requests.get(
            "http://api.weatherapi.com/v1/current.json?" +
            f"key={local_config.WEATHER_API_KEY}&q={local_config.WEATHER_ZIPCODE}&aqi=no",
            timeout=local_config.WEATHER_TIMEOUT)
        data_raw = req.content
        req.close()

        data = json.loads(data_raw)

        icon_url = data['current']['condition']['icon']
        req = requests.get(f"http:{icon_url}", timeout=local_config.WEATHER_TIMEOUT)
        icon_raw = req.content
        req.close()

        icon_img = Image.open(io.BytesIO(icon_raw))
        icon_img = icon_img.crop(icon_img.getbbox())

        temp = data['current']['temp_c']
        temp_widget.update(f"{int(temp):2d}C", temp, force=True)

        weather_icon_widget.update(icon_img)

    except Exception:
        logging.exception("error updating weather")
