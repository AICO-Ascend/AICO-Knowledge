#!/usr/bin/env python3
"""discriminate_audit.py — 机审二阶甄别：把粗判 BAD 分成「合法白名单」vs「真要修」。

一阶 audit_crops.py 是宽进（宁错杀），三类高频误报需要二阶精细判决：
  - multi_element(fig)：一张图含多个面板/(a)(b) 子图但只有 1 个 caption = 合法
    单图；出现 ≥2 个不同 Figure/Table 编号 caption 才是真混入。
  - prose_pollution：混入的是该图/表自己的长 caption（很多论文 caption 就是
    四五行的解释段，合法）还是正文段落/别的元素的 caption（真污染）。
  - prose_only(tab)：附录 prompt 模板表的内容本身就是散文+框线（合法表格）
    vs 行内引用占位裁出来的纯正文（假表）。
  - overlap：原 PDF 排版本身的重叠（裁剪裁不出来重叠）= 白名单；
    渲染管线（matplotlib）产生的重叠才要修。

用法：python3 discriminate_audit.py [--workers 8]
只处理 crop_audit.json 里 ok=False 的条目，结果写回（白名单 ok=true +
note 追加 [whitelisted: ...]；确认要修的 ok=false + note 追加 [confirmed]）。
"""
import json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "extraction"
SKILL = REPO / "skills" / "paper-extraction"
sys.path.insert(0, str(SKILL))
import m3_caption

PROMPTS = {
    "multi_element": """这张论文裁剪图被怀疑混入了多个独立元素。请仔细分辨：
- 若全图只有 1 个 "Figure N"/"Table N" 编号 caption（内容是多面板/(a)(b)子图/多图表并列），这是合法单图 → legit
- 若出现 ≥2 个不同编号的 caption，或混入了标题页/作者/摘要等无关内容 → bad
只输出 JSON：{{"verdict": "legit"或"bad", "reason": "≤30字"}}""",
    "prose_pollution": """这张论文裁剪图被怀疑混入正文散文。请仔细分辨：
- 若多行文字是该图/表自己的完整 caption（很多论文 caption 本身就是多行解释段），属于合法 → legit
- 若混入了正文段落、节标题、脚注、或另一张图/表的 caption → bad
只输出 JSON：{{"verdict": "legit"或"bad", "reason": "≤30字"}}""",
    "prose_only": """这张论文表格裁剪被怀疑是假表（只有散文没有表格）。请仔细分辨：
- 附录的 prompt 模板表/评测协议表，内容本身就是散文段落+框线结构（如 PROMPT/Evaluation 段），这是表格的真实内容 → legit
- 纯正文段落、无框线无表格结构（行内引用占位误裁） → bad
只输出 JSON：{{"verdict": "legit"或"bad", "reason": "≤30字"}}""",
    "overlap": """这张裁剪图里有文字重叠。请判断重叠的形态：
- 原论文排版本身的重叠（紧凑行距/上下标压线/设计如此），全图内容仍完整可读 → legit
- 渲染错误导致的重叠（整段文字糊在一起不可读、豆腐块夹杂） → bad
只输出 JSON：{{"verdict": "legit"或"bad", "reason": "≤30字"}}""",
}


def discriminate(item):
    key, v = item
    path = OUT / key
    issues = [i for i in v["issues"] if i in PROMPTS]
    if not issues:
        return key, v, "skip"
    prompt = PROMPTS[issues[0]]
    try:
        txt = m3_caption.caption(str(path), prompt, max_tokens=8000)
        m = re.search(r"\{.*\}", txt, re.S)
        r = json.loads(m.group(0))
        verdict = r.get("verdict", "bad")
        reason = str(r.get("reason", ""))[:60]
    except Exception as e:
        return key, v, f"error:{e}"
    if verdict == "legit":
        v["ok"] = True
        v["note"] = v.get("note", "") + f" [whitelisted: {reason}]"
        return key, v, "legit"
    v["note"] = v.get("note", "") + f" [confirmed: {reason}]"
    return key, v, "bad"


def main():
    workers = 8
    if "--workers" in sys.argv:
        workers = int(sys.argv[sys.argv.index("--workers") + 1])
    audit_path = OUT / "crop_audit.json"
    audit = json.loads(audit_path.read_text())
    todo = [(k, v) for k, v in audit.items() if v.get("ok") is False
            and "[confirmed" not in v.get("note", "")]
    print(f"to discriminate: {len(todo)}", flush=True)
    counts = {"legit": 0, "bad": 0, "skip": 0, "error": 0}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i, (key, v, res) in enumerate(ex.map(discriminate, todo), 1):
            audit[key] = v
            counts[res.split(":")[0] if res.startswith("error") else res] = \
                counts.get(res.split(":")[0], 0) + 1
            if i % 20 == 0:
                audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=1))
                print(f"  [{i}/{len(todo)}] {time.time()-t0:.0f}s {counts}", flush=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=1))
    bad_left = sum(1 for v in audit.values() if v.get("ok") is False)
    print(f"DONE {counts}, confirmed_bad={bad_left}")


if __name__ == "__main__":
    main()
