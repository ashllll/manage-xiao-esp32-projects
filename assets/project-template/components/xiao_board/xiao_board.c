#include "xiao_board.h"

#include "driver/gpio.h"
#include "xiao_pins.h"

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

const char *xiao_board_name(void)
{
    return XIAO_BOARD_NAME;
}

bool xiao_board_has_user_led(void)
{
    return XIAO_USER_LED >= 0;
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
