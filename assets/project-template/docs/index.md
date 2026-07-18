# XIAO ESP32 开发手册

本项目是一套可直接编译的 PlatformIO + ESP-IDF 工程，也是面向个人嵌入式项目的维护手册。它同时支持 Seeed Studio XIAO ESP32C3、ESP32S3 和 ESP32C6，并固定使用 `platformio/espressif32@7.0.0` 与 ESP-IDF 6.0.0。

## 从这里开始

| 目标 | 入口 | 完成标志 |
|---|---|---|
| 首次搭建环境 | [快速开始](getting-started.md) | 三个环境至少完成目标板编译，文档严格构建通过 |
| 选择板卡和引脚 | [型号对比](hardware/boards.md)、[引脚定义](hardware/pinout.md) | 接线表使用 D0–D10 和对应 GPIO，不含冲突 |
| 添加传感器或模块 | [外围设备集成](peripherals/index.md) | 组件、接线、依赖、最小验证和来源记录齐全 |
| 接入高精度模拟采集 | [ADS1115 实战](peripherals/ads1115.md) | 可探测设备，并用已知电压完成读数核对 |
| 编译、烧录和导出固件 | [编译与烧录](firmware/build-flash.md)、[固件发布](firmware/release.md) | 固件、Flash 参数和校验值可追溯 |
| 排查启动或串口问题 | [调试手册](debugging/index.md) | 能定位到供电、端口、下载模式、配置或外设冲突 |
| 查官方资料和本机归档 | [资料索引](reference/resources.md) | 结论注明来源、版本/板型和核对日期 |

## 核心约定

- 应用代码使用 `include/xiao_pins.h` 中的 `XIAO_D0`–`XIAO_D10`，不散布裸 GPIO 数字。
- 可复用驱动放在 `components/<device>/`，公共 API 放在组件的 `include/` 目录。
- 每个真实外设都有独立文档页，至少包含电气、接线、总线、依赖、验证、冲突和来源。
- 机密信息、串口路径和机器专属配置不提交到仓库。
- `docs/` 只保留经过复核的操作说明；PDF、CAD、镜像和历史工程留在 `XIAO_ESP32_REFERENCE_ROOT`（默认 `~/ESP32_资料整理`）指向的外部资料库。

```mermaid
flowchart LR
    A[需求与接线] --> B[外围设备组件]
    B --> C[PlatformIO 构建]
    C --> D[烧录与验证]
    D --> E[固件与文档发布]
```

## 当前基线

| 项目 | 值 |
|---|---|
| PlatformIO Core | 6.1.19 |
| Espressif32 Platform | 7.0.0（固定版本） |
| ESP-IDF | 6.0.0（由 PlatformIO 平台集成） |
| 文档 | MkDocs 1.6.x + Material 9.7.x |
| 本机 | Apple Silicon / `darwin_arm64` |
| 最近核对 | 2026-07-18 |

!!! info "模板与项目的边界"
    这里提供板级基线和通用流程。真实项目仍应在外设页中写明具体模块批次、供电、地址、采样率、协议版本和实测板卡；不能把“能编译”当成“硬件已验证”。
