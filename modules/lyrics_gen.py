import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_lyrics(theme: str) -> dict:
    """Generate song lyrics and keywords from theme."""
    
    # Generate lyrics
    lyrics_prompt = f"""Write original song lyrics (4-6 lines) about: {theme}
Make it emotional and suitable for a 30-second song.
Return ONLY the lyrics, no explanations."""
    
    lyrics_response = openai.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a creative songwriter."},
            {"role": "user", "content": lyrics_prompt}
        ],
        max_completion_tokens=200
    )
    
    lyrics = lyrics_response.choices[0].message.content.strip()
    
    # Generate search keywords
    keywords_prompt = f"""Based on these lyrics, provide 3-4 visual keywords for stock video search.
Lyrics: {lyrics}
Return ONLY comma-separated keywords, no other text."""
    
    keywords_response = openai.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You extract visual keywords."},
            {"role": "user", "content": keywords_prompt}
        ],
        max_completion_tokens=50
    )
    
    keywords_text = keywords_response.choices[0].message.content.strip()
    keywords = [k.strip() for k in keywords_text.split(",")]
    
    return {
        "lyrics": lyrics,
        "keywords": keywords
    }
