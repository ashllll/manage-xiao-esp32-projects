#include "xiao_board.h"

#include <inttypes.h>

#include "driver/gpio.h"
#include "esp_chip_info.h"
#include "esp_flash.h"
#include "esp_log.h"
#include "xiao_pins.h"
#if XIAO_EXPECTS_PSRAM
#include "esp_psram.h"
#endif

/*
 * Seeed XIAO boards wire the user LED between 3V3 and the GPIO,
 * so the LED lights up when the pin is driven low.
 */
#define XIAO_BOARD_LED_ACTIVE_LEVEL 0

/*
 * Base C3 defines XIAO_USER_LED as (-1). Keep the shift below a compile-time
 * constant expression; the GPIO calls are still guarded at runtime by
 * xiao_board_has_user_led().
 */
#if XIAO_USER_LED >= 0
#define XIAO_BOARD_LED_PIN XIAO_USER_LED
#else
#define XIAO_BOARD_LED_PIN 0
#endif

static bool s_led_on;
static const char *TAG = "xiao_board";

#if defined(XIAO_ESP32C3)
#define XIAO_EXPECTED_CHIP_MODEL CHIP_ESP32C3
#elif defined(XIAO_ESP32S3)
#define XIAO_EXPECTED_CHIP_MODEL CHIP_ESP32S3
#elif defined(XIAO_ESP32C6)
#define XIAO_EXPECTED_CHIP_MODEL CHIP_ESP32C6
#endif

const char *xiao_board_name(void)
{
    return XIAO_BOARD_NAME;
}

bool xiao_board_has_user_led(void)
{
    return XIAO_USER_LED >= 0;
}

esp_err_t xiao_board_validate(xiao_board_diagnostics_t *diagnostics)
{
    if (diagnostics == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    *diagnostics = (xiao_board_diagnostics_t){0};
    esp_chip_info_t chip_info;
    esp_chip_info(&chip_info);
    if (chip_info.model != XIAO_EXPECTED_CHIP_MODEL) {
        ESP_LOGE(TAG, "Chip model mismatch for %s: actual=%d expected=%d",
                 XIAO_BOARD_NAME, chip_info.model, XIAO_EXPECTED_CHIP_MODEL);
        return ESP_ERR_INVALID_VERSION;
    }

    esp_err_t err = esp_flash_get_size(NULL, &diagnostics->flash_size_bytes);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Unable to read Flash size for %s: %s",
                 XIAO_BOARD_NAME, esp_err_to_name(err));
        return err;
    }
    if (diagnostics->flash_size_bytes != XIAO_EXPECTED_FLASH_BYTES) {
        ESP_LOGE(TAG, "Flash size mismatch for %s: actual=%" PRIu32 " expected=%u",
                 XIAO_BOARD_NAME, diagnostics->flash_size_bytes,
                 (unsigned)XIAO_EXPECTED_FLASH_BYTES);
        return ESP_ERR_INVALID_SIZE;
    }

#if XIAO_EXPECTS_PSRAM
    diagnostics->psram_initialized = esp_psram_is_initialized();
    if (!diagnostics->psram_initialized) {
        ESP_LOGE(TAG, "Required PSRAM was not initialized for %s", XIAO_BOARD_NAME);
        return ESP_ERR_INVALID_STATE;
    }
    diagnostics->psram_size_bytes = esp_psram_get_size();
    if (diagnostics->psram_size_bytes != XIAO_EXPECTED_PSRAM_BYTES) {
        ESP_LOGE(TAG, "PSRAM size mismatch for %s: actual=%u expected=%u",
                 XIAO_BOARD_NAME, (unsigned)diagnostics->psram_size_bytes,
                 (unsigned)XIAO_EXPECTED_PSRAM_BYTES);
        return ESP_ERR_INVALID_SIZE;
    }
#endif

    return ESP_OK;
}

esp_err_t xiao_board_init(void)
{
    if (!xiao_board_has_user_led()) {
        return ESP_OK;
    }

    const gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << XIAO_BOARD_LED_PIN,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    esp_err_t err = gpio_config(&cfg);
    if (err == ESP_OK) {
        err = xiao_board_led_set(false);
    }
    return err;
}

esp_err_t xiao_board_led_set(bool on)
{
    if (!xiao_board_has_user_led()) {
        return ESP_ERR_NOT_SUPPORTED;
    }

    int level = on ? XIAO_BOARD_LED_ACTIVE_LEVEL : 1 - XIAO_BOARD_LED_ACTIVE_LEVEL;
    s_led_on = on;
    return gpio_set_level(XIAO_BOARD_LED_PIN, level);
}

esp_err_t xiao_board_led_toggle(void)
{
    return xiao_board_led_set(!s_led_on);
}
