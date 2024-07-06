#include "freertos/FreeRTOS.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include <string.h>
#include <cJSON.h>
#include "wifi.h"
#include "mqtt.h"
#include "vibro.h"
#include "parser.h"

// WiFi
static const char *wifi_login = "iPhone";
static const char *wifi_password = "218817479";

// MQTT
static const char *mqtt_uri = "mqtt://mqtt.eclipseprojects.io:1883";
static const char *mqtt_pull_topic = "5d9f651bff57b/esp32-cmd";
static const char *mqtt_push_topic = "5d9f651bff57b/laptop-cmd";

// Vibrato Motor
static const gpio_num_t vibrator_pin = GPIO_NUM_4;
static const int dot_duration = 500;
static const int dash_duration = 1000;
static const int pause_duration = 300;


void pull_topic_mqtt_callback(const char* data, const int data_len) {
    char* code = parse(data, data_len);
    vibrate(code);
    free(code);
}

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_LOGI("main", "ESP_WIFI_MODE_STA");

    wifi_init(wifi_login, wifi_password);
    connect_mqtt(mqtt_uri, mqtt_pull_topic, mqtt_push_topic, pull_topic_mqtt_callback);
    mqtt_publish("Hello from ESP32");

    setup_vibrator(vibrator_pin, dot_duration, dash_duration, pause_duration);
}

