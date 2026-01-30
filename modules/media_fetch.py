import os
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")


def fetch_pexels_videos(keyword: str, per_page: int = 5) -> List[dict]:
    """Fetch videos from Pexels."""
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": keyword,
        "per_page": per_page,
        "orientation": "landscape"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            videos = []
            for video in data.get("videos", []):
                # Get smallest HD file
                video_files = [f for f in video.get("video_files", []) if f.get("quality") in ["sd", "hd"]]
                if video_files:
                    video_files.sort(key=lambda x: x.get("width", 0))
                    videos.append({
                        "url": video_files[0]["link"],
                        "id": video["id"]
                    })
            return videos
    except Exception as e:
        print(f"Pexels error: {e}")
    
    return []


def fetch_pixabay_videos(keyword: str, per_page: int = 5) -> List[dict]:
    """Fetch videos from Pixabay."""
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": keyword,
        "per_page": per_page
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            videos = []
            for video in data.get("hits", []):
                videos.append({
                    "url": video["videos"]["small"]["url"],
                    "id": video["id"]
                })
            return videos
    except Exception as e:
        print(f"Pixabay error: {e}")
    
    return []


def download_video(url: str, output_path: str) -> bool:
    """Download video from URL."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Download error: {e}")
    return False


def fetch_videos_for_keywords(keywords: List[str], output_dir: str) -> List[str]:
    """Fetch and download videos for all keywords."""
    os.makedirs(output_dir, exist_ok=True)
    downloaded = []
    
    for i, keyword in enumerate(keywords):
        # Try Pexels first
        videos = fetch_pexels_videos(keyword, per_page=3)
        
        # If no results, try Pixabay
        if not videos:
            videos = fetch_pixabay_videos(keyword, per_page=3)
        
        # Download first video for this keyword
        if videos:
            output_path = os.path.join(output_dir, f"clip_{i}.mp4")
            if download_video(videos[0]["url"], output_path):
                downloaded.append(output_path)
        
        if len(downloaded) >= 4:  # Max 4 clips
            break
    
    return downloaded
