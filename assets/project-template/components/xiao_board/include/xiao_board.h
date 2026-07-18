#pragma once

/*
 * Minimal board-support API for Seeed Studio XIAO ESP32 boards.
 * Pin facts come from include/xiao_pins.h; application code should use
 * this component instead of touching raw GPIO numbers.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Human-readable board name, e.g. "Seeed Studio XIAO ESP32C3". */
const char *xiao_board_name(void);

/* True when the selected board profile exposes a user LED (S3, C6; not base C3). */
bool xiao_board_has_user_led(void);

/*
 * Runtime facts used to verify the selected profile's hardware prerequisites.
 * A successful validation means the chip family and Flash capacity match the
 * profile and, for S3, the expected external PSRAM is available to ESP-IDF.
 */
typedef struct {
    uint32_t flash_size_bytes;
    size_t psram_size_bytes;
    bool psram_initialized;
} xiao_board_diagnostics_t;

/*
 * Validate chip and storage resources against the selected XIAO profile.
 * Returns ESP_ERR_INVALID_VERSION for a chip-family mismatch,
 * ESP_ERR_INVALID_SIZE for a Flash/PSRAM capacity mismatch, and
 * ESP_ERR_INVALID_STATE when required PSRAM is unavailable. The component
 * logs actual and expected values before returning a validation error.
 */
esp_err_t xiao_board_validate(xiao_board_diagnostics_t *diagnostics);

/* Configure the user LED GPIO. Safe to call on boards without a user LED. */
esp_err_t xiao_board_init(void);

/* Drive the user LED. Returns ESP_ERR_NOT_SUPPORTED on boards without one. */
esp_err_t xiao_board_led_set(bool on);

/* Toggle the user LED. Returns ESP_ERR_NOT_SUPPORTED on boards without one. */
esp_err_t xiao_board_led_toggle(void);

#ifdef __cplusplus
}
#endif
