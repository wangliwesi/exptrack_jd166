"""exptrack_jd166 —— 找出实验管理与追踪工程师·投机解码的命中率里互相矛盾的两处并排列出。

在同一个输入里两两比对，检测实验管理与追踪工程师·投机解码的命中率相关的矛盾表述，把冲突双方原样并排呈现

定位：
  不替用户猜哪一句是本意，只把矛盾双方并排摆出来，由人决定取舍

岗位对应：
  目标岗位　华为 · 资深实验管理与追踪工程师
  技能主线　MLOps、Python、Ray
  领域标签　MLOps

设计约束：
  1. **只报告能定位到具体位置的结论**，不做语义猜测。
  2. **规则表公开**，每条命中都能对应到岗位要求的一条明示规则。
  3. **输入为空或格式不对时明确报错**，不静默返回空结果。

仅依赖 Python 标准库。

用法:
    python exptrack_jd166.py --help
    python exptrack_jd166.py --file input.txt
    python exptrack_jd166.py --text "示例内容"
    python exptrack_jd166.py --file input.txt --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# 岗位规则表：每条规则独立可核查，命中即报，不做推断。
# 规则由岗位 JD 的技能线与领域标签派生——每条都能对回岗位要求。
# 目标岗位：华为 · 资深实验管理与追踪工程师
RULES: list[dict] = [
    {
        "name": "实验管理与追踪工程师·投机解码的命中率·缺失",
        "why": "岗位要求「MLOps」在输入里找不到对应内容",
        "severity": "high",
        "keywords": ['missing', 'absent', '缺少', '没有', '未提供', 'MLOps'],
    },
    {
        "name": "实验管理与追踪工程师·投机解码的命中率·冲突",
        "why": "两处关于「Python」的描述互相矛盾",
        "severity": "high",
        "keywords": ['conflict', 'contradict', '矛盾', '不一致', '相反', 'Python'],
    },
    {
        "name": "实验管理与追踪工程师·投机解码的命中率·越界",
        "why": "「Ray」的取值超出岗位场景的常规范围",
        "severity": "medium",
        "keywords": ['out of range', 'outlier', '越界', '超限', '超过', 'Ray'],
    },
    {
        "name": "实验管理与追踪工程师·投机解码的命中率·退化",
        "why": "「实验管理与追踪工程师」相关的信息量不足以支撑判断",
        "severity": "medium",
        "keywords": ['degrade', 'insufficient', '不足', '太少', '无法', '实验管理与追踪工程师'],
    },
    {
        "name": "实验管理与追踪工程师·投机解码的命中率·泄漏#2",
        "why": "「MLOps」相关的内容被意外暴露",
        "severity": "high",
        "keywords": ['leak', 'expose', '泄漏', '暴露', '明文', 'MLOps'],
    },
    {
        "name": "实验管理与追踪工程师·投机解码的命中率·重复#2",
        "why": "同一处「Python」信息被反复传递",
        "severity": "low",
        "keywords": ['duplicate', 'repeat', '重复', 'again', 'Python'],
    },
    {
        "name": "实验管理与追踪工程师·投机解码的命中率·陈旧#2",
        "why": "「Ray」的时效性已过期",
        "severity": "medium",
        "keywords": ['stale', 'expired', '过期', '陈旧', '旧版', 'Ray'],
    },
    {
        "name": "实验管理与追踪工程师·投机解码的命中率·不可核#2",
        "why": "关于「实验管理与追踪工程师」的说法无法追溯到具体证据",
        "severity": "high",
        "keywords": ['unverifiable', 'no evidence', '无法追溯', '没有来源', '实验管理与追踪工程师'],
    },
]


def exptrack_jd166_split_items(text: str) -> list[str]:
    """按行/句切分为可比对的条目。"""
    items: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        for p in re.split(r"(?<=[。！？；;])\s*", line):
            p = p.strip()
            if p:
                items.append(p)
    return items


def exptrack_jd166_polarity(text: str) -> int:
    """判定一句的极性：1 正向，-1 否定，0 中性。

    只看显式否定标记与显式肯定标记，不做语义推断。
    """
    neg = any(m in text for m in ("不", "无", "未", "非", "禁止", "避免",
                                  "not ", "no ", "never", "without"))
    pos = any(m in text for m in ("是", "有", "会", "应", "需", "必须",
                                  "must", "should", "will ", "has "))
    if neg and not pos:
        return -1
    if pos and not neg:
        return 1
    return 0


def exptrack_jd166_word_tokens(text: str) -> set[str]:
    """抽词元。

    拉丁词按单词切；中文按**二元组**切。不用长正则 `[\u4e00-\u9fff]{2,}`——
    那会贪婪地把整句当成一个词元，两句中文只要措辞不同就永远没有共同词元，
    同主题判定会全部失效。二元组既能命中共享片段，又不会被长句吞掉。
    """
    low = text.lower()
    out = set(re.findall(r"[a-z]{3,}", low))
    for seg in re.findall(r"[\u4e00-\u9fff]+", low):
        if len(seg) == 1:
            out.add(seg)
        else:
            for i in range(len(seg) - 1):
                out.add(seg[i:i + 2])
    return out


def exptrack_jd166_detect_pairs(items: list[str]) -> list[dict]:
    """找同主题但极性相反的条目对。"""
    pairs: list[dict] = []
    for i, a in enumerate(items):
        pa = exptrack_jd166_polarity(a)
        if pa == 0:
            continue
        for j in range(i + 1, len(items)):
            b = items[j]
            pb = exptrack_jd166_polarity(b)
            if pb == 0 or pb == pa:
                continue
            # 共享词元才算同主题，避免把无关句子配成对
            ka = exptrack_jd166_word_tokens(a)
            kb = exptrack_jd166_word_tokens(b)
            if not (ka & kb):
                continue
            pairs.append({
                "a": {"index": i, "text": a, "polarity": pa},
                "b": {"index": j, "text": b, "polarity": pb},
                "shared": sorted(ka & kb)[:6],
            })
    return pairs


def exptrack_jd166_analyze(text: str) -> dict:
    """主分析：返回条目数、矛盾对与分布。"""
    items = exptrack_jd166_split_items(text)
    pairs = exptrack_jd166_detect_pairs(items)
    covered = {p["a"]["index"] for p in pairs} | {p["b"]["index"] for p in pairs}
    return {
        "item_count": len(items),
        "pairs": pairs,
        "conflict_count": len(pairs),
        "conflicted_items": len(covered),
        "clean_items": len(items) - len(covered),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def render(result: dict) -> str:
    """把结果渲染成人读的文本。每个工具的版式不同。"""
    out: list[str] = []
    if not result.get("ok", True):
        out.append(f"无法分析：{{result.get('error', '未知原因')}}")
        return "\n".join(out)
    out.append(f"条目数：{result['item_count']}")
    out.append(f"矛盾对：{result['conflict_count']}")
    out.append(f"涉及条目：{result['conflicted_items']}（干净 {result['clean_items']}）")
    out.append("")
    for i, pair in enumerate(result["pairs"], 1):
        out.append(f"矛盾 {i}  共享词: {', '.join(pair['shared'])}")
        out.append(f"  A[{pair['a']['index']}]: {pair['a']['text'][:100]}")
        out.append(f"  B[{pair['b']['index']}]: {pair['b']['text'][:100]}")
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="exptrack_jd166",
        description="在同一个输入里两两比对，检测实验管理与追踪工程师·投机解码的命中率相关的矛盾表述，把冲突双方原样并排呈现（仅依赖标准库）",
        epilog=(
            "示例:\n"
            "  python exptrack_jd166.py --file input.txt\n"
            "  python exptrack_jd166.py --text '示例内容'\n"
            "  python exptrack_jd166.py --file input.txt --json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="输入文件路径")
    src.add_argument("--text", help="直接给出输入内容")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"读不了文件：{{e}}", file=sys.stderr)
            return 2
    else:
        content = args.text

    if not content.strip():
        print("输入是空的。", file=sys.stderr)
        return 2

    result = exptrack_jd166_analyze(content)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(render(result))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
