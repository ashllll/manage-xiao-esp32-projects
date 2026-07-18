#pragma once

/*
 * Minimal board-support API for Seeed Studio XIAO ESP32 boards.
 * Pin facts come from include/xiao_pins.h; application code should use
 * this component instead of touching raw GPIO numbers.
 */

#include <stdbool.h>

#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Human-readable board name, e.g. "Seeed Studio XIAO ESP32C3". */
const char *xiao_board_name(void);

/* True when the selected board profile exposes a user LED (S3, C6; not base C3). */
bool xiao_board_has_user_led(void);

/* Configure the user LED GPIO. Safe to call on boards without a user LED. */
esp_err_t xiao_board_init(void);

/* Drive the user LED. Returns ESP_ERR_NOT_SUPPORTED on boards without one. */
esp_err_t xiao_board_led_set(bool on);

/* Toggle the user LED. Returns ESP_ERR_NOT_SUPPORTED on boards without one. */
esp_err_t xiao_board_led_toggle(void);

#ifdef __cplusplus
}
#endif
