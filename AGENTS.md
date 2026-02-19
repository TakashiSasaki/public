# AGENTS.md

This file is for logging findings, decisions, and important context for other agents.

## Environment Investigation
- Python: 3.12.12
- CUDA: Available (GTX 1060 6GB, CUDA 12.6/12.7)
- Vulkan: Available (User provided driver source: https://developer.nvidia.com/vulkan-driver)
- HOME vs USERPROFILE: `HOME` is not set. `USERPROFILE` is set to `C:\Users\takas`.

## Development Rules
- **Commit Messages**: MUST be detailed. Use `git commit -F commit_message.txt`.
- **Project Management**: Use `uv` for dependency and environment management.
- **Automation**: A git pre-commit hook automatically increments the patch version in `pyproject.toml` on every commit.
- **Environment Check**: Run `uv run check-env` to verify system capabilities.
- **Dependencies**: Use `uv run download-bin --backend [cuda|vulkan|cpu]` to download `llama.cpp` binaries to `deps/llama_cpp_[backend]/`. Default is `cuda`.
- **SSE Check**: Run `uv run check-sse` to verify CPU SSE/AVX support.
    - *Finding*: System supports SSE 4.2. AVX is not supported.
- **Models**: Use `uv run download-models [instruct|thinking|all]` to download LiquidAI LFM2.5 GGUF models to `models/`.
    - *Models*: `LiquidAI/LFM2.5-1.2B-Instruct` and `LiquidAI/LFM2.5-1.2B-Thinking`.
    - *Quantization*: Q4_K_M is used for balance of size and performance.
- **Testing**: Use `uv run test-model [instruct|thinking] [--backend cpu|cuda|vulkan]` to verify model execution via `llama-cli`.
    - *Benchmarks (LFM2.5-1.2B)*:
        - **CUDA**: ~103 t/s (Fastest)
        - **Vulkan**: ~65 t/s
        - **CPU**: ~6.7 t/s
- **Maintenance**: Use `uv run cleanup-gpu` to kill lingering llama.cpp processes and free VRAM.

