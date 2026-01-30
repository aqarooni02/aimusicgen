# AI Music Video Generator

A simple web app that generates 30-second music videos with AI-generated lyrics, music, and stock footage.

**Now using GPT-5 Nano** for fast, cost-effective lyrics generation!

## Features

- 🎤 **AI Lyrics**: GPT-5 Nano generates creative song lyrics from your theme
- 🎵 **AI Music**: Facebook MusicGen (local, free) creates unique 30-second songs
- 🎬 **Stock Footage**: Automatically fetches relevant video clips from Pexels/Pixabay
- ✂️ **Auto-Editing**: MoviePy syncs video cuts to music beats with lyrics overlay

## Quick Setup (with Python venv)

### 1. Get API Keys (all free)

- **OpenAI**: https://platform.openai.com/api-keys (for GPT-5 Nano)
- **Pexels**: https://www.pexels.com/api/ 
- **Pixabay**: https://pixabay.com/api/docs/

### 2. Run Setup Script

```bash
cd ai-music-video
chmod +x setup.sh
./setup.sh
```

This will:
- ✅ Check Python version (3.8+ required)
- ✅ Install FFmpeg if missing
- ✅ **Auto-detect your GPU** (AMD ROCm / NVIDIA CUDA / CPU)
- ✅ Create Python virtual environment (`venv/`)
- ✅ Install PyTorch with appropriate GPU support
- ✅ Install all dependencies

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Add your API keys
```

### 4. Run the App

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Start the server
python app.py
```

### 5. Open Browser

Go to: **http://localhost:8000**

## Usage

1. Enter a theme (e.g., "sunset love", "city nightlife", "mountain adventure")
2. Click **"Generate Music Video"**
3. Watch progress in real-time:
   - Step 1: GPT-5 Nano generates lyrics
   - Step 2: MusicGen creates the song (30 seconds)
   - Step 3: Fetch stock video clips
   - Step 4: Edit final music video with beat-synced cuts
4. **Download** your MP4!

## File Structure

```
ai-music-video/
├── venv/                   # Python virtual environment
├── app.py                  # FastAPI server
├── setup.sh               # Automated setup script
├── requirements.txt       # Python dependencies
├── .env                   # API keys (you create this)
├── .env.example          # Template for .env
├── modules/
│   ├── lyrics_gen.py     # GPT-5 Nano integration
│   ├── music_gen.py      # MusicGen (local AI)
│   ├── media_fetch.py    # Pexels/Pixabay APIs
│   └── video_edit.py     # MoviePy video editing
├── static/               # Web UI files
│   ├── index.html
│   ├── style.css
│   └── app.js
├── output/              # Generated videos (auto-created)
└── README.md
```

## Manual Setup (without script)

If you prefer to set up manually:

```bash
# Install system dependencies
sudo apt update && sudo apt install ffmpeg -y

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Configure and run
cp .env.example .env
# Edit .env with your keys
python app.py
```

## Requirements

- **OS**: WSL2 Kali Linux (or any Linux/macOS with ROCm support)
- **Python**: 3.8 or higher
- **RAM**: 8GB+ recommended (MusicGen needs ~4GB)
- **Storage**: ~3GB for AI model + generated videos
- **Network**: Internet connection for API calls
- **GPU**: AMD (ROCm), NVIDIA (CUDA), or CPU fallback

## GPU Support

The setup script auto-detects your GPU and installs the correct PyTorch version:

### AMD GPUs (ROCm)
- **Auto-installs**: PyTorch from `https://rocm.nightlies.amd.com/v2/gfx120X-all/`
- **Supports**: gfx120X architecture (RX 7000 series and newer)
- **Speed**: 5-10x faster than CPU for music generation
- **Install time**: ~5-10 minutes for ROCm PyTorch

### NVIDIA GPUs (CUDA)
- **Auto-installs**: PyTorch with CUDA 12.1 support
- **Speed**: 5-10x faster than CPU

### CPU Only
- **Works**: Yes, but slower (~2-3 min per song vs 20-30 sec on GPU)
- **Use case**: Fallback if no GPU detected

### WSL2 GPU Detection
On WSL2, automatic GPU detection may not work perfectly. The setup script will:
1. Try to auto-detect using available tools
2. If unclear, ask you to manually select your GPU type
3. Or you can force GPU type with environment variable

### Force GPU Type (Manual Override)
If auto-detection fails or you want to override:

```bash
# For AMD GPUs (ROCm)
FORCE_GPU=AMD ./setup.sh

# For NVIDIA GPUs (CUDA)  
FORCE_GPU=NVIDIA ./setup.sh

# For CPU only (no GPU)
FORCE_GPU=CPU ./setup.sh
```

## Model Details

### GPT-5 Nano
- **Speed**: Fastest GPT-5 variant
- **Cost**: $0.05/1M input tokens, $0.40/1M output tokens
- **Use case**: Perfect for quick lyrics generation
- **Context**: 400K tokens
- **Output**: 128K max tokens
- **Note**: Only supports default temperature (1)

### MusicGen
- **Local**: Runs entirely on your machine (no API costs)
- **Size**: ~2GB model download (one-time)
- **Speed**: ~1-2 min per 30s song on CPU
- **GPU**: Optional (faster with CUDA/ROCm)

## Verify GPU is Working

After setup, verify your GPU is being used:

```bash
source venv/bin/activate
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}'); print(f'Available: {torch.cuda.is_available()}')"
```

Expected output for AMD:
```
GPU: AMD Radeon RX 7900 XT
Available: True
```

Expected output for NVIDIA:
```
GPU: NVIDIA GeForce RTX 4080
Available: True
```

Expected output for CPU:
```
GPU: CPU
Available: False
```

## Troubleshooting

### "No module named 'xxx'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### AMD GPU not detected
```bash
# Check if ROCm is available
rocminfo

# If ROCm not installed on WSL2:
sudo apt install rocminfo

# Re-run setup
./setup.sh
```

### ROCm PyTorch installation fails
```bash
# Manual install for AMD GPU
source venv/bin/activate
pip uninstall torch torchaudio -y
pip install --pre torch torchaudio --index-url https://rocm.nightlies.amd.com/v2/gfx120X-all/

# Verify installation
python -c "import torch; print(f'ROCm: {torch.cuda.is_available()}')"
```

### MoviePy import errors
If you get `ModuleNotFoundError: No module named 'moviepy.editor'`:
- You have MoviePy 2.x installed, which uses different imports
- The code has been updated to use MoviePy 2.x API (see `modules/video_edit.py`)

### MusicGen model download fails
```bash
# Pre-download manually
source venv/bin/activate
python -c "from transformers import AutoProcessor, MusicgenForConditionalGeneration; AutoProcessor.from_pretrained('facebook/musicgen-small'); MusicgenForConditionalGeneration.from_pretrained('facebook/musicgen-small')"
```

### FFmpeg not found
```bash
sudo apt update && sudo apt install ffmpeg -y
```

### API rate limits
- Pexels: 200 requests/hour
- Pixabay: 100 requests/minute
- OpenAI: Check your tier limits

### GPU out of memory
```bash
# If GPU runs out of VRAM, the app will automatically fall back to CPU
# Or you can force CPU mode by setting:
export CUDA_VISIBLE_DEVICES=""
python app.py
```

## Deactivate Virtual Environment

When done:
```bash
deactivate
```

## Clean Up

To remove everything:
```bash
deactivate  # If venv is active
rm -rf venv/
rm -rf output/
```

## License

MIT - Feel free to use and modify!
