# 无线连接

## 能力矩阵

| 板卡 | Wi-Fi | BLE | IEEE 802.15.4 |
|---|---|---|---|
| XIAO ESP32C3 | 2.4 GHz Wi-Fi | 支持 | 不支持 |
| XIAO ESP32S3 | 2.4 GHz Wi-Fi | 支持 | 不支持 |
| XIAO ESP32C6 | 2.4 GHz Wi-Fi 6 | 支持 | 支持 |

802.15.4 是底层无线能力，不等于项目自动具备 Zigbee、Thread 或 Matter。还需要对应 ESP-IDF 组件/协议栈、分区、密钥、网络角色、互操作和可能的认证工作。

## Wi-Fi 集成顺序

1. 初始化 NVS、event loop 和 `esp_netif`。
2. 创建 STA/AP netif，再初始化 Wi-Fi driver。
3. 注册事件处理，设置模式和配置。
4. 启动并用有限次数重连。
5. 只有获得 IP 后才启动依赖网络的业务。

凭据不得写入仓库。个人项目可通过串口/BLE provisioning 后存入 NVS；量产项目还应设计设备身份、证书轮换和恢复流程。

## BLE

在 NimBLE 与 Bluedroid 之间按功能、内存和生态选择，不要同时启用无用 host。文档应记录角色、GATT service/characteristic UUID、权限、MTU、配对/绑定策略、广告间隔和断线恢复。

## C6 的 802.15.4

开始 Zigbee/Thread/Matter 项目前先确认：

- 使用的 ESP-IDF/组件版本明确支持 ESP32-C6。
- 协议角色、网络拓扑、信道和共存策略已确定。
- 分区和 NVS 能保存网络数据与升级状态。
- 设备密钥和 commissioning 数据有安全注入方式。
- 真实设备完成互操作和长时间共存测试。

## 射频与共存

- 2.4 GHz Wi-Fi、BLE 和 802.15.4 共用射频资源，吞吐/延迟目标必须在真实并发场景中测量。
- 天线区域远离金属、电池、显示排线和高噪声电源；XIAO 小尺寸并不消除布局影响。
- 日志记录断线原因和重试节奏，但不记录密码、密钥和完整身份令牌。
- 断网时业务应有明确降级行为，避免紧密重连循环耗电或阻塞看门狗。

## 官方入口

- [ESP-IDF Wi-Fi](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/wifi.html)
- [ESP-IDF Bluetooth API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/bluetooth/index.html)
- [ESP-IDF ESP32-C6 文档](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/)
- [Espressif Component Registry](https://components.espressif.com/)

最近核对：2026-07-18。
