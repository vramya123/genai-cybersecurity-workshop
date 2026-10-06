from pathlib import Path
from llm import ask
print(ask("You are a senior security architect. Reply in under 450 words, using terse bullets and one table.", Path("prompts/threat_model.md").read_text(), 6000, "threat"))
