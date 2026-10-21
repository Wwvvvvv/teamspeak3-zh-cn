#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge new Chinese translations into the work/*.ts sources and recompile.

Sources: ref-zh (upstream community translation) + tr-lagos-*.json / tr-permissions.json
"""
import json
import os
import re
import subprocess
import sys
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(BASE, "work")
DIST = os.path.join(BASE, "dist")
UPSTREAM = os.path.join(BASE, "upstream")
TRANSLATIONS = os.path.join(BASE, "translations")
LRELEASE = os.environ.get("LRELEASE", "lrelease")
LCONVERT = os.environ.get("LCONVERT", "lconvert")

TARGETS = ["lagos", "permissions", "qt", "ts_core_errors",
           "error_report", "package_installer", "update"]


def load_translations():
    """key -> chinese, where key is 'context||source'."""
    trans = {}
    for i in range(1, 10):
        p = os.path.join(TRANSLATIONS, f"tr-lagos-{i}.json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            trans.update(json.load(f))
    with open(os.path.join(TRANSLATIONS, "tr-permissions.json"), encoding="utf-8") as f:
        for ident, text in json.load(f).items():
            trans[f"PermI18n||{ident}"] = text
    return trans


def escape_xml(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def merge_message(msg, trans, key, numerus):
    """Return the replacement XML block for one <message>, or None if untouched."""
    chunk = msg
    m = re.search(r"<translation([^>]*)>(.*?)</translation>", chunk, re.S)
    if not m:
        return None
    body = m.group(2).strip()
    if numerus and "<numerusform></numerusform>" in body.replace(" ", ""):
        if key not in trans:
            return None
        text = escape_xml(trans[key])
        new = f"<translation><numerusform>{text}</numerusform></translation>"
        return chunk[:m.start()] + new + chunk[m.end():]
    if body and "numerusform" not in body:
        # already translated: keep, but drop an unfinished marker if present
        if 'type="unfinished"' in chunk:
            return chunk.replace(' type="unfinished"', "")
        return None
    if key not in trans:
        return None
    text = escape_xml(trans[key])
    new = f"<translation>{text}</translation>"
    return chunk[:m.start()] + new + chunk[m.end():]


def merge_file(name, trans):
    path = os.path.join(WORK, f"{name}_zh.ts")
    with open(path, encoding="utf-8") as f:
        xml = f.read()

    # strip a stale xml declaration/doctype mismatch by working on raw text
    pattern = re.compile(
        r"<message([^>]*)>\s*<source>(.*?)</source>(.*?)</message>", re.S)
    ctx_spans = [(m.start(), m.group(1)) for m in
                 re.finditer(r"<context>\s*<name>(.*?)</name>", xml)]
    ctx_spans = [m.group(1) for m in
                 re.finditer(r"<context>\s*<name>(.*?)</name>", xml)]

    out = []
    pos = 0
    ctx_i = -1
    applied = 0
    missing = []

    def unescape(s):
        return (s.replace("&lt;", "<").replace("&gt;", ">")
                 .replace("&quot;", '"').replace("&apos;", "'")
                 .replace("&amp;", "&"))

    for m in re.finditer(r"<context>.*?</context>", xml, re.S):
        ctx = re.search(r"<name>(.*?)</name>", m.group(0), re.S).group(1)
        block = m.group(0)
        new_block = block
        for mm in reversed(list(re.finditer(
                r"<message([^>]*)>\s*<source>(.*?)</source>(.*?)</message>",
                block, re.S))):
            # applied below
            raw = mm.group(0)
            src = unescape(mm.group(2))
            key = f"{ctx}||{src}"
            numerus = 'numerus="yes"' in mm.group(1)
            repl = merge_message(raw, trans, key, numerus)
            if repl is not None and repl != raw:
                new_block = (new_block[:mm.start()] + repl +
                             new_block[mm.end():])
                applied += 1
            # report what is still empty
            tm = re.search(r"<translation([^>]*)>(.*?)</translation>", raw, re.S)
            txt = re.sub(r"<[^>]+>", "", tm.group(2)).strip() if tm else ""
            if not txt and 'type="unfinished"' not in raw:
                missing.append(key)
        out.append(xml[pos:m.start()])
        out.append(new_block)
        pos = m.end()
    out.append(xml[pos:])
    xml = "".join(out)

    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    return applied, missing


def strip_unfinished(name):
    """Drop type="unfinished" markers from entries that already carry text."""
    path = os.path.join(WORK, f"{name}_zh.ts")
    with open(path, encoding="utf-8") as f:
        xml = f.read()

    def on_message(m):
        raw = m.group(0)
        if 'type="unfinished"' not in raw:
            return raw
        tr = re.search(r"<translation([^>]*)>(.*?)</translation>", raw, re.S)
        if tr is None:
            return raw
        inner = tr.group(2)
        text = re.sub(r"<numerusform>\s*</numerusform>", "", inner)
        text = re.sub(r"<[^>]+>", "", text).strip()
        if inner.count("<numerusform>") and not text:
            return raw
        return raw.replace(' type="unfinished"', "")

    xml2 = re.sub(r"<message[^>]*>.*?</message>", on_message, xml, flags=re.S)
    if xml2 != xml:
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml2)


def numerus_fix(name):
    """Give every numerus <translation> a <numerusform> (Chinese has one form)."""
    path = os.path.join(WORK, f"{name}_zh.ts")
    with open(path, encoding="utf-8") as f:
        xml = f.read()

    def fix_block(block):
        def repl(m):
            attrs, body = m.group(1), m.group(2)
            if "numerusform" in body or not body.strip():
                return m.group(0)
            return (f"<translation{attrs}><numerusform>{body.strip()}"
                    f"</numerusform></translation>")
        return re.sub(r"<translation([^>]*)>(.*?)</translation>", repl, block, flags=re.S)

    def on_message(m):
        if 'numerus="yes"' in m.group(1):
            return fix_block(m.group(0))
        return m.group(0)

    xml2 = re.sub(r"<message([^>]*)>.*?</message>", on_message, xml, flags=re.S)
    if xml2 != xml:
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml2)
    return xml2 != xml


def reset_work():
    """Always start from the pristine upstream sources so builds are reproducible."""
    import shutil
    os.makedirs(WORK, exist_ok=True)
    for name in TARGETS:
        src = os.path.join(UPSTREAM, f"{name}_zh.ts")
        dst = os.path.join(WORK, f"{name}_zh.ts")
        shutil.copyfile(src, dst)


def main():
    reset_work()
    trans = load_translations()
    print(f"loaded {len(trans)} new translations")
    total_missing = []
    for name in TARGETS:
        applied, missing = merge_file(name, trans)
        fixed = numerus_fix(name)
        strip_unfinished(name)
        print(f"{name}: applied={applied} numerus_fixed={fixed} still_empty={len(missing)}")
        total_missing += missing

    if total_missing:
        print("\nSTILL MISSING:")
        for k in total_missing:
            print("  ", k)

    os.makedirs(DIST, exist_ok=True)
    qms = []
    for name in TARGETS:
        src = os.path.join(WORK, f"{name}_zh.ts")
        qm = os.path.join(DIST, f"{name}_zh.qm")
        r = subprocess.run([LRELEASE, src, "-qm", qm],
                           capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())
        if r.returncode != 0:
            sys.exit(f"lrelease failed for {name}")
        qms.append(f"{name}_zh.qm")

    # verify every qm round-trips with a sane entry count
    for q in qms:
        ts = os.path.join("/tmp", q.replace(".qm", ".roundtrip.ts"))
        subprocess.run([LCONVERT, "-i", os.path.join(DIST, q), "-o", ts], check=True)
        with open(ts, encoding="utf-8") as f:
            n = f.read().count("<source>")
        print(f"{q}: {n} messages in qm")

    # package as .ts3_translation
    pkg_ini = "\n".join([
        "Name = TeamSpeak 3 简体中文语言包",
        "Type = Translation",
        "Author = 寂听 & EdisonJwa (社区翻译), 补全翻译: Claude",
        "Version = 3.6.2",
        "Platforms = ",
        "Description = 基于 https://github.com/jitingcn/TS3-Translation_zh-CN 补全",
    ])
    ini_path = os.path.join(DIST, "package.ini")
    with open(ini_path, "w", encoding="utf-8") as f:
        f.write(pkg_ini)
    out = os.path.join(DIST, "Chinese_Translation_zh-CN.ts3_translation")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(ini_path, "package.ini")
        for q in qms:
            z.write(os.path.join(DIST, q), f"translations/{q}")
    print(f"\npackage: {out}")


if __name__ == "__main__":
    main()
