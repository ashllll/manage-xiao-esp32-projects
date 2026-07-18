# I²C

默认使用 D4/SDA 和 D5/SCL；GPIO 映射由 `XIAO_I2C_SDA`、`XIAO_I2C_SCL` 提供。

## 电气与接线

| 信号 | XIAO | C3 / S3 / C6 GPIO | 要求 |
|---|---|---|---|
| SDA | D4 | 6 / 5 / 22 | 3.3 V 开漏，上拉 |
| SCL | D5 | 7 / 6 / 23 | 3.3 V 开漏，上拉 |
| VCC | 3V3 | — | 按模块数据手册核对电流 |
| GND | GND | — | 必须共地 |

模块常自带上拉；多个模块并联会让等效阻值过低。内部上拉只适合临时实验，正式设计使用合适的外部上拉并根据电容、线长和速率测量波形。

## ESP-IDF 6.0 主机初始化

ESP-IDF 6.0 应使用新 I²C master driver。旧 `driver/i2c.h` 已在 6.0 标记 EOL，不要为新组件复制旧 command-link 示例。

```c
#include "driver/i2c_master.h"
#include "xiao_pins.h"

static i2c_master_bus_handle_t s_bus;

static esp_err_t app_i2c_init(void)
{
    const i2c_master_bus_config_t cfg = {
        .i2c_port = 0,
        .sda_io_num = XIAO_I2C_SDA,
        .scl_io_num = XIAO_I2C_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = false,
    };
    return i2c_new_master_bus(&cfg, &s_bus);
}
```

添加设备：

```c
i2c_master_dev_handle_t device;
const i2c_device_config_t dev_cfg = {
    .dev_addr_length = I2C_ADDR_BIT_LEN_7,
    .device_address = 0x48,
    .scl_speed_hz = 100000,
};
ESP_ERROR_CHECK(i2c_master_bus_add_device(s_bus, &dev_cfg, &device));
```

典型寄存器读取：

```c
uint8_t reg = 0x00;
uint8_t data[2];
ESP_ERROR_CHECK(i2c_master_transmit_receive(
    device, &reg, sizeof(reg), data, sizeof(data), 100));
```

组件 `CMakeLists.txt` 增加 `PRIV_REQUIRES esp_driver_i2c`。

## 地址扫描 { #i2c-address-scan }

扫描仅用于诊断，不是产品初始化流程。对 `0x08`–`0x77` 逐个调用 `i2c_master_probe()`，给每次探测设置有限超时；某些设备会因协议副作用或上电状态不响应扫描，应以数据手册为准。

## 错误处理

| 错误 | 常见原因 | 处理 |
|---|---|---|
| NACK | 地址错误、设备未上电、设备忙 | 核对 7 位地址和时序，有限重试 |
| timeout | SCL/SDA 被拉低、速率/线长不合适 | 断电检查接线和上拉，必要时恢复总线 |
| 数据跳变 | 电源噪声、上拉不当、共享总线竞争 | 示波器/逻辑分析仪检查并降低速率 |
| 多任务冲突 | 多处直接操作同一 handle | 由单一组件串行化访问 |

释放时先 `i2c_master_bus_rm_device()`，所有设备移除后再 `i2c_del_master_bus()`。

## 官方 API

- [ESP-IDF stable：I²C](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/i2c.html)
- [ESP-IDF 6.0 外设迁移说明](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/migration-guides/release-6.x/6.0/peripherals.html)

最近核对：2026-07-18。
