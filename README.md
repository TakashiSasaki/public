# llama-cpp-sse

This project provides utilities to set up and run `llama.cpp` with SSE4.x support on Windows, along with tools for downloading compatible models.

## Usage

This project uses `uv` for dependency management and script execution.

### 1. Environment Check
Check your system's Python version, GPU availability (CUDA/Vulkan), and CPU capabilities.
```bash
uv run check-env
```

### 2. SSE Support Check
Verify if your CPU supports SSE4.x instructions (required for the CPU binaries used in this project).
```bash
uv run check-sse
```

### 3. Download llama.cpp Binaries
Download the latest `llama.cpp` binaries for your desired backend. The binaries are extracted to the `deps/` directory.
```bash
# Default (CUDA)
uv run download-bin

# Specify backend
uv run download-bin --backend cuda
uv run download-bin --backend vulkan
uv run download-bin --backend cpu
```

### 4. Download Models
Download GGUF models (e.g., LiquidAI LFM2.5) to the `models/` directory.
```bash
# Download both Instruct and Thinking models
uv run download-models all

# Download specific model
uv run download-models instruct
uv run download-models thinking

### 5. Test Models
Verify that the downloaded models can be loaded and generate text using `llama.cpp`.
```bash
# Test Instruct model
uv run test-model instruct --backend cuda

# Test Thinking model
uv run test-model thinking --backend vulkan
```

### 6. GPU Memory Cleanup
If a process hangs or you want to ensure all GPU memory is released, run the cleanup script. This will forcefully terminate any lingering `llama-cli.exe` or `llama-server.exe` processes.
```bash
uv run cleanup-gpu
```
