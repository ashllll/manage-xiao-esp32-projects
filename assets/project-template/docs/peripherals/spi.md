# SPI

默认总线使用 D8/SCK、D9/MISO、D10/MOSI。每个设备另选一个经核对的 GPIO 作为 CS，例如 D3；不要把同一个 CS 分给多个设备。

## 接线

| 信号 | XIAO | C3 / S3 / C6 GPIO | 说明 |
|---|---|---|---|
| SCK | D8 | 8 / 7 / 19 | 时钟 |
| MISO | D9 | 9 / 8 / 20 | 设备到主机；只写设备可不接 |
| MOSI | D10 | 10 / 9 / 18 | 主机到设备 |
| CS | 项目分配 | 按板型 | 每个设备独立，通常低有效 |

S3 Sense 的 microSD 常占 GPIO7/8/9，并与这组排针 SPI 和用户 LED GPIO21 产生资源冲突。使用扩展板时先查看原理图，不要同时初始化两个互相冲突的用途。

## 初始化

```c
#include "driver/spi_master.h"
#include "xiao_pins.h"

spi_bus_config_t bus_cfg = {
    .sclk_io_num = XIAO_SPI_SCK,
    .miso_io_num = XIAO_SPI_MISO,
    .mosi_io_num = XIAO_SPI_MOSI,
    .quadwp_io_num = -1,
    .quadhd_io_num = -1,
    .max_transfer_sz = 4096,
};
ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus_cfg, SPI_DMA_CH_AUTO));
```

添加设备：

```c
spi_device_handle_t device;
spi_device_interface_config_t dev_cfg = {
    .clock_speed_hz = 10 * 1000 * 1000,
    .mode = 0,
    .spics_io_num = XIAO_D3,
    .queue_size = 4,
};
ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &dev_cfg, &device));
```

同步传输：

```c
uint8_t tx[2] = {0x80, 0x00};
uint8_t rx[2] = {0};
spi_transaction_t t = {
    .length = sizeof(tx) * 8,
    .tx_buffer = tx,
    .rx_buffer = rx,
};
ESP_ERROR_CHECK(spi_device_transmit(device, &t));
```

组件声明 `PRIV_REQUIRES esp_driver_spi`。

## 每个设备必须记录

- SPI mode（CPOL/CPHA）和最大时钟。
- CS 上电默认电平、建立/保持时间。
- 是否全双工、半双工或仅写。
- 命令/地址/数据字节序。
- 最大事务长度、DMA 对齐和缓冲区生命周期。
- 共享 MISO 时设备在 CS 无效期间是否真正高阻。

高速失败时先降频验证，再用逻辑分析仪检查边沿、CS 和 mode。不要把面包板短线上的可用频率直接当作产品布线指标。

## 清理

先等待/取回所有排队事务，调用 `spi_bus_remove_device()`，最后 `spi_bus_free()`。多任务访问同一 device handle 时由组件加锁，不能在两个任务中同时发同步事务。

官方参考：[ESP-IDF SPI Master Driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/spi_master.html)。最近核对：2026-07-18。
