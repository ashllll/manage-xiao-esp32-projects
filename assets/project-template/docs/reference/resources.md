# 资料索引

本工程使用两层资料：工程内保存经过复核的精简说明；完整官方归档、PDF、原理图、模型和历史资料保留在独立资料库中。

## 本地资料库

资料库路径由环境变量指定；未设置时使用用户主目录下的默认位置：

```bash
export XIAO_ESP32_REFERENCE_ROOT="${XIAO_ESP32_REFERENCE_ROOT:-$HOME/ESP32_资料整理}"
```

该目录是可选的本地增强资料库，不是构建依赖；公开仓库只保留经过复核的索引和官方来源链接。

重点入口：

| 内容 | 本地路径 | 用途 |
|---|---|---|
| 总索引 | `README.md` | 查看可信度规则、当前入口和目录边界 |
| 清理记录 | `清理记录_2026-07-18.md` | 查看移除文件、原因和可恢复位置 |
| S3 官方归档 | `官方文档/Seeed_XIAO_ESP32S3_Getting_Started/` | 未经语义改写的官方中文 Raw Markdown 和资源清单 |
| 历史 PlatformIO 项目 | `02_PlatformIO项目/` | 查找已经验证过的接线与实现 |
| 硬件资料 | `04_硬件_数据手册/` | ADS1115 等外围设备数据手册和原理图 |
| 原 XIAO 工作目录 | `归档/SeeedStudioXIAOESP32_2026-07-18/` | 数据手册、第三方库和原工作环境归档；错误派生手册已移出 |
| ESP-IDF 源码 | `05_ESP-IDF源码/` | 查询当前本机 framework 实现；注意区分版本 |
| 工具链与 SDK 缓存 | `06_工具链_SDK缓存/` | 离线定位已安装包，不作为可提交依赖 |
| 固件二进制 | `07_固件_二进制/` | 历史构建线索；使用前必须核对板型、版本和校验值 |

!!! warning
    历史 AI 派生手册、迁移前的全盘扫描清单和低可信快捷入口已于 2026-07-18 移出资料库。`03_文档资料/` 现在只提供可信入口说明。不要恢复已隔离的旧手册作为开发依据。

## Seeed 官方入口

| 型号 | 官方中文文档 | 官方 GitHub Markdown |
|---|---|---|
| XIAO ESP32C3 | [快速上手](https://wiki.seeedstudio.com/cn/XIAO_ESP32C3_Getting_Started/) | [原始文档](https://github.com/Seeed-Studio/wiki-documents/blob/docusaurus-version/sites/zh-CN/docs/Sensor/SeeedStudio_XIAO/SeeedStudio_XIAO_ESP32C3/cn_XIAO_ESP32C3_Getting_Started.md) |
| XIAO ESP32S3 | [快速上手](https://wiki.seeedstudio.com/cn/xiao_esp32s3_getting_started/) | [原始文档](https://github.com/Seeed-Studio/wiki-documents/blob/docusaurus-version/sites/zh-CN/docs/Sensor/SeeedStudio_XIAO/SeeedStudio_XIAO_ESP32S3/cn_XIAO_ESP32S3_Getting_Started.md) |
| XIAO ESP32C6 | [快速上手](https://wiki.seeedstudio.com/cn/xiao_esp32c6_getting_started/) | [原始文档](https://github.com/Seeed-Studio/wiki-documents/blob/docusaurus-version/sites/zh-CN/docs/Sensor/SeeedStudio_XIAO/SeeedStudio_XIAO_ESP32C6/cn_XIAO_ESP32C6_Getting_Started.md) |

还应结合以下权威来源：

- [ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/latest/)
- [PlatformIO Espressif 32 平台](https://registry.platformio.org/platforms/platformio/espressif32)
- [PlatformIO XIAO ESP32C3](https://docs.platformio.org/en/latest/boards/espressif32/seeed_xiao_esp32c3.html)
- [PlatformIO XIAO ESP32S3](https://docs.platformio.org/en/latest/boards/espressif32/seeed_xiao_esp32s3.html)
- [PlatformIO XIAO ESP32C6](https://docs.platformio.org/en/latest/boards/espressif32/seeed_xiao_esp32c6.html)

## ESP-IDF API 入口

| 主题 | 官方文档 |
|---|---|
| I²C | [I²C master driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/i2c.html) |
| SPI | [SPI master](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/spi_master.html) |
| UART | [UART](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/uart.html) |
| ADC | [ADC oneshot](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/adc_oneshot.html) |
| PWM | [LEDC](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/ledc.html) |
| Wi-Fi | [Wi-Fi Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/wifi.html) |
| C6 | [ESP32-C6 Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/) |

`stable` 页面当前可能指向 ESP-IDF 6.0.x 的最新补丁，而本工程基线是 6.0.0。复制 API 前同时核对本机 `framework-espidf` 头文件；遇到补丁差异时以当前构建依赖为准，并在升级后统一更新文档。

## MCP 查询用途

- `espressif-documentation`：查当前 ESP-IDF 编程指南、API 和迁移说明。
- `esp-component-registry`：查外设组件、版本、示例和许可证。
- `codebase-memory-mcp`：查本地代码结构、调用关系和影响范围。
- `playwright-browser`：处理需要动态页面交互的官方 Wiki。

MCP 结果是研究输入，不自动成为项目事实。板级电气和引脚仍需对照 Seeed 官方页面，组件仍需固定版本并通过本地构建/硬件验证。

## 已复核的重要差异

- ESP32C3 的 GPIO2、GPIO8、GPIO9 涉及启动配置；D6 会输出启动日志。
- ESP32S3 基础版、Sense 与 Plus 的扩展引脚并不完全相同，不能共用一张扩展引脚表。
- S3 Sense 的 microSD 会占用 GPIO7、GPIO8、GPIO9、GPIO21，并与排针 SPI/用户 LED 资源产生冲突。
- S3 Sense 后续批次的摄像头型号可能不同，应用应以当前硬件和官方说明为准，避免只写死旧型号。
- ESP32C6 具备 802.15.4 能力，但具体 Zigbee/Thread 功能仍取决于所用 ESP-IDF、组件和项目配置。

本页最后核对日期：2026-07-18。

当前工程工具链基线：PlatformIO Core 6.1.19、Espressif 32 Platform 7.0.0、ESP-IDF 6.0.0、Apple Silicon `darwin_arm64`。
