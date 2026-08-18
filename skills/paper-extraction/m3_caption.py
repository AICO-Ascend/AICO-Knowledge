#!/usr/bin/env python3
"""m3_caption.py — image deep-captioning via 蓝区火山AI网关 (OpenAI-compatible).

Replacement for the dead MiniMax coding-plan MCP (its /v1/coding_plan/vlm path is
MiniMax-native; the gateway only proxies OpenAI/Anthropic protocols, so the MCP
CANNOT use the gateway — this script is the supported path).

Usage:
  m3_caption.py <image.png> [prompt]            # print caption
  m3_caption.py --save <image.png> [prompt]     # also append to extraction/minimax_captions.json
                                                # (only for images under extraction/assets/)
  m3_caption.py --model glm-5.2 <image.png> ... # swap vision/text model (env M3_MODEL)

Model is configurable (--model flag or M3_MODEL env, default MiniMax-M3) so the
skill is portable across gateway models. MiniMax-M3 is the default vision model;
glm-5.2 also reads images. Swap freely — the caption contract is model-agnostic.

Key: env VOLC_GATEWAY_KEY, or ~/.config/aico/volc_gateway_key (chmod 600, outside repo).
Base URL is not secret (hardcoded default, overridable via VOLC_GATEWAY_URL).

Gotchas baked in:
- MiniMax-M3 is a reasoning model: max_tokens must leave headroom (default 8000);
  too-small budgets get eaten by reasoning_content and content comes back EMPTY.
- timeout 300s (image+reasoning can take a while).
- --save uses an fcntl file lock so parallel runs (4-5 images per batch) are safe —
  no clobbered JSON.
"""
import base64, fcntl, json, os, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_URL = "https://st8tp3ajl0df3n8b8l8qu.apigateway-cn-beijing.volceapi.com/v1/chat/completions"
DEFAULT_PROMPT = ("Describe the main figure: architecture/components/data flow + "
                  "one key technical takeaway (≤120 words). Then transcribe the caption verbatim.")
CAPTIONS = REPO / "extraction" / "minimax_captions.json"


def get_key():
    k = os.environ.get("VOLC_GATEWAY_KEY", "").strip()
    if k:
        return k
    p = Path.home() / ".config" / "aico" / "volc_gateway_key"
    if p.exists():
        return p.read_text().strip()
    sys.exit("no gateway key: set VOLC_GATEWAY_KEY or ~/.config/aico/volc_gateway_key")


def caption(image_path, prompt, model=None, max_tokens=8000):
    model = model or os.environ.get("M3_MODEL", "MiniMax-M3")
    img = base64.b64encode(Path(image_path).read_bytes()).decode()
    ext = Path(image_path).suffix.lstrip(".").lower() or "png"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/{ext};base64,{img}"}}]}],
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        os.environ.get("VOLC_GATEWAY_URL", DEFAULT_URL),
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {get_key()}", "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=300))
    msg = r["choices"][0]["message"]
    content = msg.get("content") or ""
    if not content.strip():
        raise RuntimeError(f"[{model}] empty content (reasoning ate the budget? usage={r.get('usage')})")
    return content.strip()


def save_caption(image_path, text):
    p = Path(image_path).resolve()
    assets = (REPO / "extraction" / "assets").resolve()
    if assets not in p.parents:
        print("  [skip save] image not under extraction/assets/")
        return
    key = f"extraction/assets/{p.name}"
    CAPTIONS.parent.mkdir(parents=True, exist_ok=True)
    # fcntl lock → safe to run 4-5 m3_caption.py --save in parallel (no clobbered JSON)
    with open(CAPTIONS, "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        raw = fh.read()
        d = json.loads(raw) if raw.strip() else {}
        d[key] = text
        fh.seek(0); fh.truncate()
        fh.write(json.dumps(d, ensure_ascii=False, indent=1))
        fcntl.flock(fh, fcntl.LOCK_UN)
    print(f"  [saved] {key} ({len(d)} total)")


def main():
    args = sys.argv[1:]
    save = "--save" in args
    args = [a for a in args if a != "--save"]
    model = None
    if "--model" in args:
        i = args.index("--model")
        model = args[i + 1]
        args = args[:i] + args[i + 2:]
    if not args:
        print(__doc__)
        return
    image = args[0]
    prompt = args[1] if len(args) > 1 else DEFAULT_PROMPT
    text = caption(image, prompt, model=model)
    print(text)
    if save:
        save_caption(image, text)
        print("\n下一步：重跑 extract_phase1.py 合并解读进 MD，然后 sync_from_source.py --push")


if __name__ == "__main__":
    main()
