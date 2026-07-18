# <外设名称>（模板）

> 复制本页为 `docs/peripherals/<device>.md`，删除本提示，并把新页面加入 `mkdocs.yml` 的 `nav`。
> 本文件已通过 mkdocs.yml 的 `exclude_docs` 排除，不参与构建。

## 概要

- 型号 / 模块版本：
- 适用板卡：C3 / S3 / C6（注明实际测试过的型号与扩展板变体）
- SDK / 驱动来源：<ESP-IDF 内置 API ｜ esp-registry 组件 `namespace/name@x.y.z` ｜ 本地 `components/<device>`>
- 检索 / 核对日期：YYYY-MM-DD

## 电气特性

| 项目 | 值 | 备注 |
|---|---|---|
| 供电电压 | 3.3 V | |
| 峰值电流 | | |
| 逻辑电平 | | ESP32 GPIO 不耐受 5 V |

## 接线

| 信号 | XIAO 引脚 | GPIO（C3 / S3 / C6） | 外设引脚 | 说明 |
|---|---|---|---|---|
| SDA | D4 | 6 / 5 / 22 | SDA | 3.3 V，上拉 |
| SCL | D5 | 7 / 6 / 23 | SCL | 3.3 V，上拉 |
| VCC | 3V3 | — | VCC | |
| GND | GND | — | GND | |

## 总线配置

- 协议 / 地址 / 速率：
- 上拉要求：
- 共享总线时的注意事项：

## 固件集成

依赖固定方式（二选一或并用）：

```yaml
# components/<device>/idf_component.yml
dependencies:
  namespace/name: "x.y.z"
```

- Kconfig / sdkconfig 变更：
- 初始化顺序与失败行为：

## 最小验证

```bash
pio run -e xiao_esp32c3 -t upload
pio device monitor -b 115200
```

预期输出 / 现象：

## 已知问题与冲突

- <与启动配置引脚、原生 USB、S3 Sense 扩展板等的冲突>

## 来源记录

| 资料 | URL | 版本 | 检索日期 |
|---|---|---|---|
| 数据手册 | | | |
| 驱动 / 组件 | | | |
