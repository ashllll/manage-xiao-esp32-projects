# 快速开始

## 1. 前置条件

本项目在 Apple Silicon Mac 上验证。终端应能找到 Python 3 和 PlatformIO：

```bash
uname -m
python3 --version
pio --version
```

预期 `uname -m` 输出 `arm64`。如果尚未安装 PlatformIO，推荐使用隔离的 Python 环境或官方 PlatformIO Core 安装方式；不要用系统 Python 混装项目依赖。

克隆或复制工程后，先进入根目录：

```bash
export XIAO_ESP32_PROJECT_ROOT="${XIAO_ESP32_PROJECT_ROOT:-$HOME/code/esp/xiao_esp32}"
cd "$XIAO_ESP32_PROJECT_ROOT"
pio system info
```

也可直接进入任意克隆或复制出来的工程根目录；上述环境变量只是可选的跨终端便捷入口。

`pio system info` 的平台应包含 `darwin_arm64`。

推荐让 `~/.platformio/penv/bin` 位于 PATH 前部，避免调用系统 Python 3.9 下的旧入口。`command -v pio` 应指向隔离环境，`pio --version` 应为 6.1.19。

## 2. 选择开发板

默认是 XIAO ESP32C3。可以使用 `-e` 临时选择目标：

```bash
pio run -e xiao_esp32c3
pio run -e xiao_esp32s3
pio run -e xiao_esp32c6
```

也可以修改 `platformio.ini`：

```ini
[platformio]
default_envs = xiao_esp32s3
```

环境名必须与实际板卡一致。S3 基础版、Sense、Plus 的扩展硬件不同；本模板只把顶部 D0–D10 和通用用户 LED作为板级基线。

## 3. 首次编译

```bash
pio run -e xiao_esp32c3
pio run -e xiao_esp32s3
pio run -e xiao_esp32c6
```

第一次运行会下载 PlatformIO 平台、ESP-IDF 和交叉编译器。不要同时 `source export.sh` 激活另一套本机 ESP-IDF；本工程由 PlatformIO 管理框架和工具链。

## 4. 连接和烧录

使用可传输数据的 USB-C 线连接开发板：

```bash
pio device list
pio run -e xiao_esp32c3 -t upload
pio device monitor -b 115200
```

预期日志包含编译配置标签、实测 Flash 容量、默认 I²C/UART/SPI 引脚，随后出现：

```text
I (...) xiao_esp32: XIAO_RUNTIME_READY version=1 board=Seeed Studio XIAO ESP32C3
I (...) xiao_esp32: heartbeat count=1 uptime_ms=...
```

`XIAO_RUNTIME_READY` 只会在运行时 Flash/PSRAM 自检通过后输出，适合人工验收和后续串口自动化脚本使用。C3 基础版没有可由应用控制的用户 LED，因此只有日志心跳；S3/C6 同时闪烁用户 LED。

若自动下载失败，按住 BOOT，短按 RESET，松开 BOOT 后重新执行上传。不要把 `/dev/cu.*` 端口写入共享的 `platformio.ini`。

## 5. 构建文档

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-docs.txt
.venv/bin/mkdocs build --strict
.venv/bin/mkdocs serve
```

浏览器打开终端显示的本地地址。`--strict` 会把失效导航、链接和 Markdown 警告作为失败处理。

## 6. 完成检查

- [ ] 目标板环境编译成功。
- [ ] 串口日志中的芯片系列与所选 PlatformIO 环境一致。
- [ ] Flash 容量为 C3/C6 4 MB 或 S3 8 MB。
- [ ] 串口出现 `XIAO_RUNTIME_READY version=1`，并持续输出递增的心跳计数。
- [ ] S3 日志显示 PSRAM 已初始化，而不只是构建配置声称启用。
- [ ] 生成配置使用 USB Serial/JTAG 主控制台，D6/D7 未被应用日志占用。
- [ ] `mkdocs build --strict` 成功。
- [ ] 新增外设前已阅读[引脚定义](hardware/pinout.md)和[电气安全](hardware/power-usb.md)。

生成物位于 `.pio/`、`.venv/` 和 `site/`，均不属于源文件。
