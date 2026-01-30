from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import asyncio
import json
from datetime import datetime

from modules.lyrics_gen import generate_lyrics
from modules.music_gen import generate_music
from modules.media_fetch import fetch_videos_for_keywords
from modules.video_edit import create_music_video

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure output directory exists
os.makedirs("output", exist_ok=True)


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Receive theme
        data = await websocket.receive_text()
        request = json.loads(data)
        theme = request.get("theme", "")
        
        if not theme:
            await websocket.send_json({"error": "No theme provided"})
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Step 1: Generate lyrics
        await websocket.send_json({"step": 1, "status": "Generating lyrics..."})
        try:
            result = generate_lyrics(theme)
            lyrics = result["lyrics"]
            keywords = result["keywords"]
            await websocket.send_json({
                "step": 1, 
                "status": "Lyrics generated", 
                "lyrics": lyrics,
                "keywords": keywords
            })
        except Exception as e:
            await websocket.send_json({"step": 1, "status": f"Error: {str(e)}"})
            return
        
        # Step 2: Generate music
        await websocket.send_json({"step": 2, "status": "Creating song with MusicGen..."})
        audio_path = f"output/audio_{timestamp}.wav"
        try:
            generate_music(lyrics, audio_path, duration=30)
            await websocket.send_json({"step": 2, "status": "Song created"})
        except Exception as e:
            await websocket.send_json({"step": 2, "status": f"Error: {str(e)}"})
            return
        
        # Step 3: Fetch video clips
        await websocket.send_json({"step": 3, "status": "Fetching stock video clips..."})
        clips_dir = f"output/clips_{timestamp}"
        try:
            video_clips = fetch_videos_for_keywords(keywords, clips_dir)
            if not video_clips:
                await websocket.send_json({"step": 3, "status": "No clips found, retrying with theme..."})
                video_clips = fetch_videos_for_keywords([theme], clips_dir)
            
            if not video_clips:
                await websocket.send_json({"step": 3, "status": "Error: No video clips available"})
                return
                
            await websocket.send_json({"step": 3, "status": f"Found {len(video_clips)} clips"})
        except Exception as e:
            await websocket.send_json({"step": 3, "status": f"Error: {str(e)}"})
            return
        
        # Step 4: Create music video
        await websocket.send_json({"step": 4, "status": "Editing music video..."})
        output_path = f"output/video_{timestamp}.mp4"
        try:
            create_music_video(video_clips, audio_path, lyrics, output_path)
            
            # Get file size
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            
            await websocket.send_json({
                "step": 4, 
                "status": "Complete!",
                "video_url": f"/download/video_{timestamp}.mp4",
                "file_size": f"{file_size:.1f} MB"
            })
        except Exception as e:
            await websocket.send_json({"step": 4, "status": f"Error: {str(e)}"})
            return
        
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()


@app.get("/download/{filename}")
async def download(filename: str):
    file_path = f"output/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=filename)
    return {"error": "File not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
