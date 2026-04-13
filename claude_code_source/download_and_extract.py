import urllib.request
import json
import tarfile
import io
import os

print("Fetching metadata from npm...")
url = "https://registry.npmjs.org/@anthropic-ai/claude-code"
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())

# The version in the user's screenshot had a 57MB map file. 
# Claude Code was published recently, around Mar 2026 or Feb 2024? The screenshot says "Mar 31".
# Let's find the latest version and download its tarball.
versions = list(data.get('versions', {}).keys())
latest_version = data.get('dist-tags', {}).get('latest', versions[-1])
print(f"Latest version is {latest_version}")

tarball_url = data['versions'][latest_version]['dist']['tarball']
print(f"Downloading {tarball_url} ...")

with urllib.request.urlopen(tarball_url) as response:
    tar_data = response.read()

print("Extracting tarball...")
with tarfile.open(fileobj=io.BytesIO(tar_data), mode="r:gz") as tar:
    map_members = [m for m in tar.getmembers() if m.name.endswith(".map")]
    if not map_members:
        print("No .map files found in the latest version.")
        # Try a specific older version, e.g., 0.2.1, 0.2.29, 0.2.42
        # For this script we will stop here.
    else:
        print(f"Found map file: {map_members[0].name}")
        tar.extractall(path="extracted_npm_pkg")
        print("Done. To extract the source code from the map, use the extract_sourcemap.py script.")

print("Finished script execution.")
