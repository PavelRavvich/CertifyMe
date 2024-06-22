import time
import unittest
from unittest.mock import patch
import paho.mqtt.client as mqtt
from conf import mqtt_pull_topic, mqtt_host, mqtt_port, mqtt_push_topic
import json

import laptop_client


class TestMQTTCommands(unittest.TestCase):
    def setUp(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connected = False
        self.messages = []

    def tearDown(self):
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            self.connected = True
            self.client.subscribe(mqtt_pull_topic)
        else:
            print(f"Failed to connect, return code {rc}\n")

    def on_message(self, client, userdata, msg):
        self.messages.append(json.loads(msg.payload.decode('utf-8')))

    def test_mqtt_connection(self):
        self.client.connect(mqtt_host, mqtt_port, 60)
        self.client.loop_start()
        time.sleep(2)
        self.assertTrue(self.connected)

        test_message = {"cmd": "save-screenshot"}
        self.client.publish(mqtt_pull_topic, json.dumps(test_message))
        time.sleep(1)

        self.assertIn(test_message, self.messages)

        self.client.loop_stop()


if __name__ == '__main__':
    unittest.main()
