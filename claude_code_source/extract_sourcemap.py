import json
import os

MAP_FILE = "node_modules/@anthropic-ai/claude-code/cli.js.map"
OUTPUT_DIR = "src_extracted"

if not os.path.exists(MAP_FILE):
    print(f"File not found: {MAP_FILE}")
    exit(1)

with open(MAP_FILE, "r", encoding="utf-8") as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        print("Error decoding JSON from map file")
        exit(1)

sources = data.get("sources", [])
sources_content = data.get("sourcesContent", [])

print(f"Loaded {len(sources)} sources from {MAP_FILE}")

extracted = 0
for i, source_path in enumerate(sources):
    content = sources_content[i] if i < len(sources_content) else None
    if not content:
        continue
    
    clean_path = source_path
    if clean_path.startswith("webpack:///"):
        clean_path = clean_path.replace("webpack:///", "")
    
    # Remove weird prefixes like ".." or "node_modules" if they escape our dir
    # we just want the pure src
    if clean_path.startswith("../"):
        clean_path = clean_path.replace("../", "", 1)
        
    out_file = os.path.normpath(os.path.join(OUTPUT_DIR, clean_path))
    
    # Prevent traversal
    if ".." in out_file or not out_file.startswith(OUTPUT_DIR):
        continue

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    extracted += 1

print(f"Done extracting {extracted} files to {OUTPUT_DIR}")
