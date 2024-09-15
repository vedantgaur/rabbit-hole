import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

SUNO_API_KEY = os.getenv('SUNO_API_KEY')
SUNO_API_URL = 'https://api.suno.ai/generate'  # Placeholder URL

def generate_music_snippet(query):
    headers = {
        'Authorization': f'Bearer {SUNO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'prompt': query,
        'duration': 30,  # Generate a 30-second snippet
        'style': 'adaptive'  # Assuming Suno has a style parameter
    }
    
    response = requests.post(SUNO_API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        # Assuming Suno returns a URL to the generated audio
        audio_url = response.json()['audio_url']
        
        # Download the audio file
        audio_response = requests.get(audio_url)
        if audio_response.status_code == 200:
            output_path = f"static/music/{query.replace(' ', '_')}.mp3"
            with open(output_path, 'wb') as f:
                f.write(audio_response.content)
            return output_path
        else:
            print(f"Failed to download audio: {audio_response.status_code}")
    else:
        print(f"Suno API request failed: {response.status_code}")
        print(response.text)
    
    return None  # Return None if generation or download fails