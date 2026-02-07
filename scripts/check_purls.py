import os
import re
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SCHEMA_DIR = PROJECT_ROOT / "schema"
REPORT_PATH = SCHEMA_DIR / "url_availability_report.txt"
PURL_PREFIX = "https://purl.org/gag/"

def find_urls(directory):
    """Finds all GAG PURLs within the schema directory."""
    urls = set()
    # Matches URLs starting with the prefix until a breaking character
    pattern = re.compile(rf'{re.escape(PURL_PREFIX)}[^\s\"\'\],}}#]+')
    
    for path in directory.rglob("*"):
        if path.suffix == ".txt" or path.is_dir():
            continue
        try:
            content = path.read_text(encoding="utf-8")
            matches = pattern.findall(content)
            for m in matches:
                # Clean trailing periods or commas
                urls.add(m.rstrip('.').rstrip(','))
        except Exception as e:
            print(f"Warning: Could not read {path}: {e}")
    return sorted(list(urls))

def check_url(url):
    """Checks the reachability of a single URL."""
    try:
        # Use a standard User-Agent to avoid generic bot blocks
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.getcode(), "OK"
    except urllib.error.HTTPError as e:
        return e.code, str(e)
    except urllib.error.URLError as e:
        return "Error", str(e.reason)
    except Exception as e:
        return "Exception", str(e)

def main():
    print(f"Scanning for URLs in: {SCHEMA_DIR}")
    urls = find_urls(SCHEMA_DIR)
    
    if not urls:
        print("No URLs found matching the prefix.")
        return

    print(f"Checking {len(urls)} URLs...")
    results = []
    for url in urls:
        print(f"Checking {url: <50} ... ", end="", flush=True)
        code, msg = check_url(url)
        results.append((url, code, msg))
        print(f"[{code}]")

    # Generate Report
    with REPORT_PATH.open('w', encoding='utf-8') as f:
        f.write("URL AVAILABILITY REPORT\n")
        f.write("=======================\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Project Root: {PROJECT_ROOT}\n\n")
        
        ok_list = [r for r in results if r[1] == 200]
        err_list = [r for r in results if r[1] != 200]
        
        f.write(f"[OK] Accessible URLs ({len(ok_list)}):\n")
        for url, code, msg in ok_list:
            f.write(f"  {code}   {url}\n")
            
        f.write(f"\n[XX] Inaccessible / Error URLs ({len(err_list)}):\n")
        for url, code, msg in err_list:
            f.write(f"  {code}   {url}  <-- {msg}\n")

    # Generate JSON Report for Schema Browser
    json_report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total": len(urls),
            "accessible": len(ok_list),
            "inaccessible": len(err_list)
        },
        "results": [
            {"url": url, "status_code": code, "message": msg, "ok": code == 200}
            for url, code, msg in results
        ]
    }
    
    import json
    json_path = SCHEMA_DIR / "url_availability_report.json"
    with json_path.open('w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2)

    print(f"\nReport generated at: {REPORT_PATH}")
    print(f"JSON Report generated at: {json_path}")

if __name__ == "__main__":
    main()
