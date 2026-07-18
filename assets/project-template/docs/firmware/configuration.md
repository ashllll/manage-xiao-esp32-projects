# 配置与依赖

## 配置分层

本项目不提交根目录生成的 `sdkconfig`，而是使用可复现的 defaults：

| 文件 | 适用范围 | 关键配置 |
|---|---|---|
| `sdkconfig.defaults` | 所有板卡 | 115200 控制台、INFO 日志、体积优化 |
| `sdkconfig.flash-4mb` | C3、C6 | 4 MB Flash |
| `sdkconfig.xiao-esp32s3` | S3 | 8 MB Flash、Octal PSRAM |

`platformio.ini` 把每个环境生成的配置放到 `.pio/sdkconfig-<environment>`。修改 `menuconfig` 后，不要直接提交生成文件；把需要长期保留的选项提炼到对应 defaults，再清理重建验证。

## 查看配置

```bash
pio run -e xiao_esp32s3 -t menuconfig
```

检查最终编译头：

```bash
rg 'CONFIG_ESPTOOLPY_FLASHSIZE|CONFIG_SPIRAM' \
  .pio/build/xiao_esp32s3/config/sdkconfig.h
```

预期：

- C3/C6：`CONFIG_ESPTOOLPY_FLASHSIZE_4MB`。
- S3：`CONFIG_ESPTOOLPY_FLASHSIZE_8MB`、`CONFIG_SPIRAM`、`CONFIG_SPIRAM_MODE_OCT`。

## PlatformIO 依赖

根环境固定 `platform = espressif32@7.0.0`。更新平台时应一次性验证三个环境、Flash/PSRAM、固件大小和文档，并在 `CHANGELOG.md` 记录 PlatformIO 平台与 ESP-IDF 对应关系。

不要单独覆盖 `framework-espidf` 为更高版本，除非同时验证 PlatformIO 构建脚本、工具链、board manifest 和三个目标板。版本号更高不等于集成更稳定。

## ESP-IDF 组件依赖

Registry 组件通过 `idf_component.yml` 固定版本：

```yaml
dependencies:
  idf: ">=6.0,<6.1"
  espressif/example_component: "1.2.3"
```

规则：

1. 精确记录实际使用版本，不使用无界 `*`。
2. 检查许可证、维护状态、示例和支持芯片。
3. 把组件配置写入 defaults 或组件 Kconfig，不提交密钥。
4. 升级前读 release notes，并重新跑硬件最小验证。

## CMake 依赖

每个组件声明直接依赖。例如 I²C 组件：

```cmake
idf_component_register(
    SRCS "sensor.c"
    INCLUDE_DIRS "include"
    PRIV_REQUIRES esp_driver_i2c
)
```

如果头文件的公共类型直接引用某组件类型，应使用 `REQUIRES`；仅 `.c` 内部使用则优先 `PRIV_REQUIRES`。

## 机密与环境差异

- Wi-Fi、云端和证书机密通过 NVS provisioning、构建环境变量或安全存储注入。
- `upload_port`、`monitor_port` 和个人代理设置放在未提交的本地覆盖中。
- 不把 `.pio/`、`.venv/`、`site/` 或生成的 `sdkconfig` 当作源文件。
- CI 和本机使用相同固定平台，但主机工具链架构可以不同；固件目标仍由交叉编译器决定。

## 变更检查

- [ ] defaults 只包含需要固定的选项。
- [ ] 三个环境都重新构建。
- [ ] S3 PSRAM 和三板 Flash 容量检查通过。
- [ ] 依赖版本与来源已写入外设页。
- [ ] 没有密钥、串口路径和机器专属路径进入提交内容。
