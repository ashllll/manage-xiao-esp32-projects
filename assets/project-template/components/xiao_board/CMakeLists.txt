idf_component_register(
    SRCS "xiao_board.c"
    INCLUDE_DIRS "include"
    PRIV_REQUIRES esp_driver_gpio esp_hw_support spi_flash esp_psram
)
