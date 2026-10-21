# 来源与许可说明

本项目的**大部分翻译文本并非原创**，开源前请仔细阅读本节。

## 翻译文本来源

| 来源 | 占比 | 许可状态 |
|------|------|----------|
| [jitingcn/TS3-Translation_zh-CN](https://github.com/jitingcn/TS3-Translation_zh-CN) | 约 87%（3328 / 3428 条主界面 + 498 条权限中的 229 条） | **仓库未附带 LICENSE 文件** |
| 本项目补译（`translations/*.json`） | 主界面 416 条 + 权限说明 269 条 | 由本项目贡献者提供 |

上游仓库 `jitingcn/TS3-Translation_zh-CN` 在公开页面上**没有** LICENSE / COPYING 文件，
GitHub API 返回的 `license` 字段为 `null`。这意味着在法律意义上它属于"保留所有权利"，
而不是 GPL/MIT 等自由许可。

因此：

- 本项目**不能**单方面为上游译文套用 MIT/Apache 等许可证。
- `LICENSE-TEXT.md` 中的 CC BY-SA 4.0 仅适用于**本项目新增的补译部分**与脚本代码。
- 若要使用、分发或商用上游译文部分，**应先联系上游作者取得授权**（上游 README 留有 Telegram 群组）。
- 如果你只是在自己的机器上安装使用，正常使用不受影响。

> 说明：本项目最初是在本地评估时误以为上游为 GPL 仓库，检查后确认上游并没有 LICENSE 文件，
> 故在此明确更正。若上游后续补充了许可证，请以对方为准。

## 脚本与构建工具

`build.py`、`install.sh`、`portable/安装中文.command` 为本项目原创，采用 MIT 许可证（见 `LICENSE`）。

## TeamSpeak 商标

TeamSpeak 是 TeamSpeak Systems GmbH 的商标。本项目为社区非官方项目，
与 TeamSpeak Systems GmbH 无任何关联，也未获得其背书。

本项目**不包含** TeamSpeak 客户端的任何二进制文件或原始英文词条，
仅包含社区翻译文本与 Qt `.qm` 编译产物。

## Qt 工具链

构建依赖 Qt Linguist 工具（`lrelease` / `lconvert`）。这些工具由 Qt 项目提供，
遵循 LGPLv3 / GPLv3 等许可，本项目仅以命令行方式调用，不修改也不分发它们。
