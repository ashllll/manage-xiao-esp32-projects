# 外围设备集成

外设集成从电气和资源分配开始，不从复制示例代码开始。当前工程是 ESP-IDF，不直接使用 Arduino 的 `Wire`、`SPI`、`Serial`、`analogRead` 等 API。

## 总线入口

| 类型 | 默认 XIAO 引脚 | ESP-IDF 6.0 入口 | 适用设备 |
|---|---|---|---|
| I²C | D4 SDA、D5 SCL | `driver/i2c_master.h` | 传感器、RTC、ADC、小屏幕 |
| SPI | D8 SCK、D9 MISO、D10 MOSI；CS 自选 | `driver/spi_master.h` | 显示、SD 卡、高速 ADC、Flash |
| UART | D6 TX、D7 RX | `driver/uart.h` | GNSS、Modbus、蜂窝/串口模块 |
| GPIO | 任意经核对的 D 引脚 | `driver/gpio.h` | 按键、中断、片选、开关量 |
| ADC | 按板型能力核对 | `esp_adc/adc_oneshot.h` | 电压、模拟传感器 |
| PWM | GPIO matrix 可路由引脚 | `driver/ledc.h` | LED、蜂鸣器、简单调速 |

详见 [I²C](i2c.md)、[ADS1115 实战](ads1115.md)、[SPI](spi.md)、[UART](uart.md) 和 [GPIO/ADC/PWM](gpio-adc-pwm.md)。

## 新外设的落地步骤

1. 从数据手册确认供电、逻辑电平、峰值电流和协议。
2. 在[引脚资源表](../hardware/pinout.md)中分配总线和控制引脚。
3. 优先查 ESP-IDF 内置驱动与 [Espressif Component Registry](https://components.espressif.com/)。
4. 固定组件版本，检查许可证和目标芯片支持。
5. 先实现“探测 + 一次读写 + 错误日志”的最小闭环。
6. 对断线、NACK、超时、CRC、错误 ID 和重新初始化进行验证。
7. 复制 `_template.md` 建立真实外设页，并加入 `mkdocs.yml`。

## 外设页最低要求

每个外设建立独立页面，并至少记录：

1. 型号、模块版本和原厂资料链接。
2. 供电电压、峰值电流和逻辑电平。
3. XIAO 引脚与外设引脚对应关系。
4. 总线地址、速率和上拉要求。
5. 使用的 SDK/驱动来源与固定版本。
6. 初始化示例、错误码和已知问题。

推荐表格：

| 信号 | XIAO 引脚 | GPIO | 外设引脚 | 说明 |
|---|---|---:|---|---|
| SDA | D4 | 按开发板映射 | SDA | 3.3 V，上拉 |
| SCL | D5 | 按开发板映射 | SCL | 3.3 V，上拉 |

此外必须写明：

- 哪块实际板卡和哪一批模块已测试；“能编译”与“硬件已验证”分开标注。
- 初始化顺序、超时、重试上限、资源释放和恢复策略。
- `CMakeLists.txt`/`idf_component.yml` 的直接依赖。
- 串口预期日志或可测量现象。
- 与启动配置、USB、用户 LED、S3 Sense microSD/摄像头的冲突。
- 数据手册、组件和官方示例的 URL、版本及核对日期。

## 共享总线规则

- I²C 设备共享 SDA/SCL，但地址必须唯一，整条总线只保留合适的等效上拉。
- SPI 设备共享 SCK/MOSI/MISO，每个设备使用独立 CS，并分别配置 mode/clock。
- 多任务共享同一设备或总线时，在一个组件内串行化访问，避免调用方各自创建 driver。
- 总线错误不能无限重试；记录错误、限制次数，并提供重新初始化或设备降级策略。

## 现有资料

本机资料库包含 ADS1115 数据手册、原理图和历史工程，可从[资料索引](../reference/resources.md)定位；可直接按 [ADS1115 实战](ads1115.md)完成接线、驱动与验证。历史代码可能是 Arduino、旧 ESP-IDF API，或包含未经核实的依赖声明，只作为线索，接入本工程前必须按 ESP-IDF 6.0 重写和验证。
