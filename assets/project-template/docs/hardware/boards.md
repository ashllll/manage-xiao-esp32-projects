# XIAO 型号选择

| PlatformIO 环境 | Board ID | CPU 架构 | Flash/PSRAM | 无线重点 | 适合场景 |
|---|---|---|---|---|---|
| `xiao_esp32c3` | `seeed_xiao_esp32c3` | RISC-V，单核 | 4 MB / 无板载 PSRAM | 2.4 GHz Wi-Fi、BLE | 成本敏感、普通传感器、低复杂度联网 |
| `xiao_esp32s3` | `seeed_xiao_esp32s3` | Xtensa，双核 | 8 MB / Octal PSRAM | 2.4 GHz Wi-Fi、BLE | 摄像头、语音、显示、较大缓冲区和 USB 应用 |
| `xiao_esp32c6` | `seeed_xiao_esp32c6` | RISC-V，单核 | 4 MB / 无板载 PSRAM | Wi-Fi 6、BLE、IEEE 802.15.4 | Thread、Zigbee、Matter 或新一代低功耗联网 |

构建平台固定为 `platformio/espressif32@7.0.0`，对应 ESP-IDF 6.0.0 工具链。宿主环境为 Apple Silicon `darwin_arm64`。上表描述当前模板的配置，不替代芯片数据手册中的完整能力表。

## 选择原则

- 只需要 Wi-Fi/BLE 和少量传感器时优先 C3。
- 需要 PSRAM、摄像头、较大的图像/音频缓冲区或原生 USB 时优先 S3。
- 明确需要 802.15.4、Thread、Zigbee 或 Matter 时选择 C6，并先确认 ESP-IDF 组件、协议栈和认证需求。
- 已有扩展板时先按变体核对兼容性，不能只按“XIAO 14 针外形相同”推断电气和附加引脚完全一致。

## 变体边界

### S3 基础版

本项目的 D0–D10 表适用于通用顶部排针。用户 LED 位于 GPIO21，低电平点亮。

### S3 Sense

Sense 扩展板带摄像头和 microSD。常见 microSD 接线占用 GPIO7、GPIO8、GPIO9、GPIO21，会与排针 SPI 和用户 LED 冲突。摄像头型号可能随硬件批次变化，代码和文档必须记录实物批次。

### S3 Plus

Plus 暴露额外引脚，但不能把 Plus 的 D11/D12 或底部焊盘映射直接套用到基础版/Sense。项目若使用额外引脚，应新建专门板型配置，而不是修改共用 D0–D10 表。

官方资料：

- [XIAO ESP32C3 入门](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/)
- [XIAO ESP32S3 入门](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)
- [XIAO ESP32C6 入门](https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/)

!!! note
    XIAO ESP32S3 Sense、Plus 等衍生型号会占用额外 GPIO。使用摄像头、SD 卡或扩展底板前，请在外围设备文档中记录冲突。

## 编译时板型识别

`platformio.ini` 为三个环境分别定义 `XIAO_ESP32C3`、`XIAO_ESP32S3` 或 `XIAO_ESP32C6`。`include/xiao_pins.h` 根据该宏生成板名、引脚和用户 LED；不要在业务代码中自行重复板型判断。
