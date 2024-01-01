"""Gets sensor data"""
# pylint: disable=too-many-arguments,broad-except

import logging
import json

import paho.mqtt.client as mqtt

import local_config

class SensorData:
    temp = None
    humid = None

    def temp_str(self):
        return f"{self.temp:.1f}C"

    def humid_str(self):
        return f"{self.humid:.1f}%"

    def persist(self):
        with open(local_config.SENSOR_PERSIST_PATH, 'w', encoding='utf-8') as outf:
            outf.write(json.dumps({"temp": self.temp, "humid": self.humid}))

    def restore(self):
        try:
            with open(local_config.SENSOR_PERSIST_PATH, encoding='utf-8') as inf:
                saved_state = json.loads(inf.read())
                self.temp = saved_state["temp"]
                self.humid = saved_state["humid"]
        except Exception:
            logging.exception("fail to load saved sensor state")


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
        self.sensor_data.persist()
