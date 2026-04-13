import os
import yaml

skills_dir = r"C:\Users\jotam\OneDrive\Desktop\GahenaxAI\.agent\skills"
output_file = r"C:\Users\jotam\OneDrive\Desktop\GahenaxAI\scripts\skills_summary.yaml"

summaries = {}

for skill_name in os.listdir(skills_dir):
    skill_path = os.path.join(skills_dir, skill_name)
    if os.path.isdir(skill_path):
        skill_file = os.path.join(skill_path, "SKILL.md")
        if os.path.exists(skill_file):
            try:
                with open(skill_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.startswith("---"):
                        _, frontmatter_str, _ = content.split("---", 2)
                        data = yaml.safe_load(frontmatter_str)
                        summaries[skill_name] = data.get("description", "No description")
            except Exception as e:
                summaries[skill_name] = f"Error reading skill: {str(e)}"

with open(output_file, "w", encoding="utf-8") as f:
    yaml.dump(summaries, f, allow_unicode=True)

print(f"Summarized {len(summaries)} skills to {output_file}")
