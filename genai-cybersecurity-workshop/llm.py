"""Shared helpers. Three modes (env WORKSHOP_MODE):
  live    - Anthropic API (needs internet + ANTHROPIC_API_KEY). Saves every answer to cache/.
  ollama  - local model via Ollama (needs `ollama serve` + a pulled model). Saves to cache/.
  replay  - NO network, NO packages: plays back cache/<name>.txt (your real recorded runs),
            else fallback/<name>.txt (illustrative samples shipped with the repo).
Run `python record.py` once while online, then use WORKSHOP_MODE=replay at the venue."""
import json, os, re, sys, urllib.request
from pathlib import Path

MODE = os.getenv("WORKSHOP_MODE", "live")
MODEL = os.getenv("WORKSHOP_MODEL", "claude-sonnet-5-5")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
ROOT = Path(__file__).parent
for _s in (sys.stdout, sys.stderr):                 # never crash on characters the Windows console lacks
    try:
        _s.reconfigure(errors="replace")
    except Exception:
        pass
_ASCII = {"\u2192": "->", "\u2190": "<-", "\u2194": "<->", "\u2013": "-", "\u2014": "-", "\u201c": '"',
          "\u201d": '"', "\u2018": "'", "\u2019": "'", "\u2026": "...", "\u2022": "-", "\u2265": ">=",
          "\u2264": "<=", "\u00d7": "x", "\u2713": "OK", "\u2717": "X"}

def _clean(text: str) -> str:
    """Swap fancy Unicode for ASCII so cmd.exe prints it and the cache file is portable."""
    for k, v in _ASCII.items():
        text = text.replace(k, v)
    return text

SECRET = re.compile(r"(sk_live_|sk-ant-|AKIA|ghp_)[A-Za-z0-9_\-]+")

def redact(text: str) -> str:
    """Strip secret VALUES before code leaves your machine (keeps variable names)."""
    return SECRET.sub("<REDACTED_SECRET>", text)

def _replay(name):
    for folder in ("cache", "fallback"):
        p = ROOT / folder / f"{name}.txt"
        if p.exists():
            print(f"[replay: {folder}/{name}.txt]", file=sys.stderr)
            return _clean(p.read_text(encoding="utf-8", errors="replace"))
    raise SystemExit(f"No recording for '{name}'. Run `python record.py` while online first.")

def _live(system, user, max_tokens):
    import anthropic                      # imported lazily: replay mode needs no packages
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY, or run offline with WORKSHOP_MODE=replay.")
    ws = os.getenv("ANTHROPIC_WORKSPACE_ID")      # only needed if your key is not scoped to a workspace
    client = anthropic.Anthropic(default_headers={"anthropic-workspace-id": ws} if ws else None)
    tokens = max(max_tokens, 4000)
    for _ in range(3):
        msg = client.messages.create(model=MODEL, max_tokens=tokens, system=system,
                                     messages=[{"role": "user", "content": user}])
        if msg.stop_reason != "max_tokens":
            break
        tokens *= 2                       # answer was cut off: retry with more room
    else:
        print("WARNING: answer may still be truncated", file=sys.stderr)
    # newer models may return a thinking block first: keep only the text blocks
    return "".join(blk.text for blk in msg.content if getattr(blk, "type", "") == "text")

def _ollama(system, user, max_tokens):
    body = json.dumps({"model": OLLAMA_MODEL, "stream": False, "options": {"num_predict": max_tokens},
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(f"{OLLAMA_URL}/api/chat", body, {"Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=300))["message"]["content"]
    except OSError:
        raise SystemExit("Ollama not reachable. Start it with `ollama serve` and `ollama pull "
                         f"{OLLAMA_MODEL}`.")

def ask(system: str, user: str, max_tokens: int = 1500, name: str = "adhoc") -> str:
    if MODE == "replay":
        return _replay(name)
    user = redact(user)
    text = _clean((_ollama if MODE == "ollama" else _live)(system, user, max_tokens))
    if os.getenv("WORKSHOP_RECORD", "1") == "1":
        (ROOT / "cache" / f"{name}.txt").write_text(text, encoding="utf-8")
    return text

def ask_json(system: str, user: str, max_tokens: int = 1500, name: str = "adhoc") -> dict:
    text = ask(system, user, max_tokens, name)
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError(f"Model did not return JSON:\n{text}")
    return json.loads(match.group(0))
