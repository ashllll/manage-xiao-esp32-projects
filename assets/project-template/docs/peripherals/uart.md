# UART

默认排针 D6/TX、D7/RX；连接外设时 TX 接对方 RX、RX 接对方 TX，并共地。只接受 3.3 V TTL 电平，不能直接连接 RS-232 ± 电压或 5 V TTL。

| 信号 | XIAO | C3 / S3 / C6 GPIO |
|---|---|---|
| TX | D6 | 21 / 43 / 16 |
| RX | D7 | 20 / 44 / 17 |

本模板将 ESP-IDF 应用控制台固定到 USB Serial/JTAG，因此 D6/D7 可由 `UART_NUM_1` 使用。芯片 ROM 在 ESP-IDF bootloader 接管前仍可能短暂通过 UART0 输出启动字节；外设若会主动驱动 RX、对启动字节敏感或与 UART0 共用内部资源，仍需评估上电时序。不要通过烧写 eFuse 隐藏日志。

## 初始化示例

```c
#include "driver/uart.h"
#include "xiao_pins.h"

static const uart_port_t PORT = UART_NUM_1;

uart_config_t cfg = {
    .baud_rate = 115200,
    .data_bits = UART_DATA_8_BITS,
    .parity = UART_PARITY_DISABLE,
    .stop_bits = UART_STOP_BITS_1,
    .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
    .source_clk = UART_SCLK_DEFAULT,
};
ESP_ERROR_CHECK(uart_driver_install(PORT, 2048, 0, 0, NULL, 0));
ESP_ERROR_CHECK(uart_param_config(PORT, &cfg));
ESP_ERROR_CHECK(uart_set_pin(
    PORT, XIAO_UART_TX, XIAO_UART_RX,
    UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
```

组件声明 `PRIV_REQUIRES esp_driver_uart`。

## 协议层

UART 只定义字节传输。外设页还必须定义：

- 波特率、数据位、校验、停止位和流控。
- 帧头、长度、命令、负载、CRC 和字节序。
- 帧间超时、最大帧长和错误恢复。
- 模块上电/复位/唤醒所需控制引脚和时序。

接收任务应使用有限缓冲区和明确状态机，不依赖“读到一次就是完整帧”。记录短读、超时、溢出、CRC 错误和未知命令。

## RS-485/RS-232

连接 RS-485 需要收发器和 DE/RE 方向控制；连接 RS-232 需要电平转换器。不要把协议名称与电气层混淆。长线、工业现场和不同供电域还要考虑隔离、终端和浪涌保护。

## 验证

1. 先做本机 TX/RX 回环。
2. 再连接外设并捕获原始十六进制帧。
3. 验证断电、半帧、错误 CRC、超时和重连。
4. 在生成的 sdkconfig 中确认 `CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG` 已启用且 `CONFIG_ESP_CONSOLE_UART` 未启用。

官方参考：[ESP-IDF UART](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/uart.html)。最近核对：2026-07-18。
