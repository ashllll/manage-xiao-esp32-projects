# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与[语义化版本](https://semver.org/lang/zh-CN/)。
版本号与根目录 `CMakeLists.txt` 中的 `PROJECT_VER` 保持一致；发布时同步更新两者并打 Git Tag。

## [Unreleased]

## [0.1.0] - 2026-07-18

### Added

- 初始模板：PlatformIO + ESP-IDF 三环境（`xiao_esp32c3` / `xiao_esp32s3` / `xiao_esp32c6`），分层 sdkconfig。
- `include/xiao_pins.h`：XIAO 丝印 D0–D10 到各板 GPIO 的符号映射及 I2C/UART/SPI 默认引脚。
- `components/xiao_board`：板级支持组件（用户 LED 心跳、板级信息 API），`main.c` 演示调用。
- MkDocs Material 中文文档站：硬件、引脚、固件、外围设备、调试、资料索引，以及 `docs/peripherals/_template.md` 外设页模板。
- GitHub Actions：固件三环境矩阵构建（含 PlatformIO 缓存）与 MkDocs Pages 部署。
- Apache-2.0 LICENSE。
