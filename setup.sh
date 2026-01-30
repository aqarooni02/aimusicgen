#!/bin/bash

# AI Music Video Generator - Setup Script with Python venv
# Supports both AMD (ROCm) and NVIDIA (CUDA) GPUs
# Run this script to set up the virtual environment and install dependencies

set -e  # Exit on error

echo "🎵 AI Music Video Generator Setup"
echo "=================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check for Python 3.13 for ROCm 7.2
PYTHON_CMD="python3"
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
    PYTHON_VERSION="3.13"
    echo "✅ Python 3.13 found - will use for ROCm 7.2 nightly builds"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
    PYTHON_VERSION="3.10"
    echo "⚠️  Python 3.10 found - will install ROCm 6.2 (for Python 3.13+ and ROCm 7.2, install: sudo apt install python3.13 python3.13-venv)"
else
    PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+')
fi

REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "❌ Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Using Python: $PYTHON_VERSION"

echo "✅ Python version: $PYTHON_VERSION"

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing FFmpeg..."
    sudo apt update && sudo apt install ffmpeg -y
fi

echo "✅ FFmpeg installed"

# Detect GPU (with manual override support)
echo ""
echo "🔍 Detecting GPU..."

# Check for manual override first
if [ -n "$FORCE_GPU" ]; then
    GPU_TYPE="$FORCE_GPU"
    echo "📝 Manual override: Using $GPU_TYPE (from FORCE_GPU environment variable)"
else
    # Auto-detect GPU
    GPU_TYPE=""
    
    # Method 1: Check for nvidia-smi (NVIDIA)
    if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
        GPU_TYPE="NVIDIA"
        echo "🔥 NVIDIA GPU detected (nvidia-smi) - will use CUDA"
    # Method 2: Check for ROCm/HIP
    elif command -v rocminfo &> /dev/null && rocminfo &> /dev/null 2>&1 | grep -q "GPU"; then
        GPU_TYPE="AMD"
        echo "🔥 AMD GPU detected (rocminfo) - will use ROCm"
    # Method 3: Check /proc for GPU info (WSL2)
    elif [ -f "/proc/driver/nvidia/version" ]; then
        GPU_TYPE="NVIDIA"
        echo "🔥 NVIDIA GPU detected (/proc/driver) - will use CUDA"
    # Method 4: Check for DirectX GPU info on WSL
    elif [ -f "/proc/sys/kernel/osrelease" ] && grep -q "WSL" /proc/sys/kernel/osrelease 2>/dev/null; then
        echo "⚠️  WSL2 detected but GPU not clearly identified"
        echo "   Common WSL2 GPUs:"
        echo "   - AMD Radeon: Uses ROCm"
        echo "   - NVIDIA GeForce/RTX: Uses CUDA"
        echo ""
        
        # Ask user
        echo "   Please select your GPU type:"
        echo ""
        echo "   1) AMD (ROCm) - Radeon RX series"
        echo "   2) NVIDIA (CUDA) - GeForce/RTX series"
        echo "   3) CPU only (no GPU)"
        echo ""
        
        read -p "   Enter choice (1-3): " gpu_choice
        
        case $gpu_choice in
            1) GPU_TYPE="AMD"; echo "🔥 Selected: AMD GPU with ROCm" ;;
            2) GPU_TYPE="NVIDIA"; echo "🔥 Selected: NVIDIA GPU with CUDA" ;;
            3) GPU_TYPE="CPU"; echo "⚠️  Selected: CPU only" ;;
            *) GPU_TYPE="CPU"; echo "⚠️  Invalid choice, defaulting to CPU" ;;
        esac
    else
        GPU_TYPE="CPU"
        echo "⚠️  No GPU detected - will use CPU (slower)"
        echo ""
        echo "   If you have a GPU, you can force it with:"
        echo "   FORCE_GPU=AMD ./setup.sh    # For AMD GPUs"
        echo "   FORCE_GPU=NVIDIA ./setup.sh # For NVIDIA GPUs"
    fi
fi

# Create virtual environment
echo ""
echo "🔧 Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists. Recreating..."
    rm -rf venv
fi

$PYTHON_CMD -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "🚀 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install base requirements first (without torch)
echo ""
echo "📥 Installing base dependencies..."
pip install fastapi uvicorn python-multipart websockets transformers moviepy librosa openai requests Pillow python-dotenv accelerate soundfile

