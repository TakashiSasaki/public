import platform
import subprocess
import sys
import os

try:
    import cpuinfo
except ImportError:
    print("Installing py-cpuinfo...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "py-cpuinfo"])
    import cpuinfo

def check_sse_support():
    print(f"Platform: {platform.system()} {platform.release()} ({platform.machine()})")
    
    info = cpuinfo.get_cpu_info()
    flags = info.get('flags', [])
    arch = info.get('arch', '').lower()
    
    print(f"CPU: {info.get('brand_raw', 'Unknown')}")
    print(f"Architecture: {arch}")
    
    sse_flags = [f for f in flags if 'sse' in f.lower()]
    avx_flags = [f for f in flags if 'avx' in f.lower()]
    
    print("\nSupported Extensions:")
    print(f"SSE: {', '.join(sse_flags) if sse_flags else 'None'}")
    print(f"AVX: {', '.join(avx_flags) if avx_flags else 'None'}")
    
    # Check specifically for SSE 4.x which is often required
    has_sse4_1 = 'sse4_1' in flags or 'sse4.1' in flags
    has_sse4_2 = 'sse4_2' in flags or 'sse4.2' in flags
    
    print("\n--- Compatibility Check ---")
    if has_sse4_2:
        print("✅ SSE 4.2 supported (Recommended for llama.cpp)")
    elif has_sse4_1:
        print("⚠️ SSE 4.1 supported (May work, but SSE 4.2 is preferred)")
    else:
        print("❌ SSE 4.x NOT supported. llama.cpp may fail or run very slowly.")

    # AVX check
    if 'avx2' in flags:
        print("✅ AVX2 supported (Good performance)")
    elif 'avx' in flags:
        print("✅ AVX supported")
    else:
        print("⚠️ AVX NOT supported")

def main():
    check_sse_support()

if __name__ == "__main__":
    main()
