import requests
import os
import time
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Suno cookie from .env
SUNO_COOKIE = os.getenv('SUNO_COOKIE')
SUNO_API_URL = 'https://suno.gcui.art/api/generate'  # Suno API endpoint

def generate_music_snippet(query):
    headers = {
        'Cookie': SUNO_COOKIE,
        'Content-Type': 'application/json'
    }
    
    data = {
        'prompt': query,
        'duration': 30,  # 30-second snippet
        'model_version': 'v3',
        'temperature': 1.0,
        'top_k': 250,
        'top_p': 0.99,
        'classifier_free_guidance': 3.0,
        'output_format': 'mp3',
        'sample_rate': 44100
    }
    
    print(f"Sending request to Suno API with data: {json.dumps(data, indent=2)}")
    
    # Make request to Suno API
    try:
        response = requests.post(SUNO_API_URL, headers=headers, json=data)
        print(f"API Response Status Code: {response.status_code}")
        print(f"API Response Content: {response.text}")
        
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Suno API: {e}")
        return None
    
    if response.status_code == 200:
        try:
            response_data = response.json()
            task_id = response_data.get('task_id')
            if task_id:
                print(f"Task ID received: {task_id}")
                # Poll for task completion
                status_url = f"{SUNO_API_URL}/status/{task_id}"
                poll_count = 0
                while True:
                    poll_count += 1
                    print(f"Polling attempt {poll_count} for task status...")
                    try:
                        status_response = requests.get(status_url, headers=headers)
                        print(f"Status Response Code: {status_response.status_code}")
                        print(f"Status Response Content: {status_response.text}")
                        
                        status_response.raise_for_status()
                        status_data = status_response.json()
                        
                        if status_data['status'] == 'completed':
                            audio_url = status_data['result']['audio_url']
                            print(f"Audio URL received: {audio_url}")
                            # Download and save the audio file
                            try:
                                audio_response = requests.get(audio_url)
                                audio_response.raise_for_status()
                                output_path = f"static/music/{query.replace(' ', '_')}.mp3"
                                with open(output_path, 'wb') as f:
                                    f.write(audio_response.content)
                                print(f"Audio file saved to: {output_path}")
                                return output_path
                            except requests.exceptions.RequestException as e:
                                print(f"Error downloading audio file: {e}")
                            break
                        elif status_data['status'] == 'failed':
                            print(f"Task failed. Error: {status_data.get('error', 'Unknown error')}")
                            break
                        else:
                            print(f"Task status: {status_data['status']}")
                    except requests.exceptions.RequestException as e:
                        print(f"Error polling task status: {e}")
                        break
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON response: {e}")
                        break
                    
                    time.sleep(5)  # Wait before polling again
            else:
                print("No task ID returned by the API.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
    else:
        print(f"Suno API request failed with status code: {response.status_code}")
    
    return None  # Return None if generation or download fails

if __name__ == "__main__":
    query = "calm piano music"  # Example prompt, change as needed
    music_file_path = generate_music_snippet(query)
    
    if music_file_path:
        print(f"Music snippet saved at: {music_file_path}")
    else:
        print("Failed to generate music snippet.")