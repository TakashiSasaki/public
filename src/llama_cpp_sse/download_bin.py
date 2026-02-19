import os
import zipfile
import urllib.request
import shutil
from pathlib import Path
import sys

URL = "https://github.com/ggml-org/llama.cpp/releases/download/b8095/cudart-llama-bin-win-cuda-12.4-x64.zip"
DEPS_DIR = Path("deps")
DEST_DIR = DEPS_DIR / "llama_cpp_bin"

def download_file(url, dest_path):
    print(f"Downloading {url}...")
    try:
        with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Download complete.")
    except Exception as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)

def extract_zip(zip_path, extract_to):
    print(f"Extracting {zip_path} to {extract_to}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("Extraction complete.")
    except Exception as e:
        print(f"Error extracting zip: {e}")
        sys.exit(1)

def main():
    if not DEPS_DIR.exists():
        DEPS_DIR.mkdir(parents=True, exist_ok=True)
    
    if DEST_DIR.exists():
        print(f"Destination directory {DEST_DIR} already exists. Skipping download.")
        return

    check_env_script = Path("src/llama_cpp_sse/check_env.py")
    # Simple check to ensure we are running from project root or close to it
    if not check_env_script.exists() and not Path("pyproject.toml").exists():
         print("Warning: It seems you are not running from the project root.")

    zip_path = DEPS_DIR / "temp_llama.zip"
    
    download_file(URL, zip_path)
    extract_zip(zip_path, DEST_DIR)
    
    try:
        os.remove(zip_path)
        print("Cleaned up temporary zip file.")
    except OSError as e:
        print(f"Error removing temporary file: {e}")

    print(f"\nllama.cpp binaries installed to: {DEST_DIR.absolute()}")

if __name__ == "__main__":
    main()
