import json

with open("scanner-results.json", "r", encoding="utf-8") as f:
    scanner = json.load(f)

# For EFU, I'll fetch raw results directly here to be sure
import urllib.request
import urllib.parse
import json as json_lib

ip = "127.160.164.78"
port = 8000
query = '"D:\\github\\get-a-grip"'
params = {
    'q': query,
    'j': 1,
    'path_column': 1,
    'count': 5000
}
url = f"http://{ip}:{port}/?{urllib.parse.urlencode(params)}"
with urllib.request.urlopen(url) as response:
    efu_data = json_lib.loads(response.read().decode('utf-8'))

scanner_files = {f["Filename"] for f in scanner.get("files", [])}
scanner_dirs = {d["Filename"] for d in scanner.get("dirs", [])}

efu_results = efu_data.get("results", [])
efu_files = {f["path"] + "\\" + f["name"] if f["path"] else f["name"] for f in efu_results if f.get("type") == "file"}
efu_dirs = {d["path"] + "\\" + d["name"] if d["path"] else d["name"] for d in efu_results if d.get("type") == "folder"}

print(f"Scanner: Files={len(scanner_files)}, Dirs={len(scanner_dirs)}")
print(f"Everything: Files={len(efu_files)}, Dirs={len(efu_dirs)}")

print("\nFiles in Everything but not in Scanner:")
for f in sorted(efu_files - scanner_files):
    print(f"  {f}")

print("\nDirs in Everything but not in Scanner:")
for d in sorted(efu_dirs - scanner_dirs):
    print(f"  {d}")

print("\nFiles in Scanner but not in Everything:")
for f in sorted(scanner_files - efu_files):
    print(f"  {f}")
