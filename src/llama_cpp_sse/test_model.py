import argparse
import subprocess
import sys
import os
from pathlib import Path

# Constants
DEPS_DIR = Path("deps")
MODELS_DIR = Path("models")

BACKEND_MAP = {
    "cpu": DEPS_DIR / "llama_cpp_cpu" / "llama-cli.exe",
    "cuda": DEPS_DIR / "llama_cpp_cuda" / "llama-cli.exe",
    "vulkan": DEPS_DIR / "llama_cpp_vulkan" / "llama-cli.exe"
}

MODELS = {
    "instruct": "LFM2.5-1.2B-Instruct-Q4_K_M.gguf",
    "thinking": "LFM2.5-1.2B-Thinking-Q4_K_M.gguf"
}

PROMPTS = {
    "instruct": "Hello! Who are you?",
    "thinking": "Solve this logic puzzle: If A is older than B, and B is older than C, who is the youngest?"
}

def run_test(model_key, backend):
    if model_key not in MODELS:
        print(f"Error: Unknown model '{model_key}'. Available: {list(MODELS.keys())}")
        sys.exit(1)

    model_file = MODELS_DIR / MODELS[model_key]
    if not model_file.exists():
        print(f"Error: Model file '{model_file}' not found. Please run 'uv run download-models {model_key}' first.")
        sys.exit(1)

    cli_path = BACKEND_MAP.get(backend)
    if not cli_path or not cli_path.exists():
        print(f"Error: llama-cli.exe not found for backend '{backend}' at '{cli_path}'.")
        print(f"Please run 'uv run download-bin --backend {backend}' first.")
        sys.exit(1)

    prompt = PROMPTS[model_key]
    print(f"--- Testing {model_key} model with {backend} backend ---")
    print(f"Model: {model_file}")
    print(f"CLI: {cli_path}")
    print(f"Prompt: {prompt}")
    print("-" * 30)

    # For CUDA/Vulkan, we might need to ensure the directory is in the DLL search path on Windows
    # But usually llama.cpp handles this if DLLs are next to the exe.
    
    cmd = [
        str(cli_path),
        "-m", str(model_file),
        "-p", prompt,
        "-n", "64",
        "-c", "512",
        "--temp", "0.7"
    ]

    # Add extra args based on backend if needed
    if backend == "cuda":
        cmd.extend(["-ngl", "99"]) # Offload all layers to GPU
    elif backend == "vulkan":
        cmd.extend(["-ngl", "99"]) # Offload all layers to GPU

    try:
        # Run the command and stream output
        result = subprocess.run(cmd, check=True, text=True, capture_output=False)
        print("\n" + "-" * 30)
        print(f"Test finished with exit code {result.returncode}")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError running model: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(130)

def main():
    parser = argparse.ArgumentParser(description="Test LiquidAI models with llama-cli")
    parser.add_argument("model", choices=["instruct", "thinking"], help="Model to test")
    parser.add_argument("--backend", choices=["cpu", "cuda", "vulkan"], default="cpu", help="Backend to use")
    args = parser.parse_args()

    run_test(args.model, args.backend)

if __name__ == "__main__":
    main()
