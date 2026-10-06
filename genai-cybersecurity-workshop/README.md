# GenAI for Cybersecurity: Shift Left, With an AI at Every Gate

Workshop materials: slides are in `slides/`, code is in this folder. **No API key is included. Never commit your own key.** The example pipeline is in `examples/github-actions-security.yml`; copy it to `.github/workflows/` to enable it and add your own `ANTHROPIC_API_KEY` as a repository secret (do this only in a private repo or fork).

Hands-on repo for the 30-minute workshop. Four gates: IDE -> Pull Request -> CI/CD -> Pre-prod.
`app.py` and `infra/main.tf` are **intentionally vulnerable**. Never deploy them.

## Prerequisites
- Python 3.10+ and git (check: `python3 --version`)
- (Live mode only) An Anthropic API key (console.anthropic.com). Other providers work: change only `ask()` in `llm.py`.
- Optional: a GitHub repo (for the CI demo). Semgrep needs internet; the triage demo has an offline sample.

## WINDOWS USERS (Command Prompt) - read this first
These instructions use the cross-platform Python scripts (`record.py`, `demo.py`), which work on Windows, macOS and Linux. On Windows (Command Prompt):
```bat
cd genai-sec-workshop
python -m venv .venv
.venv\Scripts\activate
pip install anthropic
set ANTHROPIC_API_KEY=sk-ant-your-key-here
python record.py
```
- Use `python` (or `py`), not `python3`. No quotes around the key in `set`.
- `set` only lasts for that window; re-run it if you open a new Command Prompt. PowerShell: `$env:ANTHROPIC_API_KEY="sk-ant-..."`.
- Offline demo: `set WORKSHOP_MODE=replay` then `python demo.py` (or any single command from the Demos table).
- Only `anthropic` is needed (skip flask/semgrep; they aren't used by the demos).
- The git pre-push hook works in Git for Windows (it runs through Git Bash).

## OFFLINE VENUE? Read this first
No internet at the venue means no API calls. Three options, best first:

**A. Record online, replay offline (recommended, zero dependencies at the venue)**
1. At home or hotel, with internet: do Setup below, then `python record.py`. It runs every demo once and saves the real answers in `cache/`.
2. At the venue: `export WORKSHOP_MODE=replay` (Windows: `set WORKSHOP_MODE=replay`) and run the demos exactly as in the table. Only plain Python 3 is needed. No key, no packages, no network.
3. Never recorded? The repo ships `fallback/` samples (hand-written illustrations, not real model output) so replay still works. Say so on stage if you use them.
4. `python demo.py` steps through all six demos with a pause between each (`python demo.py` with WORKSHOP_MODE=replay set).

**B. Local model with Ollama (live, but fully offline)**
1. Online beforehand: install Ollama, then `ollama pull qwen2.5-coder:7b` (about 5 GB; a larger model gives better JSON).
2. At the venue: `ollama serve` in one terminal, then `export WORKSHOP_MODE=ollama` and run the demos. Answers are saved to `cache/` too.
3. Needs about 8 GB free RAM; expect 10-60 s per answer on a laptop without a GPU. Small models sometimes break the JSON format, so keep replay as your fallback. Optional: `export OLLAMA_MODEL=<name>`.

**C. Attendees' laptops offline:** before the event, run `pip download -r requirements.txt -d wheels` and share the `wheels/` folder on USB. They install with `pip install --no-index --find-links wheels -r requirements.txt`. Replay mode doesn't need this at all.

**What changes offline**
- GitHub Actions can't run. Show the workflow file plus a screenshot of a failed check, or use the local stand-in: `cp hooks/pre-push .git/hooks/pre-push`, then `git push` and the AI gate runs before the push (see Diff demo).
- Semgrep (`--config auto` downloads rules) is skipped. Use `sample/semgrep_sample.json`, already wired into the triage demo.
- Test everything with Wi-Fi turned off before you travel.

## Setup (once, ~2 min, online)
```bash
cd genai-sec-workshop
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."                  # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
```
Optional: `export WORKSHOP_MODEL=<model id>` to change the model (default `claude-sonnet-5-5`).

## Demos
| Gate | Command | What to expect |
|---|---|---|
| 1 IDE | `python secure_gen.py` | Two answers to the same prompt. Compare the two answers: a modern model may already parameterize SQL for the naive prompt, but SECURE adds input validation, bounds, env-based config, generic errors, a CWE list and residual risks |
| 2 PR | `python ai_review.py --file app.py` | Findings: SQL injection (CWE-89), command injection (CWE-78), hardcoded secret (CWE-798). Exit code 1 |
| 2 PR (real diff) | see "Diff demo" below | Same, but only for changed lines |
| 3 CI | `python triage.py sample/semgrep_sample.json` | 3 raw findings -> 2 confirmed, the `os` import flagged as false positive |
| 3 IaC | `python ai_review.py --file infra/main.tf` | Open SSH to the world (CWE-284), public-read bucket |
| 4 Pre-prod | `python threat_model.py` | STRIDE table, ranked risks, 3 staging test cases |
| 4 Logs | `python log_triage.py sample/access.log` | Brute force then successful login (203.0.113.9), SQLi + command injection (198.51.100.7), recon (192.0.2.44) |

Check the exit code after any review: `echo $?` (1 = build would fail).
Model output varies run to run. Judge the substance, not exact wording.

### Diff demo (the PR flow)
```bash
git init -q && git checkout -q -b main
git add llm.py && git commit -qm "base"          # a clean baseline
git checkout -q -b feature/user-lookup
git add app.py && git commit -qm "add user lookup"
python ai_review.py --base main                  # reviews only what the branch adds
```

### CI demo on GitHub
1. Push the repo to GitHub.
2. Settings -> Secrets and variables -> Actions -> New secret: `ANTHROPIC_API_KEY`.
3. Create a branch, change `app.py`, open a pull request into `main`.
4. Open the **Checks** tab: `ai-security-gate` runs Semgrep, AI triage and AI review. The job fails on confirmed or high/critical findings.
5. Fix the code (parameterized query, env var for secret, `subprocess.run([...], shell=False)`) and push: the check turns green.

## Securing the AI itself (what this repo already does)
- `llm.py: redact()` strips secret values before code is sent to the model.
- Every system prompt says the input is untrusted data (prompt-injection defence).
- Output is structured JSON; the bot can fail a build but cannot merge, push or edit code.
- Humans approve every merge.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `Set ANTHROPIC_API_KEY first` | Re-export the key in this shell |
| `JSONDecodeError` / `Model did not return JSON` | Re-run; or raise `max_tokens` for that script |
| `authentication_error` | Wrong or revoked key |
| `model not found` | Set `WORKSHOP_MODEL` to a model your key can access |
| `semgrep` fails offline | Use `sample/semgrep_sample.json`; for live: `semgrep --config auto --json -o semgrep.json .` (needs internet) |
| `not scoped to a workspace` (400) | Create the key inside the **Default** workspace, or `set ANTHROPIC_WORKSPACE_ID=wrkspc_...` (ID from the console's Workspaces page) |
| Rate limit (429) | Wait a few seconds; run demos one at a time |
