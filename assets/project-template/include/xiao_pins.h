#pragma once

/*
 * XIAO silk-screen pin names mapped to ESP-IDF GPIO numbers.
 * Keep application code on these symbolic names instead of raw GPIO values.
 */

#if defined(XIAO_ESP32C3)

#define XIAO_BOARD_NAME "Seeed Studio XIAO ESP32C3"
#define XIAO_D0 2
#define XIAO_D1 3
#define XIAO_D2 4
#define XIAO_D3 5
#define XIAO_D4 6
#define XIAO_D5 7
#define XIAO_D6 21
#define XIAO_D7 20
#define XIAO_D8 8
#define XIAO_D9 9
#define XIAO_D10 10
#define XIAO_USER_LED (-1)
#define XIAO_EXPECTED_FLASH_BYTES (4U * 1024U * 1024U)
#define XIAO_EXPECTS_PSRAM 0
#define XIAO_EXPECTED_PSRAM_BYTES 0U

#elif defined(XIAO_ESP32S3)

#define XIAO_BOARD_NAME "Seeed Studio XIAO ESP32S3"
#define XIAO_D0 1
#define XIAO_D1 2
#define XIAO_D2 3
#define XIAO_D3 4
#define XIAO_D4 5
#define XIAO_D5 6
#define XIAO_D6 43
#define XIAO_D7 44
#define XIAO_D8 7
#define XIAO_D9 8
#define XIAO_D10 9
#define XIAO_USER_LED 21
#define XIAO_EXPECTED_FLASH_BYTES (8U * 1024U * 1024U)
#define XIAO_EXPECTS_PSRAM 1
#define XIAO_EXPECTED_PSRAM_BYTES (8U * 1024U * 1024U)

#elif defined(XIAO_ESP32C6)

#define XIAO_BOARD_NAME "Seeed Studio XIAO ESP32C6"
#define XIAO_D0 0
#define XIAO_D1 1
#define XIAO_D2 2
#define XIAO_D3 21
#define XIAO_D4 22
#define XIAO_D5 23
#define XIAO_D6 16
#define XIAO_D7 17
#define XIAO_D8 19
#define XIAO_D9 20
#define XIAO_D10 18
#define XIAO_USER_LED 15
#define XIAO_EXPECTED_FLASH_BYTES (4U * 1024U * 1024U)
#define XIAO_EXPECTS_PSRAM 0
#define XIAO_EXPECTED_PSRAM_BYTES 0U

#else
#error "Select a supported PlatformIO XIAO environment"
#endif

#define XIAO_I2C_SDA XIAO_D4
#define XIAO_I2C_SCL XIAO_D5
#define XIAO_UART_TX XIAO_D6
#define XIAO_UART_RX XIAO_D7
#define XIAO_SPI_SCK XIAO_D8
#define XIAO_SPI_MISO XIAO_D9
#define XIAO_SPI_MOSI XIAO_D10
