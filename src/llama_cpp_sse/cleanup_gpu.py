import subprocess
import sys
import platform

def cleanup_gpu():
    print("Attempting to release GPU memory by terminating llama.cpp processes...")
    
    # Process names to look for
    process_names = ["llama-cli.exe", "llama-server.exe", "llama-bench.exe"]
    
    if platform.system() != "Windows":
        print("Cleanup script currently optimized for Windows.")
        return

    found = False
    for name in process_names:
        try:
            # taskkill /F /IM <name> /T (Force, Image Name, Tree)
            # 2>/dev/null in shell, but here we just check return code
            result = subprocess.run(
                ["taskkill", "/F", "/IM", name, "/T"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ Successfully terminated {name}")
                found = True
            elif "プロセスが見つかりませんでした" in result.stderr or "not found" in result.stderr.lower():
                # Silently ignore if not running
                pass
            else:
                # Some other error
                pass
        except Exception as e:
            print(f"Error terminating {name}: {e}")

    if not found:
        print("No active llama.cpp processes found. Memory should already be free.")
    else:
        print("Cleanup completed.")

def main():
    cleanup_gpu()

if __name__ == "__main__":
    main()
