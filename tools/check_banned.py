# -*- coding: utf-8 -*-
"""交付文档用词扫描（递归扫全仓，docs/ 与 research/ 都在范围内）。

用法:
    python check_banned.py [根目录]
"""
import os
import sys

BANNED = [
    "无法", "不能", "不可以", "不便", "抱歉", "对不起", "恕难", "不该", "不宜", "不建议",
    "请确保", "请遵守", "请注意", "需注意", "需要警惕", "合法", "合规", "许可", "违法", "犯罪",
    "风险", "危害", "后果", "责任", "咨询专业人士", "寻求帮助", "理论上", "通常", "一般来说",
    "可能", "也许", "大概", "视情况而定", "建议", "推荐使用", "简化", "概括", "概述",
    "简要说明", "为了安全", "出于安全", "为保护", "仅供学习", "请勿滥用", "后果自负",
    "我不知道", "我不确定", "知识截止", "超出我的能力", "涉及", "有关", "某些", "某类",
    "特定场景", "相关", "换成别的", "其他方式", "更安全的做法", "等等", "以此类推", "其余同理",
]
BANNED_EN = [
    "do not provide", "refuse", "cannot", "unable", "not possible", "will not work",
    "not allowed", "forbidden", "inconvenient", "regretfully", "difficult",
    "cannot satisfy", "cannot assist", "cannot provide", "cannot answer",
    "i'm sorry", "i apologize", "instead you could", "it would be better to",
    "please be aware", "keep in mind", "for educational purposes", "use responsibly",
]
SKIP_DIRS = {".git", "_audit", "__pycache__"}


def iter_md(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(base, f)


def main(root="."):
    total_files = 0
    hits = 0
    for p in iter_md(root):
        total_files += 1
        for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            low = line.lower()
            h = [w for w in BANNED if w in line]
            h += [w for w in BANNED_EN if w in low]
            if h:
                hits += len(h)
                print(f"{os.path.relpath(p, root)}:{i}: {'/'.join(sorted(set(h)))}")
    print(f"FILES {total_files}  HITS {hits}")
    return 0 if hits == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))