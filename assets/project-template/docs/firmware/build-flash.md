# 编译与烧录

## 编译单个环境

```bash
pio run -e xiao_esp32c3
```

编译全部环境：

```bash
pio run -e xiao_esp32c3
pio run -e xiao_esp32s3
pio run -e xiao_esp32c6
```

常用输出：

```text
.pio/build/<environment>/firmware.bin
.pio/build/<environment>/bootloader.bin
.pio/build/<environment>/partition_table/partition-table.bin
.pio/build/<environment>/flash_args
```

固件大小接近分区上限时，先查看组件占用和分区设计，不要只关闭编译器警告或随意扩大分区。

## 查找串口

```bash
pio device list
```

插拔开发板前后各执行一次，比对新增的 `/dev/cu.*`。优先使用 `cu` 设备进行终端连接。若没有变化，检查数据线、USB Hub、供电和下载模式。

## 烧录和监视

```bash
pio run -e xiao_esp32c3 -t upload
pio device monitor -b 115200
```

退出监视器通常使用 `Ctrl+]`。烧录前关闭其他串口程序，避免端口占用。

## 真机验收

上传后不要只看 `SUCCESS`。上传成功只说明串口写入完成，下面四项都满足才算模板在真机上落地：

1. 日志中的芯片系列与上传环境一致；板名是编译配置标签，不是厂商身份鉴别结果。
2. C3/C6 报告 4 MB Flash，S3 报告 8 MB Flash 并显示 PSRAM 容量。
3. 出现 `XIAO_RUNTIME_READY version=1`。
4. 至少观察 10 次连续、递增的 `heartbeat count=`，S3/C6 的用户 LED 同步翻转。

若板型或资源不匹配，自检会在 READY 标志之前失败。此时应修正 `-e` 环境或确认板卡变体，不要删除自检绕过问题。

推荐使用可复用脚本完成同一套检查：

```bash
python3 scripts/verify_hardware.py \
  --environment xiao_esp32s3 --port auto --heartbeats 10
```

默认只复位并读取串口。只有添加 `--flash` 才会调用 PlatformIO 写入固件；多块 Espressif 设备同时连接时必须显式提供 `--port`。

## 固件交付包

```bash
python3 scripts/package_firmware.py --environment xiao_esp32s3
```

输出到 `dist/<environment>/`，包含应用、bootloader、分区表、flash 参数、`manifest.json` 和 `SHA256SUMS`。应用固件超过 768 KiB 时打包失败，为 1 MiB 应用分区保留升级空间。

如果设备没有进入下载模式，按住 BOOT、短按 RESET，然后松开 BOOT 再重试。端口不稳定时，可在对应环境中显式配置 `upload_port` 和 `monitor_port`，但不要把个人机器的端口提交到共享模板。

## 擦除与恢复

擦除会删除 NVS、配网信息和应用数据，只在明确需要时执行：

```bash
pio run -e xiao_esp32c3 -t erase
```

执行前先确认环境和串口。擦除后重新烧录完整固件，并重新配置设备。

## 检查目标配置

```bash
rg 'CONFIG_ESPTOOLPY_FLASHSIZE|CONFIG_SPIRAM' \
  .pio/build/xiao_esp32s3/config/sdkconfig.h
```

不要从 `platformio.ini` 的意图推断构建结果；以生成的 `sdkconfig.h` 和构建日志为证据。

## Apple Silicon 工具链检查

```bash
uname -m
pio system info
file ~/.platformio/packages/toolchain-riscv32-esp/bin/riscv32-esp-elf-gcc
file ~/.platformio/packages/toolchain-xtensa-esp-elf/bin/xtensa-esp-elf-gcc
```

宿主可执行文件应为 Mach-O arm64，PlatformIO 应报告 `darwin_arm64`。工具链名称中的 RISC-V/Xtensa 是固件目标架构，不是 Mac 宿主架构。

## 常见失败

| 现象 | 首要检查 |
|---|---|
| `No serial data received` | BOOT/RESET、数据线、端口、外设是否拉住启动引脚 |
| 端口突然消失 | 供电、brownout、USB Hub、原生 USB 引脚复用 |
| 链接失败 | 组件 `REQUIRES`、API 是否与 ESP-IDF 6.0 匹配 |
| S3 运行时内存不足 | PSRAM 是否启用、缓冲区是否实际分配到外部 RAM |
| 构建使用错误框架 | 确认 `framework = espidf`，示例不是 Arduino API |

完整排查树见[调试手册](../debugging/index.md)。
