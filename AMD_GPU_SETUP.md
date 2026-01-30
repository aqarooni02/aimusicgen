# AMD GPU Support Notes

## Current Situation
Your AMD Radeon RX 9070 XT is **detected** but **not accessible** in WSL2.

**Why?** 
- WSL2 doesn't have `/dev/kfd*` device (needed for AMD GPU access)
- WSL2 AMD GPU support is experimental and limited

**Detected Hardware:**
- GPU: AMD Radeon RX 9070 XT (gfx1201)
- CPU: AMD Ryzen 9 9900X

## Solutions

### Option 1: Use Native Linux (Recommended)
Run this directly on Linux (not WSL2) for full AMD GPU support.

### Option 2: Windows Native ROCm
Install ROCm 7.2 directly on Windows:

```bash
# Visit: https://repo.radeon.com/rocm/windows/rocm-rel-7.2/

# Requirements:
# - ROCm 7.2 for Windows
# - Visual Studio 2022 (C++ workload)
# - Python 3.13

# Install PyTorch with ROCm 7.2:
pip install torch torchaudio --pre --index-url https://rocm.nightlies.amd.com/v2/gfx120X-all/torch
```

### Option 3: Use CPU (Current)
The app will work, but music generation will be slower.

## Testing GPU Access

```bash
# Check if GPU is accessible
python -c "import torch; print(f'GPU available: {torch.cuda.is_available()}')"

# Check ROCm status
rocminfo | grep -i "Radeon\|gfx"

# Check device files (should exist for GPU access)
ls -la /dev/kfd* /dev/dri/
```

## WSL2 AMD GPU Passthrough

Currently, WSL2 does not support full AMD GPU passthrough. Only NVIDIA GPUs work well in WSL2.

For AMD GPUs, you need to use:
1. Native Linux installation
2. Windows ROCm (Windows native, not WSL2)
3. Wait for future WSL2 updates
