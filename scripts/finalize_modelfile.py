import yaml
import os

modelfile_path = r"C:\Users\jotam\OneDrive\Desktop\GahenaxAI\Gahenax_Modelfile"
skills_path = r"C:\Users\jotam\OneDrive\Desktop\GahenaxAI\scripts\skills_summary.yaml"

with open(skills_path, "r", encoding="utf-8") as f:
    summaries = yaml.safe_load(f)

skill_list = "\n".join([f"- {k}: {v}" for k, v in summaries.items()])

with open(modelfile_path, "r", encoding="utf-8") as f:
    content = f.read()

placeholder = "- (Full list of 75 skills inherited from .agent/skills/)"
if placeholder in content:
    new_content = content.replace(placeholder, skill_list)
    with open(modelfile_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Success: Skills injected into Modelfile.")
else:
    print("Error: Placeholder not found in Modelfile.")
