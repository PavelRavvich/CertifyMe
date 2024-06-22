import base64
import json
import logging
import paho.mqtt.client as mqtt

import os

from io import BytesIO

import datetime
import requests
import pyautogui

from PIL import Image
from screeninfo import get_monitors

import ssl
import sys

from conf import mqtt_pull_topic, mqtt_host, mqtt_port, mqtt_push_topic, prompt, max_tokens

print(ssl.OPENSSL_VERSION)
print(sys.executable)


api_key = os.getenv("OPENAI_API_KEY")
max_retry = 3
screenshots = []

pull_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
push_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)


def make_screenshot():
    def capture_screen():
        monitors = get_monitors()
        monitor = monitors[len(monitors)]
        region = (monitor.x, monitor.y, monitor.width, monitor.height)
        logging.info(f"Capturing screen region: {region}")
        return pyautogui.screenshot(region=region)

    def encode_base64_image(image: Image) -> str:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def save_image(image: Image):
        try:
            os.makedirs("screen_history", exist_ok=True)
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join("screen_history", f"screenshot_{current_time}.png")
            image.save(screenshot_path, "PNG")
            logging.info(f"Image successfully saved to {screenshot_path}")
        except Exception as e:
            logging.error(f"An error occurred while saving the image: {e}")

    screen = capture_screen()
    save_image(screen)
    return encode_base64_image(screen)


def ai_complete(base64_image_list):
    def images_to_request():
        return [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}"
                }
            }
            for image in base64_image_list
        ]

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                               {
                                   "type": "text",
                                   "text": prompt
                               }
                           ] + images_to_request()
            }
        ],
        "max_tokens": max_tokens
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    def request_openai():
        retry = 0
        while retry < max_retry:
            try:
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                return response.json()["choices"][0]['message']['content']
            except Exception as e:
                logging.error(f"An error occurred while calling the AI: {e}")
                retry += 1
        return "An error occurred while calling the AI."

    logging.info("Shift + Space pressed. AI completion in progress...")
    return request_openai()


def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            logging.info("Connected successfully to MQTT broker")
            client.subscribe(mqtt_pull_topic)
        else:
            logging.error(f"Failed to connect, return code {rc}")

    def on_disconnect(client, userdata, rc):
        logging.warning("Disconnected from MQTT broker, attempting to reconnect")
        client.reconnect()

    try:
        pull_client.on_connect = on_connect
        push_client.on_disconnect = on_disconnect
        pull_client.on_disconnect = on_disconnect
        pull_client.on_message = on_message

        pull_client.connect(mqtt_host, mqtt_port, 60)
        push_client.connect(mqtt_host, mqtt_port, 60)
    except Exception as e:
        logging.error("Failed to connect MQTT clients: " + str(e))
        exit(1)


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode('utf-8'))
    cmd = payload.get("cmd")
    if cmd == "save-screenshot":
        screenshot = make_screenshot()
        screenshots.append(screenshot)
        notification = {"status": "SCREEN_SAVED"}
        push_client.publish(mqtt_push_topic, json.dumps(notification))
        logging.info("Screenshot created.")
    elif cmd == "clear-screenshots":
        screenshots.clear()
        notification = {"status": "SCREEN_CLEAR"}
        push_client.publish(mqtt_push_topic, json.dumps(notification))
        logging.info("Screenshots cleared.")
    elif cmd == "send-to-ai":
        result = ai_complete(screenshots)
        notification = {"status": "AI_COMPLETE", "answer": result}
        push_client.publish(mqtt_push_topic, json.dumps(notification))
        logging.info(f"AI completion result: {result}")
        screenshots.clear()
    else:
        logging.warning(f"Unknown command: {cmd}")
        notification = {"status": "UNKNOWN_CMD"}
        push_client.publish(mqtt_push_topic, json.dumps(notification))


def run_mqtt():
    connect_mqtt()
    pull_client.loop_forever()


def main():
    run_mqtt()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script interrupted by user. Exiting...")

