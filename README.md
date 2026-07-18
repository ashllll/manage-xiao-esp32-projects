# Manage XIAO ESP32 Projects

[![Validate Skill](https://github.com/ashllll/manage-xiao-esp32-projects/actions/workflows/validate.yml/badge.svg)](https://github.com/ashllll/manage-xiao-esp32-projects/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

面向 Seeed Studio XIAO ESP32 系列的跨 Agent 开发 Skill。它把 PlatformIO、ESP-IDF、MkDocs Material、官方资料、固件交付和真机验证整理为一套可复用流程，适合个人项目快速起步，也适合将既有工程迁移成结构统一、可持续维护的仓库。

当前支持：

| 开发板 | PlatformIO 环境 | Flash | 处理器与特性 |
| --- | --- | ---: | --- |
| XIAO ESP32C3 | `xiao_esp32c3` | 4 MB | RISC-V、Wi-Fi、BLE |
| XIAO ESP32S3 | `xiao_esp32s3` | 8 MB | Xtensa、Wi-Fi、BLE、Octal PSRAM |
| XIAO ESP32C6 | `xiao_esp32c6` | 4 MB | RISC-V、Wi-Fi 6、BLE、IEEE 802.15.4 |

> Apple Silicon 已验证：PlatformIO Core 6.1.19、`platformio/espressif32@7.0.1`、ESP-IDF 6.0.1、MkDocs 1.6.1、Material 9.7.7，主机平台为 `darwin_arm64`。版本基线最后核对于 2026-07-18。

## 它能做什么

- 从模板创建 C3、S3 或 C6 工程，同时保留三个可构建环境。
- 生成 PlatformIO + ESP-IDF 工程、MkDocs Material 文档站和 GitHub Actions 校验流程。
- 按开发板应用 Flash、PSRAM、USB Serial/JTAG 等差异化配置。
- 校验工程结构、构建全部环境、严格构建文档，并检查固件交付物。
- 打包可烧录固件及 SHA-256 校验清单。
- 通过串口验证真机启动标记和连续 heartbeat；烧录操作必须显式启用。
- 安装并审计同一 Skill 在 Codex、Claude Code、Pi、Reasonix 等 Agent 中的全局发现状态。
- 配置 Espressif 官方文档 MCP 和组件注册表 MCP，让多个 AI 客户端共享官方资料入口。

当前仓库已经自动化了工程脚手架、配置校验、构建、文档、固件打包和跨 Agent 安装。由需求规格自动选择外围器件、解决引脚冲突并生成完整业务代码仍属于后续路线，不应视为现有能力。详见[自动化路线图](references/automation-roadmap.md)。

## 快速开始

### 1. 安装 Skill

需要 Git、Python 3 和 Node.js/npm。首次安装建议将仓库放到跨 Agent 技能的规范目录：

```bash
git clone https://github.com/ashllll/manage-xiao-esp32-projects.git \
  "$HOME/.agents/skills/manage-xiao-esp32-projects"
cd "$HOME/.agents/skills/manage-xiao-esp32-projects"

npx --yes skills add "$PWD" \
  --global \
  --agent '*' \
  --skill manage-xiao-esp32-projects \
  --yes
```

如果已经安装，请在该目录执行 `git pull --ff-only` 更新，不要重复克隆。安装后可运行审计：

```bash
python3 scripts/validate_cross_agent_skill.py
npx --yes skills list --global --json
```

不同 Agent 的调用语法略有区别：

- Codex：`$manage-xiao-esp32-projects`
- Claude Code：`/manage-xiao-esp32-projects`
- 其他支持 Agent Skills 开放格式的客户端：在技能列表中选择 `manage-xiao-esp32-projects`

完整说明见[跨 Agent Skill 安装指南](references/cross-agent-skills.md)。

### 2. 创建 XIAO ESP32S3 工程

以下命令会创建工程、应用 S3 默认配置，并初始化 Git：

```bash
cd "$HOME/.agents/skills/manage-xiao-esp32-projects"

python3 scripts/bootstrap_project.py \
  "$HOME/code/esp/my-xiao-s3-project" \
  --name my-xiao-s3-project \
  --board s3 \
  --init-git
```

目标目录必须为空或尚不存在。脚手架不会覆盖已有项目。

生成的工程包含：

```text
my-xiao-s3-project/
├── src/                    # ESP-IDF 应用代码
├── include/                # 公共头文件
├── components/             # 项目级 ESP-IDF 组件
├── docs/                   # MkDocs 文档
├── scripts/                # 验证、打包和真机检查工具
├── tests/                  # 测试目录
├── platformio.ini          # C3/S3/C6 构建环境
└── mkdocs.yml              # Material 文档配置
```

### 3. 验证工程

轻量结构检查：

```bash
python3 scripts/validate_project.py "$HOME/code/esp/my-xiao-s3-project"
```

完整构建三个开发板环境和文档站：

```bash
python3 scripts/validate_project.py \
  "$HOME/code/esp/my-xiao-s3-project" \
  --build \
  --docs
```

也可以进入工程直接运行：

```bash
cd "$HOME/code/esp/my-xiao-s3-project"

pio run -e xiao_esp32c3
pio run -e xiao_esp32s3
pio run -e xiao_esp32c6

python3 -m pip install -r requirements-docs.txt
python3 -m mkdocs build --strict
```

## 在 AI Agent 中怎么用

安装后可以直接描述目标，不必先手动拼装完整流程。例如：

```text
使用 $manage-xiao-esp32-projects，为 XIAO ESP32S3 创建一个温湿度采集项目，
使用 ESP-IDF，生成 PlatformIO 工程和 MkDocs 文档；先确认传感器型号、供电、
总线和引脚约束，再写代码。
```

```text
使用 $manage-xiao-esp32-projects，检查当前工程的 S3 USB Serial/JTAG、
Octal PSRAM 和分区配置，构建固件并生成交付清单，但不要烧录开发板。
```

```text
使用 $manage-xiao-esp32-projects，把这个已有 ESP32 工程迁移到统一模板，
保留现有代码和 Git 历史，并补齐官方资料索引、引脚说明和文档构建。
```

Skill 会先确认开发板、外围器件、电气约束、引脚占用和预期交付物。涉及烧录、串口监视或修改现有工程时，应明确授权和目标设备。

## Espressif 官方 MCP

仓库内置跨客户端配置脚本，支持以下官方服务：

| 服务 | 地址 | 用途 |
| --- | --- | --- |
| Espressif Documentation | `https://mcp.espressif.com/docs` | 检索 ESP-IDF、芯片和官方开发文档；需要 OAuth |
| ESP Component Registry | `https://components.espressif.com/mcp` | 检索官方组件注册表 |

先预览将要修改的客户端配置：

```bash
python3 scripts/configure_mcp_clients.py
```

确认后再写入配置：

```bash
python3 scripts/configure_mcp_clients.py --apply
```

脚本支持 Codex、Claude Code、OpenCode、VS Code、LM Studio 和 Reasonix，并在修改已有配置前创建备份。OAuth 授权通常需要在每个客户端首次连接时分别完成。详情见[跨 Agent MCP 指南](references/cross-agent-mcp.md)。

## 固件与真机验证

在生成的工程中打包固件：

```bash
cd "$HOME/code/esp/my-xiao-s3-project"
python3 scripts/package_firmware.py --environment xiao_esp32s3
```

真机校验器默认只读取串口，不会自动烧录：

```bash
python3 scripts/verify_hardware.py \
  --environment xiao_esp32s3 \
  --port /dev/cu.usbmodemXXXX
```

只有明确需要覆盖开发板固件时才增加 `--flash`。成功标准包括：发现 READY 标记、连续 heartbeat 满足阈值、heartbeat 编号严格递增且设备未重复重启。

## 本地资料库

工程可选接入本地 XIAO ESP32 资料库：

```bash
export XIAO_ESP32_REFERENCE_ROOT="$HOME/ESP32_资料整理"
export XIAO_ESP32_PROJECT_ROOT="$HOME/code/esp/xiao_esp32"
```

两项环境变量都有默认值。没有本地资料库时，固件构建、文档构建和 Skill 使用仍应正常工作；公开仓库仅保存经过审核的索引和官方来源链接，不提交大体积资料副本。

## 仓库结构

```text
manage-xiao-esp32-projects/
├── SKILL.md                         # Agent 执行入口与工作流
├── agents/openai.yaml               # Agent 元数据
├── assets/project-template/         # 可直接生成的工程模板
├── references/                      # 工作流、MCP、跨 Agent 与路线图说明
├── scripts/bootstrap_project.py     # 创建新工程
├── scripts/validate_project.py      # 校验生成工程
├── scripts/configure_mcp_clients.py # 配置官方 MCP
├── scripts/validate_cross_agent_skill.py
└── scripts/validate_skill.py        # 校验 Skill 包本身
```

进一步阅读：

- [完整工程工作流](references/workflow.md)
- [跨 Agent Skill 安装](references/cross-agent-skills.md)
- [跨 Agent MCP 配置](references/cross-agent-mcp.md)
- [自动化路线图](references/automation-roadmap.md)
- [开发板能力与配置差异](references/board-capabilities.md)
- [版本维护与升级策略](references/maintenance.md)

## 开发与校验

提交修改前至少运行：

```bash
python3 scripts/validate_skill.py
python3 scripts/validate_project.py assets/project-template
```

如果本机已经安装 PlatformIO 和文档依赖，再执行完整模板构建：

```bash
python3 scripts/validate_project.py assets/project-template --build --docs
```

CI 会检查 Skill 格式、模板结构和脚手架文件清单，运行模板测试，并构建 C3、S3、C6 固件、交付包和 MkDocs 文档。

## 安全原则

- 不提交 Wi-Fi 密码、Token、私钥、串口日志中的敏感信息或个人绝对路径。
- 不自动覆盖非空工程目录。
- 不自动烧录开发板；写入硬件必须显式使用 `--flash`。
- 引脚和电气参数以对应开发板、扩展板及外围器件的官方资料为准。
- 自动生成内容不能替代对供电、电平、启动绑带引脚和总线冲突的人工复核。

## License

本项目采用 [Apache License 2.0](LICENSE)。Seeed Studio、Espressif、PlatformIO 和 MkDocs 等名称及资料归其各自权利人所有。
