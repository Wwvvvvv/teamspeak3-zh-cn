#!/bin/bash
# TeamSpeak 3 简体中文语言包 —— 双击运行即可，无需管理员密码
# 适用：macOS 上的 TeamSpeak 3 Client (3.6.x)

cd "$(dirname "$0")" || exit 1
# 语言文件优先取便携包自带的 translations/，否则回退到仓库的 dist/
if [ -d "translations" ]; then
  SRC="translations"
elif [ -d "../dist" ]; then
  SRC="../dist"
else
  echo "❌ 找不到语言文件（translations/ 或 ../dist/）。"
  read -n 1 -s -r -p "按任意键退出..."
  exit 1
fi
DST="$HOME/Library/Application Support/TeamSpeak 3/translations"
DB="$HOME/Library/Application Support/TeamSpeak 3/settings.db"

echo "==============================================="
echo " TeamSpeak 3 简体中文语言包"
echo "==============================================="
echo

# 检查客户端是否安装
if [ ! -d "/Applications/TeamSpeak 3 Client.app" ] \
   && [ ! -d "$HOME/Applications/TeamSpeak 3 Client.app" ]; then
  echo "⚠️  没找到 TeamSpeak 3 Client。"
  echo "    请先安装 TeamSpeak 3（本语言包不适用于 TeamSpeak 6）。"
  echo
  read -n 1 -s -r -p "按任意键退出..."
  exit 1
fi

# 正在运行则提示
if pgrep -f "TeamSpeak 3 Client.app/Contents/MacOS/ts3client_mac" >/dev/null; then
  echo "⚠️  TeamSpeak 3 正在运行。"
  read -r -p "    是否现在自动退出客户端？[Y/n] " ans
  if [[ ! "$ans" =~ ^[Nn] ]]; then
    osascript -e 'tell application "TeamSpeak 3" to quit' >/dev/null 2>&1
    sleep 3
    pkill -f "TeamSpeak 3 Client.app/Contents/MacOS/ts3client_mac" 2>/dev/null
  else
    echo "    请先手动退出客户端后再运行本脚本。"
    read -n 1 -s -r -p "按任意键退出..."
    exit 1
  fi
fi

echo "→ 复制语言文件..."
mkdir -p "$DST"
cp "$SRC"/*_zh.qm "$DST"/ || { echo "❌ 复制失败"; read -n 1 -s -r -p "按任意键退出..."; exit 1; }

echo "→ 设置语言为简体中文..."
if [ ! -f "$DB" ]; then
  echo "⚠️  还没找到配置文件 settings.db（客户端可能从未启动过）。"
  echo "    请先打开一次 TeamSpeak 3 并完全退出，然后再运行本脚本。"
  read -n 1 -s -r -p "按任意键退出..."
  exit 1
fi
sqlite3 "$DB" "insert or replace into Application(timestamp,key,value) values(strftime('%s','now'),'Language','zh_CN');" \
  || { echo "❌ 写入配置失败"; read -n 1 -s -r -p "按任意键退出..."; exit 1; }

echo
echo "✅ 安装完成！"
echo "   语言文件: $DST"
echo "   语言设置: $(sqlite3 "$DB" "select value from Application where key='Language';")"
echo
echo "现在打开 TeamSpeak 3 即为中文。"
echo "提示：不要在设置界面里把语言改成“英语/系统默认”，否则需要重新运行本脚本。"
echo
read -n 1 -s -r -p "按任意键退出..."
