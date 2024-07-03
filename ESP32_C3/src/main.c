#include "freertos/FreeRTOS.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "wifi.h"

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_LOGI("main", "ESP_WIFI_MODE_STA");
    wifi_init("iPhone", "218817479");
}
