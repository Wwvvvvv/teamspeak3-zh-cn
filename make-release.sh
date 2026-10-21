#!/bin/bash
# 生成可分发到其他 Mac 的便携包 zip
# 用法: bash make-release.sh
set -euo pipefail

cd "$(dirname "$0")"
[ -d dist ] || { echo "请先运行 python3 build.py" >&2; exit 1; }

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/TeamSpeak3-中文语言包/translations"
cp dist/*_zh.qm "$STAGE/TeamSpeak3-中文语言包/translations/"
cp dist/*.ts3_translation "$STAGE/TeamSpeak3-中文语言包/" 2>/dev/null || true
cp portable/安装中文.command "$STAGE/TeamSpeak3-中文语言包/"
cp LICENSE NOTICE.md "$STAGE/TeamSpeak3-中文语言包/"
chmod +x "$STAGE/TeamSpeak3-中文语言包/安装中文.command"

OUT="TeamSpeak3-中文语言包.zip"
rm -f "$OUT"
(cd "$STAGE" && ditto -c -k --sequesterRsrc "TeamSpeak3-中文语言包" "$OLDPWD/$OUT")

echo "生成: $PWD/$OUT ($(du -h "$OUT" | cut -f1))"
unzip -l "$OUT"
