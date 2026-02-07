import os
import re
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SCHEMA_DIR = PROJECT_ROOT / "schema"
REPORTS_DIR = PROJECT_ROOT / "reports" / "purl-availability"
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

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Custom handler to stop automatic redirects and allow manual tracking."""
    def http_error_301(self, req, fp, code, msg, hdrs): raise urllib.error.HTTPError(req.get_full_url(), code, msg, hdrs, fp)
    def http_error_302(self, req, fp, code, msg, hdrs): raise urllib.error.HTTPError(req.get_full_url(), code, msg, hdrs, fp)
    def http_error_303(self, req, fp, code, msg, hdrs): raise urllib.error.HTTPError(req.get_full_url(), code, msg, hdrs, fp)
    def http_error_307(self, req, fp, code, msg, hdrs): raise urllib.error.HTTPError(req.get_full_url(), code, msg, hdrs, fp)
    def http_error_308(self, req, fp, code, msg, hdrs): raise urllib.error.HTTPError(req.get_full_url(), code, msg, hdrs, fp)

def check_url(url):
    """Checks the reachability of a single URL and records redirect history."""
    history = []
    current_url = url
    max_redirects = 10
    
    # Configure opener with custom redirect handler
    opener = urllib.request.build_opener(NoRedirectHandler())
    
    for _ in range(max_redirects):
        try:
            req = urllib.request.Request(current_url, headers={'User-Agent': 'Mozilla/5.0'})
            with opener.open(req, timeout=10) as response:
                return response.getcode(), "OK", history
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308):
                location = e.headers.get('Location')
                if not location:
                    return e.code, f"Redirect without Location: {e}", history
                
                history.append(current_url)
                current_url = urllib.parse.urljoin(current_url, location)
                continue
            return e.code, str(e), history
        except urllib.error.URLError as e:
            return "Error", str(e.reason), history
        except Exception as e:
            return "Exception", str(e), history
            
    return "Error", "Too many redirects", history

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
        code, msg, history = check_url(url)
        results.append({
            "url": url,
            "code": code,
            "message": msg,
            "history": history
        })
        print(f"[{code}]" + (f" -> {len(history)} redirects" if history else ""))

    # Create reports directory
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Prepare data
    ok_list = [r for r in results if r["code"] == 200]
    err_list = [r for r in results if r["code"] != 200]
    
    # Generate Text Report (human-readable)
    txt_path = REPORTS_DIR / "latest.txt"
    with txt_path.open('w', encoding='utf-8') as f:
        f.write("URL AVAILABILITY REPORT\n")
        f.write("=======================\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Project Root: {PROJECT_ROOT}\n\n")
        
        f.write(f"[OK] Accessible URLs ({len(ok_list)}):\n")
        for r in ok_list:
            f.write(f"  {r['code']}   {r['url']}\n")
            if r["history"]:
                for step in r["history"]:
                    f.write(f"        -> redistributed from: {step}\n")
            
        f.write(f"\n[XX] Inaccessible / Error URLs ({len(err_list)}):\n")
        for r in err_list:
            f.write(f"  {r['code']}   {r['url']}  <-- {r['message']}\n")
            if r["history"]:
                for step in r["history"]:
                    f.write(f"        -> redirected via: {step}\n")

    # Generate JSON Report (for status integration)
    json_report = {
        "timestamp": datetime.now().isoformat(),
        "status": "passed" if len(err_list) == 0 else "failed",
        "summary": {
            "total": len(urls),
            "accessible": len(ok_list),
            "inaccessible": len(err_list)
        },
        "results": [
            {
                "url": r["url"], 
                "status_code": r["code"], 
                "message": r["message"], 
                "ok": r["code"] == 200,
                "redirect_history": r["history"]
            }
            for r in results
        ]
    }
    
    import json
    json_path = REPORTS_DIR / "latest.json"
    with json_path.open('w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2)

    # Generate JSON-LD Report (for schema browser)
    jsonld_report = {
        "@context": "https://purl.org/gag/schema/availability.jsonld",
        "@id": "https://purl.org/gag/schema/availability",
        "@type": "gag:AvailabilityReport",
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "@type": "gag:AvailabilitySummary",
            "total": len(urls),
            "accessible": len(ok_list),
            "inaccessible": len(err_list)
        },
        "results": [
            {
                "@type": "gag:AvailabilityResult",
                "url": r["url"], 
                "status_code": r["code"], 
                "message": r["message"], 
                "ok": r["code"] == 200,
                "redirect_history": r["history"]
            }
            for r in results
        ]
    }
    
    jsonld_path = REPORTS_DIR / "latest.jsonld"
    with jsonld_path.open('w', encoding='utf-8') as f:
        json.dump(jsonld_report, f, indent=2)

    print(f"\nReports generated in: {REPORTS_DIR}")
    print(f"  - Text report:    {txt_path.name}")
    print(f"  - JSON report:    {json_path.name}")
    print(f"  - JSON-LD report: {jsonld_path.name}")

if __name__ == "__main__":
    main()
