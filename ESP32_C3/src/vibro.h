#ifndef VIBRO_H
#define VIBRO_H

#include "driver/gpio.h"

void vibrate(const char *signals);

void setup_vibrator(gpio_num_t pin, int dot_duration_ms, int dash_duration_ms, int pause_duration_ms);

#endif