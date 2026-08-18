#!/usr/bin/env python3
"""parse_moonlight_bib.py — parse a clean BibTeX export into the source list
sync_from_source.py consumes.

WHY THIS EXISTS (portability / clean-input play)
================================================
The legacy source `archive/paper_source_moonlight.md` is a *web-page capture*
from Moonlight: it carries base64 images, column drift (date↔abstract swapped),
and — worst of all — **truncated titles** that surface as "⚠️ 待确认" rows
(e.g. "Delivery Note", "Reinforcement learning"). Those fragments need manual
arxiv title-search scraping to resolve, the most fragile, model-dependent step
in the whole pipeline.

Moonlight's 文献库 → 导出 → **BibTeX** gives structured, complete fields:
`title`, `year`, `month`, often `eprint`/`url` carrying the arxiv ID, sometimes
`abstract`. Parsing that is 100% deterministic — no Phase-0 garbage realignment,
no fuzzy arxiv search, no truncation. A weaker/smaller-context model can run the
sync one-shot without any judgment calls. This is the single biggest lever for
"skill portable to any model".

Usage
-----
  # 1. user exports BibTeX from Moonlight (文献库 → 全选 → 导出 → BibTeX),
  #    drops it here:
  #       archive/paper_source_moonlight.bib
  # 2. dry-run (show what would be ingested — verify before sync):
  python3 skills/paper-extraction/parse_moonlight_bib.py
  # 3. normal sync (sync_from_source.py auto-detects .bib and prefers it):
  python3 skills/paper-extraction/sync_from_source.py --push

If both .bib and .md exist, .bib wins (clean source). Delete the .bib to revert
to the legacy capture parse — fully backward compatible.

Output of `entries()`: list of dicts:
  {title, date("YYYY/M/D" or ""), arxiv_id or None, abstract or ""}
sync_from_source.parse_source() reshapes this into its (title, date) contract
and reuses the rest to short-circuit arxiv resolution.

Stdlib only (no bibtexparser dep) — tolerant brace+value matching.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BIB = REPO / "archive" / "paper_source_moonlight.bib"

MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"])}


def _strip_braces(s):
    # collapse one level of enclosing braces; unescape \{ \}
    s = s.replace("\\{", "\x00").replace("\\}", "\x01")
    s = s.strip()
    while s.startswith("{") and s.endswith("}"):
        s = s[1:-1].strip()
    return s.replace("\x00", "{").replace("\x01", "}")


def _split_entries(txt):
    """Yield raw {body} of each @type{key, ...} entry."""
    out = []
    i = 0
    while True:
        m = re.search(r"@\w+\s*\{", txt[i:])
        if not m:
            break
        start = i + m.end()
        depth, j = 1, start
        while j < len(txt) and depth:
            if txt[j] == "{":
                depth += 1
            elif txt[j] == "}":
                depth -= 1
            j += 1
        if depth:
            break  # unbalanced — stop
        out.append(txt[start:j - 1])
        i = j
    return out


def _parse_fields(body):
    """key = value pairs, brace-aware value parsing."""
    fields = {}
    # first token up to first comma is the cite key
    comma = body.find(",")
    if comma < 0:
        return fields
    # rest = body[comma+1:]
    rest = body[comma + 1:]
    pos = 0
    while pos < len(rest):
        m = re.match(r"\s*([\w-]+)\s*=\s*", rest[pos:])
        if not m:
            # advance to next comma to avoid infinite loop
            nxt = rest.find(",", pos)
            pos = (nxt + 1) if nxt >= 0 else len(rest)
            continue
        key = m.group(1).lower()
        val_start = pos + m.end()
        ch = rest[val_start:val_start + 1]
        if ch == "{":
            depth, j = 1, val_start + 1
            while j < len(rest) and depth:
                if rest[j] == "{":
                    depth += 1
                elif rest[j] == "}":
                    depth -= 1
                j += 1
            val = rest[val_start + 1:j - 1]
            pos = j
        elif ch == '"':
            j = val_start + 1
            while j < len(rest) and rest[j] != '"':
                if rest[j] == "\\":
                    j += 1
                j += 1
            val = rest[val_start + 1:j]
            pos = j + 1
        else:
            # bare value up to comma
            nxt = rest.find(",", val_start)
            j = nxt if nxt >= 0 else len(rest)
            val = rest[val_start:j].strip()
            pos = j
        fields[key] = _strip_braces(val)
        # skip trailing whitespace + comma
        while pos < len(rest) and rest[pos] in " \t\r\n,":
            pos += 1
    return fields


def _arxiv_id(fields):
    for k in ("eprint", "archiveprefix"):
        pass
    eid = fields.get("eprint", "").strip()
    if re.match(r"\d{4}\.\d{4,5}", eid):
        return eid
    for u in (fields.get("url", ""), fields.get("howpublished", "")):
        m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", u)
        if m:
            return m.group(1)
    return None


def _date(fields):
    y = fields.get("year", "").strip()
    mo = fields.get("month", "").strip().lower()[:3]
    if not y:
        return ""
    mi = MONTHS.get(mo, 0) or ""
    return f"{y}/{mi}/1" if mi else f"{y}//1"


def entries(path=BIB):
    """Return [{title, date, arxiv_id, abstract}] from a .bib file."""
    txt = Path(path).read_text(encoding="utf-8", errors="ignore")
    out = []
    for body in _split_entries(txt):
        f = _parse_fields(body)
        title = _strip_braces(f.get("title", "")).strip()
        if not title:
            continue
        # drop brace-surrounded notes / dedupe trailing dots
        title = re.sub(r"\s+", " ", title).strip().rstrip(".")
        out.append({
            "title": title,
            "date": _date(f),
            "arxiv_id": _arxiv_id(f),
            "abstract": _strip_braces(f.get("abstract", "")).strip(),
        })
    # dedupe by lowercased title
    seen, dedup = set(), []
    for e in out:
        k = e["title"].lower()
        if k not in seen:
            seen.add(k)
            dedup.append(e)
    return dedup


def main():
    if not BIB.exists():
        print(f"no .bib at {BIB}\n"
              "导出步骤：Moonlight 文献库 → 右上设置每页 100 → 全选 → 导出 → BibTeX →\n"
              "落到 archive/paper_source_moonlight.bib")
        return 1
    es = entries()
    with_id = [e for e in es if e["arxiv_id"]]
    print(f"== {BIB.name}: {len(es)} entries, {len(with_id)} 带 arxiv ID（无需标题搜索）==\n")
    for e in es:
        flag = "✓" if e["arxiv_id"] else " "
        print(f"  [{flag}] {e['date']:<9} {e['title'][:90]}")
        if e["arxiv_id"]:
            print(f"        arxiv:{e['arxiv_id']}")
    print(f"\n下一步：python3 skills/paper-extraction/sync_from_source.py --push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
