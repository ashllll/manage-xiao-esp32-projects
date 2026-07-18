#include <inttypes.h>
#include <stdbool.h>

#include "esp_chip_info.h"
#include "esp_flash.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "xiao_board.h"
#include "xiao_pins.h"

static const char *TAG = "xiao_esp32";

void app_main(void)
{
    esp_chip_info_t chip_info;
    uint32_t flash_size = 0;

    esp_chip_info(&chip_info);
    ESP_ERROR_CHECK(esp_flash_get_size(NULL, &flash_size));
    ESP_ERROR_CHECK(xiao_board_init());

    ESP_LOGI(TAG, "Board profile: %s", xiao_board_name());
    ESP_LOGI(TAG, "CPU cores: %d, flash: %" PRIu32 " MB",
             chip_info.cores, flash_size / (1024U * 1024U));
    ESP_LOGI(TAG, "Default I2C pins: SDA=GPIO%d, SCL=GPIO%d",
             XIAO_I2C_SDA, XIAO_I2C_SCL);

    const bool heartbeat_led = xiao_board_has_user_led();
    if (!heartbeat_led) {
        ESP_LOGI(TAG, "No user LED on this board profile; heartbeat is log-only.");
    }
    ESP_LOGI(TAG, "PlatformIO + ESP-IDF environment is ready.");

    while (true) {
        if (heartbeat_led) {
            ESP_ERROR_CHECK(xiao_board_led_toggle());
        }
        ESP_LOGI(TAG, "heartbeat");
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
