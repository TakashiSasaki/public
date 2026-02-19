import sys
import platform
import subprocess
import os

def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except FileNotFoundError:
        return None, "Command not found", -1
    except Exception as e:
        return None, str(e), -1

def main():
    print(f"Python Info: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")

    print("\n--- CUDA Check (nvidia-smi) ---")
    out, err, code = run_command(["nvidia-smi"])
    if code == 0:
        print("CUDA available via nvidia-smi:")
        # print only first few lines to avoid spam
        print("\n".join(out.splitlines()[:10]))
    else:
        print(f"nvidia-smi check failed: {err}")

    print("\n--- Vulkan Check (vulkaninfo) ---")
    out, err, code = run_command(["vulkaninfo"])
    if code == 0:
        print("Vulkan available via vulkaninfo:")
        print("\n".join(out.splitlines()[:10]))
    else:
        print(f"vulkaninfo check failed: {err}")

    print("\n--- Environment Variables (GPU related) ---")
    for key, val in os.environ.items():
        if any(k in key.upper() for k in ["CUDA", "VULKAN", "NVIDIA", "AMD", "INTEL"]):
            print(f"{key}: {val}")

    print("\n--- HOME vs USERPROFILE Check ---")
    home = os.environ.get("HOME")
    userprofile = os.environ.get("USERPROFILE")
    print(f"HOME: {home}")
    print(f"USERPROFILE: {userprofile}")
    if home and userprofile and home.lower() == userprofile.lower():
        print("MATCH: HOME is consistent with USERPROFILE.")
    elif not home and userprofile:
        print("WARNING: HOME is not set, but USERPROFILE is set.")
    else:
        print("MISMATCH: HOME and USERPROFILE differ or are missing!")

if __name__ == "__main__":
    main()
