#include "esp_log.h"
#include <stdio.h>
#include <unistd.h>
#include "driver/gpio.h"
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

int dot_duration = 500;
int dash_duration = 1000;
int pause_duration = 300;
gpio_num_t vibrator_pin = GPIO_NUM_12;

void setup_vibrator(gpio_num_t pin, int dot_duration_ms, int dash_duration_ms, int pause_duration_ms) {
    vibrator_pin = pin;
    dot_duration = dot_duration_ms;
    dash_duration = dash_duration_ms;
    pause_duration = pause_duration_ms;

    gpio_reset_pin(vibrator_pin);
    gpio_set_direction(vibrator_pin, GPIO_MODE_OUTPUT);
}

void activate_vibrator(int duration) {
    gpio_set_level(vibrator_pin, 1);
    vTaskDelay(pdMS_TO_TICKS(duration));
    gpio_set_level(vibrator_pin, 0);
}

void vibrate(const char *signals) {
    if (signals == NULL) {
        ESP_LOGI("main vibro", "Error: signals cant be NULL");
        return;
    }

    int length = strlen(signals);
    for (int i = 0; i < length; i++) {
        if (signals[i] != '.' && signals[i] != '-') {
            ESP_LOGI("main vibro", "Error: Invalid character in signal. Only '.' and '-' are allowed.");
            return;
        }
    }

    for (int i = 0; i < length; i++) {
        if (signals[i] == '.') {
            activate_vibrator(dot_duration);
        } else if (signals[i] == '-') {
            activate_vibrator(dash_duration);
        }
        if (i < length - 1) {
            vTaskDelay(pdMS_TO_TICKS(pause_duration));
        }
    }
}

void vibrate_task(void *pvParameters) {
    char* signals = (char*) pvParameters;
    vibrate(signals);
    free(signals);
    vTaskDelete(NULL);
}

void start_vibration(const char* signals) {
    char* task_signals = strdup(signals);
    if (task_signals) {
        xTaskCreate(vibrate_task, "VibratorTask", 2048, (void*)task_signals, 5, NULL);
    }
}