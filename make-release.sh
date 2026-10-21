#!/bin/bash
# 生成可分发到其他 Mac 的便携包 zip
# 用法: bash make-release.sh
set -euo pipefail

cd "$(dirname "$0")"
[ -d dist ] || { echo "请先运行 python3 build.py" >&2; exit 1; }

NAME="TeamSpeak3-中文语言包"
OUT="TeamSpeak3-zh-CN.zip"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/$NAME/translations"
cp dist/*_zh.qm "$STAGE/$NAME/translations/"
cp dist/*.ts3_translation "$STAGE/$NAME/" 2>/dev/null || true
cp portable/安装中文.command "$STAGE/$NAME/"
cp LICENSE NOTICE.md "$STAGE/$NAME/"

# 去掉扩展属性（否则 zip 里会混入 __MACOSX/._* 垃圾文件）
xattr -cr "$STAGE/$NAME" 2>/dev/null || true
chmod +x "$STAGE/$NAME/安装中文.command"

rm -f "$OUT"
(cd "$STAGE" && zip -rq -X "$OLDPWD/$OUT" "$NAME" -x "*.DS_Store" "*__MACOSX*")

echo "生成: $PWD/$OUT ($(du -h "$OUT" | cut -f1))"
unzip -l "$OUT"
