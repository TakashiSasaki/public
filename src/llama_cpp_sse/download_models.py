import argparse
import urllib.request
import shutil
import sys
from pathlib import Path
import hashlib

MODELS = {
    "instruct": {
        "url": "https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF/resolve/main/LFM2.5-1.2B-Instruct-Q4_K_M.gguf",
        "filename": "LFM2.5-1.2B-Instruct-Q4_K_M.gguf"
    },
    "thinking": {
        "url": "https://huggingface.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF/resolve/main/LFM2.5-1.2B-Thinking-Q4_K_M.gguf",
        "filename": "LFM2.5-1.2B-Thinking-Q4_K_M.gguf"
    }
}

MODELS_DIR = Path("models")

def download_file(url, dest_path):
    print(f"Downloading {url}...")
    try:
        with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Download complete.")
    except Exception as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Download LiquidAI GGUF models")
    parser.add_argument("model", choices=["instruct", "thinking", "all"], help="Model to download")
    args = parser.parse_args()

    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

    models_to_download = [args.model] if args.model != "all" else ["instruct", "thinking"]

    for model_key in models_to_download:
        info = MODELS[model_key]
        dest_path = MODELS_DIR / info["filename"]
        
        if dest_path.exists():
            print(f"Model {info['filename']} already exists at {dest_path}. Skipping.")
        else:
            print(f"Downloading {model_key} model to {dest_path}...")
            download_file(info["url"], dest_path)
            print(f"Successfully downloaded {info['filename']}")

if __name__ == "__main__":
    main()
