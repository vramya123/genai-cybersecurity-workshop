"""Run ONCE while online. Saves real model answers to cache/ for offline replay.
Windows/macOS/Linux:  python record.py"""
import os, subprocess, sys

steps = [["secure_gen.py"], ["ai_review.py", "--file", "app.py"],
         ["ai_review.py", "--file", "infra/main.tf"], ["triage.py", "sample/semgrep_sample.json"],
         ["log_triage.py", "sample/access.log"], ["threat_model.py"]]
if os.environ.get("WORKSHOP_MODE", "live") == "replay":
    sys.exit("Unset WORKSHOP_MODE (or set it to live/ollama) before recording.")
failed = False
for s in steps:
    print("recording:", " ".join(s))
    r = subprocess.run([sys.executable] + s, capture_output=True, text=True)
    if r.returncode not in (0, 1) or "Traceback" in r.stderr:   # exit 1 alone = findings found (expected)
        failed = True
        print("  FAILED:", (r.stderr.strip().splitlines() or ["unknown error"])[-1])
saved = sorted(f for f in os.listdir("cache") if f.endswith(".txt"))
print("\nSaved to cache/:", ", ".join(saved) or "(nothing)")
if failed:
    sys.exit("\nSome steps failed. Fix the error above, then run python record.py again.")
print("All six demos recorded.")
