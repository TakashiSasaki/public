import os
import zipfile
import urllib.request
import shutil
import argparse
from pathlib import Path
import sys

URLS = {
    "cuda": [
        "https://github.com/ggml-org/llama.cpp/releases/download/b8095/cudart-llama-bin-win-cuda-12.4-x64.zip",
        "https://github.com/ggml-org/llama.cpp/releases/download/b8095/llama-b8095-bin-win-cuda-12.4-x64.zip"
    ],
    "vulkan": [
        "https://github.com/ggml-org/llama.cpp/releases/download/b8095/llama-b8095-bin-win-vulkan-x64.zip"
    ],
    "cpu": [
        "https://github.com/ggml-org/llama.cpp/releases/download/b8095/llama-b8095-bin-win-cpu-x64.zip"
    ]
}

DEPS_DIR = Path("deps")

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
    parser = argparse.ArgumentParser(description="Download llama.cpp binaries")
    parser.add_argument("--backend", choices=["cuda", "vulkan", "cpu"], default="cuda", help="Backend to download (cuda, vulkan, or cpu)")
    args = parser.parse_args()

    urls = URLS[args.backend]
    dest_dir = DEPS_DIR / f"llama_cpp_{args.backend}"

    if not DEPS_DIR.exists():
        DEPS_DIR.mkdir(parents=True, exist_ok=True)
    
    # We allow overwriting/updating, so no early return if dest_dir exists.
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"Target backend: {args.backend}")
    print(f"Target directory: {dest_dir}")

    for i, url in enumerate(urls):
        zip_path = DEPS_DIR / f"temp_llama_{args.backend}_{i}.zip"
        download_file(url, zip_path)
        extract_zip(zip_path, dest_dir)
        try:
            os.remove(zip_path)
            print(f"Cleaned up temporary zip file {zip_path}.")
        except OSError as e:
            print(f"Error removing temporary file: {e}")

    print(f"\nllama.cpp binaries for {args.backend} installed to: {dest_dir.absolute()}")

if __name__ == "__main__":
    main()
