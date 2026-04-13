import json

with open(r'C:\Users\jotam\.gemini\antigravity\brain\3302f1b7-fe87-42a6-8109-5cb2f0cfc2d8\.system_generated\steps\56\content.md', 'r', encoding='utf-8') as f:
    data = json.load(f)

versions = list(data.get('versions', {}).keys())
print("Available versions:", versions)
