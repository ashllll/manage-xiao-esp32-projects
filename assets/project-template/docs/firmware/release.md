# 固件发布

发布的目标不是“给出一个 firmware.bin”，而是让未来的自己能确认它为哪块板、用什么版本构建、如何烧录和如何回退。

## 发布前门禁

- [ ] `PROJECT_VER` 与 `CHANGELOG.md` 一致。
- [ ] C3、S3、C6 构建全部成功。
- [ ] 目标板完成上电、串口、核心外设和无线最小验证。
- [ ] Flash/PSRAM 最终配置已检查。
- [ ] 文档 `mkdocs build --strict` 通过。
- [ ] 不含凭据、个人串口路径或调试后门。
- [ ] 升级/回退和数据迁移影响已说明。

## 产物清单

为每个环境单独打包：

```text
firmware-<version>-<environment>/
├── firmware.bin
├── bootloader.bin
├── partition-table.bin
├── flash_args
├── SHA256SUMS
└── RELEASE_NOTES.md
```

不同板型的二进制不可混用。文件名必须包含版本和 PlatformIO 环境名。

## 生成校验值

```bash
cd .pio/build/xiao_esp32c3
shasum -a 256 firmware.bin bootloader.bin partition_table/partition-table.bin
```

把结果写入发布包的 `SHA256SUMS`。校验值证明文件未变化，但不代替代码签名或 Secure Boot。

## 烧录信息

`flash_args` 是当前构建生成的偏移和参数来源。发布说明中记录：

- PlatformIO Core、Espressif32 Platform 和 ESP-IDF 版本。
- board ID、Flash/PSRAM 配置和分区表。
- 完整烧录命令或 `flash_args` 用法。
- 首次启动预期日志、版本显示和健康检查。
- OTA/串口升级的前置版本和回退条件。

不要手工猜 bootloader、partition table 和 app 的偏移。

## 发布说明模板

```markdown
# <版本> — <环境>

- 板卡/变体：
- PlatformIO 环境：
- Espressif32 / ESP-IDF：
- Git commit：
- Flash / PSRAM / 分区：
- 硬件验证：
- 新功能与修复：
- 已知问题：
- 升级与回退：
- SHA-256：
```

## CI

`.github/workflows/firmware.yml` 为三个环境构建并上传 `.bin` 与 `flash_args`。CI 产物只能证明构建可复现，不能证明真实外设、电源和射频功能已验证。只有用户明确要求时才创建 GitHub Release 或自动发布固件。
