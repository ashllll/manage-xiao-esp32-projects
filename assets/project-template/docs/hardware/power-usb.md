# 供电、USB 与电气安全

## 电压边界

- 所有 ESP32 GPIO 都按 3.3 V 逻辑设计，不耐受 5 V。
- `3V3` 用于 3.3 V 外设；`5V/VBUS` 不能直接连接到 GPIO。
- 外设模块标称“5 V 供电”不代表其信号一定是 3.3 V 兼容，必须查原理图或数据手册。
- 外部电源与 XIAO 通信时必须共地；多个电源并联前先确认不会反向灌电。

## 电流预算

不要只按平均电流选电源。Wi-Fi 发射、摄像头、SD 卡写入、显示背光和电机启动会产生峰值。外围设备页应记录：

1. 模块静态和峰值电流。
2. 由 XIAO 供电还是独立电源供电。
3. 去耦电容、线长和压降。
4. 峰值发生时是否引发 brownout 或 USB 重连。

电机、继电器、加热器和高亮 LED 不由 GPIO 直接驱动；使用 MOSFET/驱动器、续流保护和独立电源。

## USB 数据线和端口

无法发现串口时，先排除“只能充电”的 USB-C 线。使用 `pio device list` 对比插拔前后的设备列表，并关闭占用端口的串口监视器。

S3 的 GPIO19/GPIO20 常用于原生 USB D-/D+。如果项目依赖原生 USB，不要把这些引脚当普通 GPIO。C3/C6 与 S3 的下载/控制台路径不同，具体以 PlatformIO board manifest 和 Seeed 官方页面为准。

## 电池

Seeed 官方资料说明 XIAO ESP32C3 可接 3.7 V 锂电池。焊接电池端子时必须确认极性，避免短路；电池供电时不能靠板载 LED 状态判断程序是否运行。其他型号或扩展底板的充电、电量测量和保护能力应按对应官方资料单独记录，不能从 C3 推断。

## 上电前检查

- [ ] 供电电压与模块数据手册一致。
- [ ] 所有信号不超过 3.3 V。
- [ ] 外部电源共地且不存在反向灌电。
- [ ] 启动配置引脚没有被外设强拉到错误电平。
- [ ] 峰值电流在电源、线材和稳压器能力范围内。
- [ ] 感性负载有驱动和保护，GPIO 不直接带负载。
- [ ] 首次上电可限流，并能通过串口观察 brownout/复位原因。

## 官方入口

- [XIAO ESP32C3：电池使用说明](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/)
- [XIAO ESP32S3 入门](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)
- [XIAO ESP32C6 入门](https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/)

最近核对：2026-07-18。
