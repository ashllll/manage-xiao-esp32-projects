# 项目开发流程

这套流程把代码、固件、接线和资料保持在同一个可验证状态。小改动可以合并步骤，但不能省略来源和硬件验证。

## 1. 写清需求

在动手接线前记录：

- 目标板卡和具体变体（C3、S3、S3 Sense、S3 Plus、C6）。
- 外设型号、模块版本、供电和逻辑电平。
- 需要的总线、采样/刷新频率、延迟和功耗目标。
- 无线协议、凭据提供方式和离线行为。
- 成功现象、错误现象和验收方法。

## 2. 先分配资源

1. 从[引脚表](hardware/pinout.md)选择 XIAO 丝印引脚。
2. 排除启动配置、原生 USB、用户 LED 和扩展板占用。
3. 为共享 I²C/SPI 总线记录地址、片选和最大速率。
4. 检查电源峰值电流，确认是否需要独立电源和共地。

输出一张接线表；没有接线表就不进入驱动编写。

## 3. 选择驱动来源

优先级如下：

1. ESP-IDF 内置驱动。
2. [Espressif Component Registry](https://components.espressif.com/) 中维护活跃、许可证清晰、支持目标芯片的组件。
3. 芯片/模块厂商官方 ESP-IDF 组件。
4. 本地自维护组件。

记录组件名、固定版本、许可证、目标芯片、示例和检索日期。Arduino 库不能直接用于当前 ESP-IDF 工程，除非明确引入 Arduino component 并接受其体积和生命周期影响。

## 4. 实现垂直切片

每次只完成一个可验证闭环：

```text
供电与接线 → 总线初始化 → 设备探测 → 一次读写 → 错误日志 → 文档
```

组件建议结构：

```text
components/<device>/
├── CMakeLists.txt
├── idf_component.yml      # 使用 Registry 依赖时
├── include/<device>.h     # 稳定公共 API
└── <device>.c
```

公共 API 返回 `esp_err_t`，把设备状态放到明确的 handle/context 中，不在驱动内部吞掉错误。应用层只依赖组件 API 和 `XIAO_*` 引脚符号。

## 5. 分层验证

| 层级 | 命令/方法 | 证明什么 |
|---|---|---|
| 静态结构 | `pio run -e <env>` | 依赖、API、配置和链接正确 |
| 配置 | 检查 `.pio/build/<env>/config/sdkconfig.h` | Flash、PSRAM 和功能开关正确 |
| 最小硬件 | 串口中的探测/一次读写日志 | 接线、地址和驱动基本可用 |
| 压力 | 长时间运行、断线、复位、异常输入 | 恢复路径和资源释放可靠 |
| 跨板卡 | 构建 C3/S3/C6 | 共用代码没有板型回归 |
| 文档 | `mkdocs build --strict` | 导航和文档结构完整 |

## 6. 交付固件

按[固件发布](firmware/release.md)收集应用、bootloader、partition table、`flash_args`、校验值和版本说明。只有在真实板卡上完成最小硬件验证后，才标记“硬件已验证”。

## 7. 更新资料

- 新外设：复制 `docs/peripherals/_template.md` 并加入导航。
- 引脚或板型事实：附 Seeed 官方链接和核对日期。
- ESP-IDF API：链接当前项目所用版本或 stable 文档。
- 大型 PDF/CAD：归档到 `XIAO_ESP32_REFERENCE_ROOT`（默认 `~/ESP32_资料整理`），项目只写索引。
- 变更版本：同步 `PROJECT_VER`、`CHANGELOG.md` 和发布说明。

## 完成定义

一个功能只有同时满足以下条件才算完成：代码可构建、目标硬件可复现、失败模式有日志、固件可追溯、接线/API/来源文档齐全、严格文档构建通过。
