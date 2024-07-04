#ifndef MQTT_H
#define MQTT_H

typedef void (*mqtt_data_callback_t)(const char* data, int data_len);

void connect_mqtt(
    const char *uri,
    const char *pull_topic,
    const char *push_topic,
    mqtt_data_callback_t callback);

void mqtt_publish(const char* data);

#endif