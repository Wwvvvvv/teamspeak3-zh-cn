#!/bin/bash
# TeamSpeak 3 简体中文语言包 —— 一键安装 (macOS)
#
# 客户端会优先读取 ~/Library/Application Support/TeamSpeak 3/translations/，
# 所以不需要管理员权限，也不会修改 /Applications 里的 app 包。
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)/dist"
SUPPORT="$HOME/Library/Application Support/TeamSpeak 3"
DST="$SUPPORT/translations"
DB="$SUPPORT/settings.db"
PROC="TeamSpeak 3 Client.app/Contents/MacOS/ts3client_mac"

if [ ! -d "/Applications/TeamSpeak 3 Client.app" ] \
   && [ ! -d "$HOME/Applications/TeamSpeak 3 Client.app" ]; then
  echo "未找到 TeamSpeak 3 Client。" >&2
  echo "请先安装 TeamSpeak 3（本语言包不适用于 TeamSpeak 6）。" >&2
  exit 1
fi

if pgrep -f "$PROC" >/dev/null; then
  echo "TeamSpeak 3 正在运行，请先完全退出客户端再执行本脚本。" >&2
  echo "（菜单栏 TeamSpeak 3 → 退出，而不是只关闭窗口）" >&2
  exit 1
fi

if [ ! -f "$DB" ]; then
  echo "未找到配置文件 settings.db。" >&2
  echo "请先启动一次 TeamSpeak 3 并完全退出（首次启动才会生成配置），然后重试。" >&2
  exit 1
fi

if [ ! -d "$SRC" ]; then
  echo "未找到 dist/ 目录。请先在仓库根目录运行 python3 build.py 生成语言文件。" >&2
  exit 1
fi

echo "→ 复制语言文件到 $DST"
mkdir -p "$DST"
cp "$SRC"/*_zh.qm "$DST"/

echo "→ 设置语言为 zh_CN"
sqlite3 "$DB" "insert or replace into Application(timestamp,key,value) \
  values(strftime('%s','now'),'Language','zh_CN');"

echo
echo "✅ 安装完成"
ls -1 "$DST" | grep _zh.qm | sed 's/^/   /'
echo "   Language=$(sqlite3 "$DB" "select value from Application where key='Language';")"
echo
echo "重新打开 TeamSpeak 3 即为中文。"
echo "注意：不要在设置界面里把语言改成“英语/系统默认”，否则需重跑本脚本。"
