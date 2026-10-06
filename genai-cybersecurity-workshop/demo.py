"""Step through every demo. Offline: set WORKSHOP_MODE=replay first.  python demo.py"""
import subprocess, sys

steps = [["secure_gen.py"], ["ai_review.py", "--file", "app.py"],
         ["triage.py", "sample/semgrep_sample.json"], ["ai_review.py", "--file", "infra/main.tf"],
         ["threat_model.py"], ["log_triage.py", "sample/access.log"]]
for s in steps:
    cmd = "python " + " ".join(s)
    input(f"\n################ {cmd}\n[press Enter to run] ")
    subprocess.run([sys.executable] + s)
