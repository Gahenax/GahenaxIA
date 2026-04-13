import urllib.request
import json

url = "https://registry.npmjs.org/@anthropic-ai/claude-code"
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())

versions = list(data.get('versions', {}).keys())
print("Available versions:", versions)

# find the most recent versions and download them one by one, looking for cli.js.map
for version in reversed(versions[-10:]):
    print(f"Checking {version}...")
    tarball_url = data['versions'][version]['dist']['tarball']
    # You can inspect the tarball if needed
