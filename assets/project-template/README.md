# XIAO ESP32 PlatformIO + ESP-IDF 工程

面向 Seeed Studio XIAO ESP32C3、ESP32S3 和 ESP32C6 的个人项目模板：

- PlatformIO 管理 ESP-IDF、工具链、依赖、编译和烧录。
- MkDocs Material 管理硬件、固件、引脚及外围设备文档。
- GitHub Actions 验证全部板卡环境并构建文档站。
- 自动验收脚本验证真机启动，标准交付包携带版本、SHA-256 和烧录参数。

可选的完整本地资料库由 `XIAO_ESP32_REFERENCE_ROOT` 指定，未设置时默认为 `~/ESP32_资料整理`；本地资料库不存在时不影响固件或文档构建。工程文档的“资料索引”页记录了经过核对的官方入口和本地资料用法。

## 支持矩阵

| 环境 | 板卡 | Flash/PSRAM |
|---|---|---|
| `xiao_esp32c3` | Seeed XIAO ESP32C3 | 4 MB / 无板载 PSRAM |
| `xiao_esp32s3` | Seeed XIAO ESP32S3 | 8 MB / Octal PSRAM |
| `xiao_esp32c6` | Seeed XIAO ESP32C6 | 4 MB / 无板载 PSRAM |

## 快速开始

```bash
pio run -e xiao_esp32c3
pio run -e xiao_esp32c3 -t upload
pio device monitor -b 115200
```

把环境名替换为实际板卡。串口出现下面的稳定标志后，说明固件已确认
芯片系列与 Flash 容量符合所选配置；S3 还会确认 8 MB Octal PSRAM 已初始化：

```text
XIAO_RUNTIME_READY version=1 board=Seeed Studio XIAO ESP32C3
heartbeat count=1 uptime_ms=...
```

如果自检不通过，组件会输出实际值和期望值并中止，不会用错误硬件配置继续运行。该检查验证芯片和内存基线，不用于鉴别板卡厂商或具体扩展板变体。

自动验收当前固件，或显式授权烧录后验收：

```bash
python3 scripts/verify_hardware.py --environment xiao_esp32s3 --port auto
python3 scripts/verify_hardware.py --environment xiao_esp32s3 --port auto --flash --json-output
```

脚本在出现多个 Espressif 串口时拒绝猜测。D6/D7 留给业务 UART；应用日志通过 USB Serial/JTAG 输出，ROM 启动阶段仍可能短暂使用 UART0。

启动文档站：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-docs.txt
mkdocs serve
```

完整手册从 [`docs/index.md`](docs/index.md) 开始，涵盖环境搭建、板型/引脚、电气安全、固件配置和发布、I²C/SPI/UART/GPIO/ADC/PWM、ADS1115 完整实例、无线连接、调试与资料维护。

默认环境在 `platformio.ini` 的 `default_envs` 中修改。

## 工程结构

- `src/main.c`：应用入口，演示 `xiao_board` 组件（LED 心跳 + 环境自检日志）。
- `components/xiao_board/`：板级支持组件；新增外设驱动放入 `components/<device>/`。
- `include/xiao_pins.h`：XIAO 丝印 D0–D10 到各板 GPIO 的符号映射，业务代码不写裸 GPIO。
- `docs/`：文档站源码；新增外设页从 `docs/peripherals/_template.md` 复制。

版本与变更记录见 `CHANGELOG.md`；许可证为 Apache-2.0（`LICENSE`）。

## 验证

```bash
pio run -e xiao_esp32c3
pio run -e xiao_esp32s3
pio run -e xiao_esp32c6
.venv/bin/mkdocs build --strict
python3 -m unittest discover -s tests -v
```

构建后可生成带校验值的交付包：

```bash
python3 scripts/package_firmware.py --environment xiao_esp32s3
```

Apple Silicon 上还应确认 `pio system info` 为 `darwin_arm64`，RISC-V/Xtensa 编译器宿主可执行文件为 Mach-O arm64。
