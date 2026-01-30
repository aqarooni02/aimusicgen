import os
import librosa
import numpy as np
from moviepy import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip
)


def analyze_beats(audio_path: str) -> list:
    """Detect beat timestamps in audio."""
    y, sr = librosa.load(audio_path, duration=30)
    
    # Get beat frames
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    
    # Convert to timestamps and ensure Python list
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # Ensure beat_times is a Python list
    if hasattr(beat_times, 'tolist'):
        beat_times = beat_times.tolist()
    
    # Add start and end
    beat_times = [0] + list(beat_times) + [30]
    
    return beat_times


def split_lyrics(lyrics: str, num_segments: int) -> list:
    """Split lyrics into segments."""
    lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
    
    # Group lines into segments
    segments = []
    lines_per_seg = max(1, len(lines) // num_segments)
    
    for i in range(0, len(lines), lines_per_seg):
        segment_lines = lines[i:i + lines_per_seg]
        segments.append(' '.join(segment_lines))
    
    return segments


def create_music_video(
    video_clips: list,
    audio_path: str,
    lyrics: str,
    output_path: str
) -> str:
    """Create final music video with lyrics overlay."""
    
    # Analyze beats
    beat_times = analyze_beats(audio_path)
    
    # Split lyrics
    num_clips = len(video_clips)
    lyric_segments = split_lyrics(lyrics, num_clips)
    
    # Ensure we have matching beats
    if len(beat_times) < num_clips + 1:
        # Create evenly spaced cuts
        beat_times = np.linspace(0, 30, num_clips + 1).tolist()
    
    # Process video clips
    final_clips = []
    
    for i, clip_path in enumerate(video_clips):
        if i >= len(lyric_segments):
            break
            
        try:
            # Load clip
            clip = VideoFileClip(clip_path)
            
            # Calculate duration for this segment
            start_time = beat_times[i]
            end_time = beat_times[min(i + 1, len(beat_times) - 1)]
            duration = end_time - start_time
            
            # Trim clip to duration (MoviePy 2.x uses subclipped)
            if clip.duration > duration:
                clip = clip.subclipped(0, duration)
            else:
                # Loop if too short
                clip = clip.loop(duration=duration)
            
            # Add fade effects (MoviePy 2.x API)
            clip = clip.with_fadein(0.5)
            clip = clip.with_fadeout(0.5)
            
            # Create text overlay
            text = lyric_segments[i]
            txt_clip = TextClip(
                text,
                fontsize=50,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2,
                size=(clip.w, None),
                method='caption'
            )
            txt_clip = txt_clip.with_duration(duration)
            txt_clip = txt_clip.with_position(('center', 'bottom'))
            txt_clip = txt_clip.with_margin(bottom=50, opacity=0)
            
            # Composite
            composite = CompositeVideoClip([clip, txt_clip])
            composite = composite.with_start(start_time)
            
            final_clips.append(composite)
            
        except Exception as e:
            print(f"Error processing clip {i}: {e}")
            continue
    
    if not final_clips:
        raise ValueError("No valid video clips to process")
    
    # Combine all clips
    final_video = CompositeVideoClip(final_clips, size=(1280, 720))
    
    # Add audio
    audio = AudioFileClip(audio_path)
    final_video = final_video.with_audio(audio)
    
    # Write output
    final_video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )
    
    # Cleanup
    for clip in final_clips:
        clip.close()
    audio.close()
    final_video.close()
    
    return output_path
