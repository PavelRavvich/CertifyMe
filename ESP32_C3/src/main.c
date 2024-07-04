#include "freertos/FreeRTOS.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "wifi.h"
#include <string.h>
#include "mqtt.h"

static const char *wifi_login = "iPhone";
static const char *wifi_password = "218817479";

static const char *mqtt_uri = "mqtt://mqtt.eclipseprojects.io:1883";
static const char *mqtt_pull_topic = "5d9f651bff57b/esp32-cmd";
static const char *mqtt_push_topic = "5d9f651bff57b/laptop-cmd";


void pull_topic_mqtt_callback(const char* data, const int data_len) {
    char* string_data = (char*) malloc(data_len + 1);
    if (string_data == NULL) {
        ESP_LOGE("main", "Failed to allocate memory");
        return;
    }
    memcpy(string_data, data, data_len);
    string_data[data_len] = '\0';

    printf("Received MQTT data: %s\n", string_data);

    free(string_data);
}

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_LOGI("main", "ESP_WIFI_MODE_STA");

    wifi_init(wifi_login, wifi_password);
    connect_mqtt(mqtt_uri, mqtt_pull_topic, mqtt_push_topic, pull_topic_mqtt_callback);
    mqtt_publish("Hello from ESP32");
}

