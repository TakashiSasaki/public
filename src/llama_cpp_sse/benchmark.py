import argparse
import subprocess
import sys
import re
import time
from pathlib import Path

# Constants
DEPS_DIR = Path("deps")
MODELS_DIR = Path("models")

BACKEND_MAP = {
    "cpu": DEPS_DIR / "llama_cpp_cpu" / "llama-cli.exe",
    "cuda": DEPS_DIR / "llama_cpp_cuda" / "llama-cli.exe",
    "vulkan": DEPS_DIR / "llama_cpp_vulkan" / "llama-cli.exe"
}

MODEL_FILE = MODELS_DIR / "LFM2.5-1.2B-Instruct-Q4_K_M.gguf"
BENCHMARK_PROMPT = "Write a complete recipe for French Onion Soup. Start with the title and ingredient list."

def run_benchmark(backend, extra_args):
    if not MODEL_FILE.exists():
        print(f"Error: Model file '{MODEL_FILE}' not found. Please run 'uv run download-models instruct' first.")
        sys.exit(1)

    cli_path = BACKEND_MAP.get(backend)
    if not cli_path or not cli_path.exists():
        print(f"Error: llama-cli.exe not found for backend '{backend}' at '{cli_path}'.")
        print(f"Please run 'uv run download-bin --backend {backend}' first.")
        sys.exit(1)

    print(f"--- Running Benchmark: {backend.upper()} backend ---")
    print(f"Target: {BENCHMARK_PROMPT}")
    print("Wait for generation to complete (real-time output enabled)...")
    print("-" * 30)

    cmd = [
        str(cli_path),
        "-m", str(MODEL_FILE),
        "-p", BENCHMARK_PROMPT,
        "--no-display-prompt", # Cleaner output
        "--single-turn",       # Exit after first prompt turn
        "--ignore-eos"         # Force generation until limit is reached
    ]

    # Add defaults if not overridden by extra_args
    if not any(arg in extra_args for arg in ["-n", "--n-predict"]):
        cmd.extend(["-n", "4096"])
    
    if not any(arg in extra_args for arg in ["-c", "--ctx-size"]):
        cmd.extend(["-c", "8192"])

    if not any(arg in extra_args for arg in ["--temp"]):
        cmd.extend(["--temp", "0.7"])

    if backend in ["cuda", "vulkan"]:
        # Default offload if not overridden by extra_args
        if not any(arg in extra_args for arg in ["-ngl", "--n-gpu-layers"]):
            cmd.extend(["-ngl", "99"])

    if extra_args:
        cmd.extend(extra_args)

    start_time = time.time()
    merged_output = ""
    try:
        # Merge stderr into stdout to prevent deadlocks and capture all info in one stream
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            bufsize=1,
            universal_newlines=True
        )

        # Read everything in real-time
        while True:
            char = process.stdout.read(1)
            if not char and process.poll() is not None:
                break
            if char:
                print(char, end="", flush=True)
                merged_output += char

        process.wait()
        duration = time.time() - start_time
        
        print("\n" + "-" * 30)
        
        # Parse performance metrics from merged output
        perf_summary = {}
        
        eval_match = re.search(r"eval time\s+=\s+([\d\.]+)\s+ms\s+/\s+(\d+)\s+tokens\s+\(\s+[\d\.]+\s+ms\s+per\s+token,\s+([\d\.]+)\s+tokens\s+per\s+second\)", merged_output)
        if eval_match:
            perf_summary['ms'] = float(eval_match.group(1))
            perf_summary['tokens'] = int(eval_match.group(2))
            perf_summary['tps'] = float(eval_match.group(3))
            
        prompt_match = re.search(r"prompt eval time\s+=\s+([\d\.]+)\s+ms\s+/\s+(\d+)\s+tokens\s+\(\s+[\d\.]+\s+ms\s+per\s+token,\s+([\d\.]+)\s+tokens\s+per\s+second\)", merged_output)
        if prompt_match:
            perf_summary['prompt_ms'] = float(prompt_match.group(1))
            perf_summary['prompt_tokens'] = int(prompt_match.group(2))
            perf_summary['prompt_tps'] = float(prompt_match.group(3))

        if perf_summary:
            print(f"Benchmark Results:")
            print(f"  - Total Tokens Generated: {perf_summary.get('tokens', 'N/A')}")
            print(f"  - Generation Speed: {perf_summary.get('tps', 'N/A')} tokens/s")
            print(f"  - Prompt Eval: {perf_summary.get('prompt_tokens', 'N/A')} tokens @ {perf_summary.get('prompt_tps', 'N/A')} tokens/s")
            print(f"  - Total Execution Time: {duration:.2f} s")
        else:
            # If standard timings missing, try to parse the status line "[ Prompt: XXX.X t/s | Generation: YYY.Y t/s ]"
            status_match = re.search(r"\[\s+Prompt:\s+([\d\.]+)\s+t/s\s+\|\s+Generation:\s+([\d\.]+)\s+t/s\s+\]", merged_output)
            if status_match:
                print(f"Benchmark Results (from status line):")
                print(f"  - Generation Speed: {status_match.group(2)} tokens/s")
                print(f"  - Prompt Eval Speed: {status_match.group(1)} tokens/s")
                print(f"  - Total Execution Time: {duration:.2f} s")
            else:
                print("Warning: Could not parse detailed performance metrics from llama.cpp output.")
                print(f"Total Execution Time: {duration:.2f} s")
            
            if process.returncode != 0:
                print(f"Error: Process exited with code {process.returncode}")
                # print(merged_output) # For debugging
            
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user.")
        process.kill()
        sys.exit(130)
    except Exception as e:
        print(f"\nError during benchmark: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Non-interactive performance benchmark for llama-cpp-sse")
    parser.add_argument("--backend", choices=["cpu", "cuda", "vulkan"], default="cuda", help="Backend to use (default: cuda)")
    parser.add_argument("-ngl", "--n-gpu-layers", type=int, help="Number of layers to offload to GPU (overrides default)")
    args, extra_args = parser.parse_known_args()

    # Consolidate ngl into extra_args if provided
    if args.n_gpu_layers is not None:
        extra_args.extend(["-ngl", str(args.n_gpu_layers)])

    # Check if backend cli exists, fallback to cpu if cuda/vulkan missing
    if not BACKEND_MAP[args.backend].exists():
        print(f"Warning: {args.backend} binaries not found. Falling back to CPU for benchmark.")
        args.backend = "cpu"

    run_benchmark(args.backend, extra_args)

if __name__ == "__main__":
    main()
