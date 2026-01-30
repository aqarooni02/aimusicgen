import torch
import soundfile as sf
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import os

# Global model cache
_model = None
_processor = None

def load_model():
    """Load MusicGen model once."""
    global _model, _processor
    if _model is None:
        print("Loading MusicGen model... (first run, may take 2-3 minutes)")
        _processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        _model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
        
        # Check for GPU (CUDA or ROCm)
        print(f"PyTorch version: {torch.__version__}")
        print(f"ROCm/CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            print(f"Using GPU: {device_name}")
            _model = _model.to("cuda")
        else:
            print("⚠️  GPU not detected - using CPU (slower)")
            print("   Troubleshooting:")
            print("   1. Check if ROCm is installed: rocminfo")
            print("   2. Verify PyTorch was installed with ROCm: python -c 'import torch; print(torch.version.cuda)'")
            print("   3. Check GPU is accessible in WSL2")
            
    return _processor, _model

def generate_music(lyrics: str, output_path: str, duration: int = 30) -> str:
    """Generate music from lyrics using MusicGen."""
    processor, model = load_model()
    
    # Create prompt from lyrics
    prompt = f"A song with these lyrics: {lyrics}"
    
    # Generate
    inputs = processor(
        text=[prompt],
        padding=True,
        return_tensors="pt"
    )
    
    if torch.cuda.is_available():
        inputs = {k: v.to("cuda") for k, v in inputs.items()}
    
    # Generate 30 seconds (at 50 tokens/sec, 30 sec = 1500 tokens)
    max_tokens = int(duration * 50)
    
    with torch.no_grad():
        audio_values = model.generate(**inputs, max_new_tokens=max_tokens)
    
    # Save audio
    audio_data = audio_values[0, 0].cpu().numpy()
    sf.write(output_path, audio_data, samplerate=32000)
    
    return output_path
