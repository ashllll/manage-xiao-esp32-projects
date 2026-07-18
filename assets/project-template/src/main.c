#include <inttypes.h>
#include <stdbool.h>

#include "esp_chip_info.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "xiao_board.h"
#include "xiao_pins.h"

static const char *TAG = "xiao_esp32";

void app_main(void)
{
    esp_chip_info_t chip_info;
    xiao_board_diagnostics_t diagnostics;

    esp_chip_info(&chip_info);
    ESP_ERROR_CHECK(xiao_board_init());
    ESP_ERROR_CHECK(xiao_board_validate(&diagnostics));

    ESP_LOGI(TAG, "Board profile: %s", xiao_board_name());
    ESP_LOGI(TAG, "CPU cores: %d, flash: %" PRIu32 " MB",
             chip_info.cores, diagnostics.flash_size_bytes / (1024U * 1024U));
    ESP_LOGI(TAG, "Default I2C pins: SDA=GPIO%d, SCL=GPIO%d",
             XIAO_I2C_SDA, XIAO_I2C_SCL);
    ESP_LOGI(TAG, "Default UART pins: TX=GPIO%d, RX=GPIO%d",
             XIAO_UART_TX, XIAO_UART_RX);
    ESP_LOGI(TAG, "Default SPI pins: SCK=GPIO%d, MISO=GPIO%d, MOSI=GPIO%d",
             XIAO_SPI_SCK, XIAO_SPI_MISO, XIAO_SPI_MOSI);
#if XIAO_EXPECTS_PSRAM
    ESP_LOGI(TAG, "PSRAM initialized: %u MB",
             (unsigned)(diagnostics.psram_size_bytes / (1024U * 1024U)));
#endif

    const bool heartbeat_led = xiao_board_has_user_led();
    if (!heartbeat_led) {
        ESP_LOGI(TAG, "No user LED on this board profile; heartbeat is log-only.");
    }
    /*
     * Automation and humans can wait for this stable marker before treating a
     * flash/boot cycle as successful. Keep it machine-readable and versioned.
     */
    ESP_LOGI(TAG, "XIAO_RUNTIME_READY version=1 board=%s", xiao_board_name());

    uint32_t heartbeat_count = 0;
    while (true) {
        if (heartbeat_led) {
            ESP_ERROR_CHECK(xiao_board_led_toggle());
        }
        ++heartbeat_count;
        ESP_LOGI(TAG, "heartbeat count=%" PRIu32 " uptime_ms=%" PRId64,
                 heartbeat_count, esp_timer_get_time() / 1000);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