# Install PyTorch based on GPU type
echo ""
if [ "$GPU_TYPE" = "AMD" ]; then
    echo "🔥 Installing PyTorch with ROCm support for AMD GPU..."
    echo "   Using AMD nightly builds for gfx120X (RX 7000 series)..."
    echo "   This may take 10-15 minutes..."
    echo ""
    
    # Check Python version for ROCm 7.2 (requires Python 3.13+)
    if [ "$PYTHON_VERSION" = "3.13" ]; then
        echo "✅ Python 3.13+ detected - installing ROCm 7.2 nightly builds"
        pip uninstall torch torchaudio torchvision -y 2>/dev/null || true
        pip install torch torchaudio --pre --index-url https://rocm.nightlies.amd.com/v2/gfx120X-all/torch
    else
        echo "⚠️  Python $PYTHON_VERSION detected, but ROCm 7.2 requires Python 3.13+"
        echo "   Falling back to ROCm 6.2 stable builds..."
        pip uninstall torch torchaudio torchvision -y 2>/dev/null || true
        pip install torch torchaudio --index-url https://download.pytorch.org/whl/rocm6.2
    fi
    
    echo ""
    echo "✅ ROCm PyTorch installed"
    echo ""
    
    # Verify ROCm installation
    echo "🧪 Verifying ROCm installation..."
    python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA/ROCm available: {torch.cuda.is_available()}'); print(f'Device count: {torch.cuda.device_count()}'); print(f'Device name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')" || echo "⚠️  ROCm verification failed - will use CPU fallback"
    
elif [ "$GPU_TYPE" = "NVIDIA" ]; then
    echo "🔥 Installing PyTorch with CUDA support..."
    echo "   This may take 10-15 minutes..."
    
    # Uninstall any existing torch to avoid conflicts
    pip uninstall torch torchaudio torchvision -y 2>/dev/null || true
    
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
    
    echo ""
    echo "✅ CUDA PyTorch installed"
    echo ""
    
    # Verify CUDA installation
    echo "🧪 Verifying CUDA installation..."
    python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')" || echo "⚠️  CUDA verification failed - will use CPU fallback"
    
else
    echo "⚠️  Installing PyTorch for CPU only..."
    
    # Uninstall any existing torch to avoid conflicts
    pip uninstall torch torchaudio torchvision -y 2>/dev/null || true
    
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
    
    echo ""
    echo "✅ CPU PyTorch installed"
fi

echo ""
echo "✅ PyTorch installation complete!"

# Final test
echo ""
echo "🧪 Testing all imports..."
python -c "import torch; import transformers; import moviepy; import librosa; print('✅ All imports successful!')"

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo "=================================="
echo ""
echo "📝 Next steps:"
echo "   1. Copy .env.example to .env and add your API keys:"
echo "      cp .env.example .env"
echo "      nano .env"
echo ""
echo "   2. Activate the virtual environment (if not already active):"
echo "      source venv/bin/activate"
echo ""
echo "   3. Run the application:"
echo "      python app.py"
echo ""
echo "   4. Open your browser and go to: http://localhost:8000"
echo ""

if [ "$GPU_TYPE" = "AMD" ]; then
    echo "🎮 GPU Info: AMD GPU with ROCm support"
    echo "   First music generation will download MusicGen model (~2GB)"
    echo ""
    echo "💡 Tip: If ROCm doesn't work, you can force CPU mode:"
    echo "      FORCE_GPU=CPU ./setup.sh"
    echo ""
elif [ "$GPU_TYPE" = "NVIDIA" ]; then
    echo "🎮 GPU Info: NVIDIA GPU with CUDA support"
    echo "   First music generation will download MusicGen model (~2GB)"
    echo ""
fi

echo "🎬 Happy music video making!"
echo ""
echo "📚 Troubleshooting:"
echo "   - If setup fails, check README.md"
echo "   - For AMD GPUs: FORCE_GPU=AMD ./setup.sh"
echo "   - For NVIDIA GPUs: FORCE_GPU=NVIDIA ./setup.sh"
echo "   - For CPU only: FORCE_GPU=CPU ./setup.sh"
