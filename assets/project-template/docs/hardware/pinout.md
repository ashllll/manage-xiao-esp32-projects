# 引脚与复用

下表是 XIAO 顶部 D0–D10 排针映射；代码定义位于 `include/xiao_pins.h`。

| XIAO | ESP32C3 | ESP32S3 | ESP32C6 | 模板符号 | 默认用途 |
|---|---:|---:|---:|---|---|
| D0 | GPIO2 | GPIO1 | GPIO0 | `XIAO_D0` | ADC/GPIO |
| D1 | GPIO3 | GPIO2 | GPIO1 | `XIAO_D1` | ADC/GPIO |
| D2 | GPIO4 | GPIO3 | GPIO2 | `XIAO_D2` | ADC/GPIO |
| D3 | GPIO5 | GPIO4 | GPIO21 | `XIAO_D3` | GPIO/片选 |
| D4 | GPIO6 | GPIO5 | GPIO22 | `XIAO_D4` / `XIAO_I2C_SDA` | I²C SDA |
| D5 | GPIO7 | GPIO6 | GPIO23 | `XIAO_D5` / `XIAO_I2C_SCL` | I²C SCL |
| D6 | GPIO21 | GPIO43 | GPIO16 | `XIAO_D6` / `XIAO_UART_TX` | UART TX |
| D7 | GPIO20 | GPIO44 | GPIO17 | `XIAO_D7` / `XIAO_UART_RX` | UART RX |
| D8 | GPIO8 | GPIO7 | GPIO19 | `XIAO_D8` / `XIAO_SPI_SCK` | SPI SCK |
| D9 | GPIO9 | GPIO8 | GPIO20 | `XIAO_D9` / `XIAO_SPI_MISO` | SPI MISO |
| D10 | GPIO10 | GPIO9 | GPIO18 | `XIAO_D10` / `XIAO_SPI_MOSI` | SPI MOSI |

“默认用途”是本模板的约定，并不表示 GPIO matrix 只能这样复用。改变总线引脚时，要同时更新 `xiao_pins.h`、外设接线页和实测记录。

## 代码用法

```c
#include "driver/gpio.h"
#include "xiao_pins.h"

gpio_config_t cfg = {
    .pin_bit_mask = 1ULL << XIAO_D3,
    .mode = GPIO_MODE_OUTPUT,
};
ESP_ERROR_CHECK(gpio_config(&cfg));
ESP_ERROR_CHECK(gpio_set_level(XIAO_D3, 1));
```

组件通过根目录 `platformio.ini` 的 `-I include` 访问该头文件。公共组件 API 不应要求调用方再次传入同一组裸 GPIO。

## 使用提醒

- ESP32C3 的 GPIO2、GPIO8、GPIO9 是启动配置相关引脚；外围电路不要在复位时强制错误电平。
- ESP32C3 的 D6 会输出启动日志，作为输入使用时要特别谨慎。
- ESP32S3 的 GPIO19/20 通常用于原生 USB，不应随意改作普通 GPIO。
- S3 Sense 的 microSD 会占用 GPIO7、GPIO8、GPIO9、GPIO21。
- 接入 5 V 外设前确认其逻辑电平；ESP32 GPIO 不耐受 5 V。

## 分配清单

每个项目维护一张资源表，至少回答：

| 资源 | 检查项 |
|---|---|
| GPIO | 上电/复位电平、输入输出方向、内部上下拉、是否跨板卡可用 |
| I²C | 地址冲突、上拉位置、总线电压、线长和速率 |
| SPI | 每个设备的 CS、模式、最大时钟、MISO 三态行为 |
| UART | 电平、波特率、TX/RX 交叉、是否与启动日志/控制台冲突 |
| ADC | 可测范围、衰减、校准、信号源阻抗、无线工作时的限制 |
| PWM | 定时器/通道、频率、分辨率和负载驱动方式 |

## 来源

- [Seeed XIAO ESP32C3 官方入门](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/)
- [Seeed XIAO ESP32S3 官方入门](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)
- [Seeed XIAO ESP32C6 官方入门](https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/)

最近核对：2026-07-18。若官方页面与本表冲突，先核对板卡变体和批次，再修改代码与文档。
