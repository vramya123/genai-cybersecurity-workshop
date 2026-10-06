"""Gate 1 demo: same task, naive vs security-aware system prompt."""
from pathlib import Path
from llm import ask

TASK = "Write a Flask endpoint that looks up a user by name from SQLite and returns JSON."
naive = "You are a helpful coding assistant."
secure = Path("prompts/secure_coding.md").read_text()

for label, system in (("NAIVE", naive), ("SECURE", secure)):
    print(f"\n{'=' * 20} {label} {'=' * 20}\n")
    print(ask(system, TASK, max_tokens=1200, name=f"gen_{label.lower()}"))
