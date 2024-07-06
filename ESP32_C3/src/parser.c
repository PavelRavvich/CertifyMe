#include "esp_log.h"
#include "parser.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

char* parse(const char* data, const int data_len) {
    char* string_data = (char*) malloc(data_len + 1);
    if (string_data == NULL) {
        ESP_LOGI("main parser", "Error: Failed to allocate memory");
        return NULL;
    }
    memcpy(string_data, data, data_len);
    string_data[data_len] = '\0';

    cJSON* json = cJSON_Parse(string_data);
    char* code_value = NULL;
    if (json != NULL) {
        cJSON* code = cJSON_GetObjectItem(json, "code");
        if (code != NULL && cJSON_IsString(code)) {
            code_value = strdup(code->valuestring);
        }
        cJSON_Delete(json);
    }

    free(string_data);
    return code_value;
}
