import os
import re

PROMPT_DIR = "prompts"
PLACEHOLDERS = [
    "business_problem",
    "tech_stack",
    "time_constraint",
    "resource_constraints"
]

def fix_braces_in_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Escape all curly braces
    content = content.replace("{", "{{").replace("}", "}}")
    # Un-escape placeholders
    for ph in PLACEHOLDERS:
        content = content.replace("{{" + ph + "}}", "{" + ph + "}")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fixed: {filepath}")

def main():
    for filename in os.listdir(PROMPT_DIR):
        if filename.endswith("_prompt.txt"):
            fix_braces_in_file(os.path.join(PROMPT_DIR, filename))

if __name__ == "__main__":
    main()