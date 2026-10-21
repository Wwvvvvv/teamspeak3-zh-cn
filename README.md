# TeamSpeak 3 简体中文语言包（macOS）

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

给 **TeamSpeak 3 Client 3.6.2 (macOS)** 用的完整简体中文语言包，附一键安装脚本。

- 全部 **3428 条主界面文本**、**498 条权限说明**、1414 条 Qt 控件、190 条错误码均已翻译，无未完成条目
- **不需要管理员密码**，不修改 `/Applications` 里的 app 包
- 双击安装，或一行命令

> ⚠️ 仅适用于 **TeamSpeak 3**。TeamSpeak 6（新版 Electron 客户端）架构完全不同，无法使用。
>
> ⚠️ 分发前请先读 [NOTICE.md](NOTICE.md)：约 87% 译文来自社区项目，该上游仓库**没有 LICENSE 文件**。

## 快速安装

```bash
git clone https://github.com/Wwvvvvv/teamspeak3-zh-cn.git
cd teamspeak3-zh-cn
bash install.sh
```

或者下载 [Release](../../releases) 里的 `TeamSpeak3-zh-CN.zip`，解压后双击 `安装中文.command`
（首次可能需要在文件上右键 → 打开，或在“系统设置 → 隐私与安全性”里放行）。

安装脚本做两件事：

1. 把 7 个 `*_zh.qm` 复制到 `~/Library/Application Support/TeamSpeak 3/translations/`
2. 在 `settings.db` 中写入 `Language = zh_CN`

装完重新打开 TeamSpeak 3 即可。

## 三个容易踩的坑

这三点在官方文档里都查不到，是实际调试得出的：

**1. 语言文件放用户目录就行，不用改 app 包**

客户端会读取 `~/Library/Application Support/TeamSpeak 3/translations/`，并且优先级高于
`/Applications/TeamSpeak 3 Client.app/Contents/SharedSupport/translations/`。
后一个位置在 macOS 上受 App 管理保护，**即使 root 也无法写入**（会报 `Operation not permitted`）。
老教程让你用 sudo 往 app 包里拷文件，在较新的 macOS 上会失败。

**2. 语言代码是 `zh_CN`，不是 `zh`**

设成 `zh` 时客户端完全不会加载中文，界面保持英文。

**3. 设置界面里没有“中文”选项，这是正常的**

语言下拉列表在编译期就固定为官方自带的 8 种（English + de/es/fr/ja/pl/pt/ru），
新增 `lagos_zh.qm` 不会自动生成下拉项。必须直接写配置：

```bash
sqlite3 ~/Library/Application\ Support/TeamSpeak\ 3/settings.db \
  "insert or replace into Application(timestamp,key,value) \
   values(strftime('%s','now'),'Language','zh_CN');"
```

之后不要在设置界面里改语言为“英语/系统默认”，否则会被覆盖，重跑一次 `install.sh` 即可。

## 手动安装

```bash
DST="$HOME/Library/Application Support/TeamSpeak 3/translations"
mkdir -p "$DST"
cp dist/*_zh.qm "$DST"/
sqlite3 "$HOME/Library/Application Support/TeamSpeak 3/settings.db" \
  "insert or replace into Application(timestamp,key,value) \
   values(strftime('%s','now'),'Language','zh_CN');"
```

## 语言包内容

| 文件 | 词条数 | 说明 |
|------|--------|------|
| `lagos_zh.qm` | 3428 | 主界面 |
| `permissions_zh.qm` | 498 | 权限名称与说明 |
| `qt_zh.qm` | 1414 | Qt 内置控件（对话框按钮、文件选择器等） |
| `ts_core_errors_zh.qm` | 190 | 核心错误码 |
| `error_report_zh.qm` | 5 | 错误上报窗口 |
| `package_installer_zh.qm` | 28 | 插件安装器 |
| `update_zh.qm` | 28 | 更新程序 |

## 从源码构建

依赖 Qt 的 `lrelease` / `lconvert`：

```bash
brew install qt

# 如果工具不在 PATH 里
export LRELEASE=/opt/homebrew/opt/qt/bin/lrelease
export LCONVERT=/opt/homebrew/opt/qt/bin/lconvert

python3 build.py
```

产物在 `dist/`，同时会打包成 `dist/Chinese_Translation_zh-CN.ts3_translation`。
构建每次都从 `upstream/` 的原始上游文件重建，可重复执行。

### 目录结构

```
upstream/     上游原始 .ts 源文件（未经修改，用于对照 diff）
translations/ 本项目补译内容（JSON，context||source -> 中文）
dist/         编译产物 *.qm 与 .ts3_translation
portable/     给另一台 Mac 用的便携包（含双击安装脚本）
build.py      合并 + 编译 + 校验 + 打包
install.sh    本机一键安装
```

### 修改翻译

译文是 JSON，key 格式为 `上下文||原文`，例如：

```json
"MainWindow||Visit the TeamSpeak webpage at www.teamspeak.com": "访问 TeamSpeak 网站：www.teamspeak.com"
```

改完跑 `python3 build.py` 重新生成。要补译上游还没覆盖的词条，
先从 `upstream/` 里找到对应的 `<source>`，再按同样格式加进 `translations/tr-lagos-N.json`。

## 致谢

- [jitingcn/TS3-Translation_zh-CN](https://github.com/jitingcn/TS3-Translation_zh-CN) — 提供了约 87% 的基础译文
- [AceSheep](https://blog.acesheep.com/p/teamspeak-3-simplified-chinese-translation/) — 早期中文社区的翻译与踩坑记录

## 免责声明

非官方项目，与 TeamSpeak Systems GmbH 无关联。TeamSpeak 是其注册商标。
