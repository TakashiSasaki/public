import os
import re
import urllib.request
import urllib.error
import ssl

# Ignore SSL certificate verification for this check script
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SCHEMA_DIR = r"c:\Users\takas\Documents\GitHub\get-a-grip\schema"

def extract_urls_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Simple regex to capture http/https URLs within text files
            # Stops at quotes, whitespace, or common delimiters
            return set(re.findall(r'https?://[^\s"\'<>]+', content))
    except Exception as e:
        print(f"Could not read {filepath}: {e}")
        return set()

def check_url(url):
    # Some PURLs usually return 302, urllib follows redirects by default.
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            return True, response.status
    except urllib.error.HTTPError as e:
        # 405 Method Not Allowed commonly happens with HEAD requests on some servers
        if e.code == 405:
            try:
                req = urllib.request.Request(url, method='GET')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
                with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                    return True, response.status
            except urllib.error.HTTPError as e2:
                return False, e2.code
            except Exception as e2:
                return False, str(e2)
        return False, e.code
    except urllib.error.URLError as e:
        return False, str(e.reason)
    except Exception as e:
        return False, str(e)

def test_schema_url_accessibility():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_dir = os.path.join(root_dir, "schema")
    report_path = os.path.join(schema_dir, "url_availability_report.txt")
    
    all_urls = set()
    print(f"Scanning directory: {schema_dir}")
    for root, dirs, files in os.walk(schema_dir):
        for file in files:
            # Skip the report file itself to avoid loop or false positives
            if file == "url_availability_report.txt":
                continue
                
            path = os.path.join(root, file)
            urls = extract_urls_from_file(path)
            all_urls.update(urls)
    
    print(f"Found {len(all_urls)} unique URLs.")
    
    accessible = []
    inaccessible = []

    for url in sorted(list(all_urls)):
        success, status = check_url(url)
        
        if success or (isinstance(status, int) and status in [403]): 
            if success:
                accessible.append((url, status))
            else:
                inaccessible.append((url, status))
        else:
            inaccessible.append((url, status))

    # Generate Report Content
    lines = []
    lines.append("URL AVAILABILITY REPORT")
    lines.append("=======================")
    from datetime import datetime
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append(f"Scanned Directory: {schema_dir}")
    lines.append("")
    
    lines.append(f"[OK] Accessible URLs ({len(accessible)}):")
    for url, status in accessible:
        lines.append(f"  {status:<5} {url}")

    lines.append("")
    lines.append(f"[XX] Inaccessible / Error URLs ({len(inaccessible)}):")
    for url, status in inaccessible:
        note = ""
        # Identify PURLs likely to be 404
        if "purl.org/gag" in url or "purl.org/domain/gag" in url:
            note = "  <-- Project specific PURL (Expected 404 if not registered)"
        elif "identity/ad" in url or "ns/snmp" in url or "net/ldap" in url:
             note = "  <-- External standard vocabulary (Known to be possibly offline)"
             
        lines.append(f"  {status:<5} {url}{note}")

    report_content = "\n".join(lines)
    
    # Write to file
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"Report written to: {report_path}")
    print(report_content)

