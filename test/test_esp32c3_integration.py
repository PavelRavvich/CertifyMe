import time
import unittest
import paho.mqtt.client as mqtt
from conf import mqtt_pull_topic, mqtt_host, mqtt_port, mqtt_push_topic
import json


class TestESP32Mqtt(unittest.TestCase):
    def setUp(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connected = False
        self.messages = []
        self.message_received = False

    def tearDown(self):
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            self.connected = True
            self.client.subscribe(mqtt_pull_topic)
        else:
            print(f"Failed to connect, return code {rc}\n")

    def on_message(self, client, userdata, msg):
        print(msg.payload.decode('utf-8'))
        self.messages.append(json.loads(msg.payload.decode('utf-8')))

    def test_receive_data_from_esp32(self):
        def on_message(client, userdata, msg):
            print(msg.payload.decode('utf-8'))
            self.message_received = True

        self.client.on_message = on_message
        self.client.connect(mqtt_host, mqtt_port, 60)
        self.client.loop_start()
        self.client.subscribe(mqtt_pull_topic)
        while not self.message_received:
            time.sleep(1)

        self.client.loop_stop()

    def test_mqtt_connection_esp32c3_send_data(self):
        self.client.connect(mqtt_host, mqtt_port, 60)
        self.client.loop_start()
        time.sleep(2)
        self.assertTrue(self.connected)

        test_message = {"cmd": "vibration", "code": "...--"}
        self.client.publish(mqtt_push_topic, json.dumps(test_message))
        self.client.loop_stop()


if __name__ == '__main__':
    unittest.main()