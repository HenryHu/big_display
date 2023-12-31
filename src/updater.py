#!/usr/bin/env python3

import sys
import time
import datetime
import requests
import local_config
import logging
import paho.mqtt.client as mqtt

class SensorData(object):
    temp = None
    humid = None

    def temp_str(self):
        return "%rC" % self.temp

    def humid_str(self):
        return "%r%%" % self.humid

class ImageWidget(object):
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

    def image(self, filename):
        try:
            data = open(filename, 'rb').read()
            w = local_config.WIDTH
            h = local_config.HEIGHT
            r = requests.post("http://%s/bitmap?x=%d&y=%d&w=%d&h=%d" % (
                local_config.LOCAL_IP, self.x, self.y, w, h), data=data)
        except Exception as e:
            logging.error(e)

    def update(self, filename):
        self.image(filename)

class TextWidget(object):
    x = 0
    y = 0
    text = ''

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def text_out(self, x, y, text, r=255, g=255, b=255):
        try:
            r = requests.get("http://%s/text?x=%d&y=%d&text=%s&r=%d&g=%d&b=%d" % (
                local_config.LOCAL_IP, x, y, text, r, g, b), timeout=1)
            r.close()
        except Exception as e:
            logging.error(e)

    def update(self, text, r=255, g=255, b=255):
        if text != self.text:
            if self.text and len(text) != len(self.text):
                self.text_out(self.x, self.y, ' ' * len(self.text))
            self.text_out(self.x, self.y, text, r, g, b)
            self.text = text

class RangedTextWidget(TextWidget):
    color_map = None
    def __init__(self, x, y, color_map={}):
        TextWidget.__init__(self, x, y)
        self.color_map = color_map

    def update(self, text, value):
        for entry in sorted(self.color_map):
            if value < entry:
                TextWidget.update(self, text, *self.color_map[entry])
                return
        TextWidget.update(self, text)

class SensorMqttClient(object):
    client = None
    topic = None
    sensor_data = None

    def __init__(self, server, user, password, topic, sensor_data):
        self.topic = topic
        self.sensor_data = sensor_data

        self.client = mqtt.Client()
        self.client.username_pw_set(user, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(server)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            logging.error("MQTT connect error! rc=" + rc)
            return
        logging.info("MQTT connected.")
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        logging.info(msg.topic, payload.split('&'))
        for part in payload.split('&'):
            (key, value) = part.split('=')
            if key == 'TEMP':
                self.sensor_data.temp = float(value)
            if key == 'HUM':
                self.sensor_data.humid = float(value)

def main():
    sensor = SensorData()
    mqtt_client = SensorMqttClient(local_config.MQTT_SERVER, local_config.MQTT_USER,
                                local_config.MQTT_PASS, local_config.MQTT_TOPIC,
                                sensor)

    requests.get("http://%s/clear" % local_config.LOCAL_IP)
    background = ImageWidget(0, 0)
    background.update("out.bmp")

    date_widget = TextWidget(3, 0)
    time_widget = TextWidget(5, 8)

    temp_widget = RangedTextWidget(0, 16, {
        15: (0, 0, 255),
        20: (0, 255, 0),
        27: (0, 255, 255),
        30: (255, 255, 0),
        40: (255, 0, 0)
    })
    humid_widget = RangedTextWidget(35, 16, {
        10: (255, 0, 0),
        20: (0, 255, 255),
        70: (0, 255, 0),
        90: (255, 255, 0),
        100: (0, 0, 255),
    })

    while True:
        now = datetime.datetime.now()

        date_widget.update(now.strftime("%Y.%m.%d"))
        time_widget.update(now.strftime("%H:%M:%S"))

        if sensor.temp is not None:
            temp_widget.update(sensor.temp_str(), sensor.temp)
        if sensor.humid is not None:
            humid_widget.update(sensor.humid_str(), sensor.humid)

        time.sleep(0.1)

if __name__ == "__main__":
    main()
