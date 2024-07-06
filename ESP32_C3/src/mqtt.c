#include "mqtt.h"
#include "mqtt_client.h"
#include "esp_log.h"

static const char *TAG = "MQTT_CLIENT";

static const char *mqtt_uri = NULL;
static const char *mqtt_pull_topic = NULL;
static const char *mqtt_push_topic = NULL;

static esp_mqtt_client_handle_t client = NULL;
static mqtt_data_callback_t g_callback = NULL;

void setup_mqtt(const char *uri, const char *pull_topic, const char *push_topic) {
    mqtt_uri = uri;
    mqtt_pull_topic = pull_topic;
    mqtt_push_topic = push_topic;
}

static esp_err_t mqtt_event_handler(esp_mqtt_event_handle_t event) {
    switch (event->event_id) {
        case MQTT_EVENT_CONNECTED:
            ESP_LOGI(TAG, "MQTT_EVENT_CONNECTED");
        esp_mqtt_client_subscribe_single(event->client, mqtt_pull_topic, 0);
        break;
        case MQTT_EVENT_DISCONNECTED:
            ESP_LOGI(TAG, "MQTT_EVENT_DISCONNECTED");
        break;
        case MQTT_EVENT_DATA:
            ESP_LOGI(TAG, "Received data: %.*s", event->data_len, event->data);
            if (g_callback != NULL) {
                g_callback(event->data, event->data_len);
            }
        break;
        default:
            ESP_LOGI(TAG, "Unhandled event: %d", event->event_id);
        break;
    }
    return ESP_OK;
}

static void mqtt_event_handler_wrapper(void* handler_args, esp_event_base_t event_base, int32_t event_id, void* event_data) {
    esp_mqtt_event_handle_t event = (esp_mqtt_event_handle_t) event_data;
    mqtt_event_handler(event);
}

void connect_mqtt(
    const char *uri,
    const char *pull_topic,
    const char *push_topic,
    mqtt_data_callback_t callback
) {
    mqtt_uri = uri;
    mqtt_pull_topic = pull_topic;
    mqtt_push_topic = push_topic;
    g_callback = callback;

    esp_mqtt_client_config_t mqtt_cfg = {
        .broker = {
            .address = {
                .uri = mqtt_uri
            }
        }
    };

    client = esp_mqtt_client_init(&mqtt_cfg);
    esp_mqtt_client_register_event(client, MQTT_EVENT_ANY, mqtt_event_handler_wrapper, NULL);
    esp_mqtt_client_start(client);
}

void mqtt_publish(const char* data) {
    if (client) {
        int len = strlen(data);
        int msg_id = esp_mqtt_client_publish(client, mqtt_push_topic, data, len, 1, 0);
        if (msg_id != -1) {
            ESP_LOGI(TAG, "Sent publish successful, msg_id=%d", msg_id);
        } else {
            ESP_LOGE(TAG, "Failed to publish");
        }
    } else {
        ESP_LOGE(TAG, "MQTT client is not initialized");
    }
}