import argparse
import urllib.request
import shutil
import sys
from pathlib import Path
import hashlib
try:
    from . import settings
except ImportError:
    # Fallback if running as script
    import settings

MODELS = {
    "instruct": {
        "url": "https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF/resolve/main/LFM2.5-1.2B-Instruct-Q4_K_M.gguf",
        "filename": "LFM2.5-1.2B-Instruct-Q4_K_M.gguf"
    },
    "thinking": {
        "url": "https://huggingface.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF/resolve/main/LFM2.5-1.2B-Thinking-Q4_K_M.gguf",
        "filename": "LFM2.5-1.2B-Thinking-Q4_K_M.gguf"
    },
    "gemma3": {
        "url": "https://huggingface.co/gguf-org/gemma-3-1b-it-gguf/resolve/main/gemma-3-1b-it-q4_k_m.gguf",
        "filename": "gemma-3-1b-it-q4_k_m.gguf"
    },
    "gemma3n": {
        "url": "https://huggingface.co/bartowski/google_gemma-3n-E4B-it-GGUF/resolve/main/google_gemma-3n-E4B-it-Q4_K_M.gguf",
        "filename": "google_gemma-3n-E4B-it-Q4_K_M.gguf"
    },
    "qwen3": {
        "url": "https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF/resolve/main/Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf",
        "filename": "Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf"
    },
    "qwen3-q8": {
        "url": "https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF/resolve/main/Qwen_Qwen3-4B-Instruct-2507-Q8_0.gguf",
        "filename": "Qwen_Qwen3-4B-Instruct-2507-Q8_0.gguf"
    },
    "qwen3-think": {
        "url": "https://huggingface.co/bartowski/Qwen_Qwen3-4B-Thinking-2507-GGUF/resolve/main/Qwen_Qwen3-4B-Thinking-2507-Q4_K_M.gguf",
        "filename": "Qwen_Qwen3-4B-Thinking-2507-Q4_K_M.gguf"
    },
    "qwen3-think-q8": {
        "url": "https://huggingface.co/bartowski/Qwen_Qwen3-4B-Thinking-2507-GGUF/resolve/main/Qwen_Qwen3-4B-Thinking-2507-Q8_0.gguf",
        "filename": "Qwen_Qwen3-4B-Thinking-2507-Q8_0.gguf"
    },
    "mistral": {
        "url": "https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF/resolve/main/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf",
        "filename": "Ministral-3-3B-Instruct-2512-Q4_K_M.gguf"
    },
    "mistral-q8": {
        "url": "https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF/resolve/main/Ministral-3-3B-Instruct-2512-Q8_0.gguf",
        "filename": "Ministral-3-3B-Instruct-2512-Q8_0.gguf"
    },
    "mistral-reason": {
        "url": "https://huggingface.co/unsloth/Ministral-3-3B-Reasoning-2512-GGUF/resolve/main/Ministral-3-3B-Reasoning-2512-Q4_K_M.gguf",
        "filename": "Ministral-3-3B-Reasoning-2512-Q4_K_M.gguf"
    },
    "mistral-reason-q8": {
        "url": "https://huggingface.co/unsloth/Ministral-3-3B-Reasoning-2512-GGUF/resolve/main/Ministral-3-3B-Reasoning-2512-Q8_0.gguf",
        "filename": "Ministral-3-3B-Reasoning-2512-Q8_0.gguf"
    },
    "llama3.2-1b": {
        "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        "filename": "Llama-3.2-1B-Instruct-Q4_K_M.gguf"
    },
    "llama3.2-1b-q8": {
        "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q8_0.gguf",
        "filename": "Llama-3.2-1B-Instruct-Q8_0.gguf"
    },
    "llama3.2-1b-spin": {
        "url": "https://huggingface.co/mradermacher/llama-3.2-1B-spinquant-hf-GGUF/resolve/main/llama-3.2-1B-spinquant-hf.IQ4_XS.gguf",
        "filename": "llama-3.2-1B-spinquant-hf.IQ4_XS.gguf"
    },
    "llama-guard": {
        "url": "https://huggingface.co/QuantFactory/Llama-Guard-3-1B-GGUF/resolve/main/Llama-Guard-3-1B.Q4_K_M.gguf",
        "filename": "Llama-Guard-3-1B.Q4_K_M.gguf"
    },
    "embed-gemma": {
        "url": "https://huggingface.co/unsloth/embeddinggemma-300m-GGUF/resolve/main/embeddinggemma-300m-Q4_0.gguf",
        "filename": "embeddinggemma-300m-Q4_0.gguf"
    },
    "embed-nomic": {
        "url": "https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/nomic-embed-text-v1.5.Q4_K_M.gguf",
        "filename": "nomic-embed-text-v1.5.Q4_K_M.gguf"
    }
}


# MODELS_DIR = Path("models")
MODELS_DIR = settings.get_models_path()

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
    parser = argparse.ArgumentParser(description="Download GGUF models")
    parser.add_argument("model", choices=["instruct", "thinking", "gemma3", "gemma3n", "qwen3", "qwen3-q8", "qwen3-think", "qwen3-think-q8", "mistral", "mistral-q8", "mistral-reason", "mistral-reason-q8", "llama3.2-1b", "llama3.2-1b-q8", "llama3.2-1b-spin", "llama-guard", "embed-gemma", "embed-nomic", "all"], help="Model to download")
    args = parser.parse_args()

    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

    models_to_download = [args.model] if args.model != "all" else ["instruct", "thinking", "gemma3", "gemma3n", "qwen3", "qwen3-think", "mistral", "mistral-reason", "llama3.2-1b", "embed-gemma"]

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
