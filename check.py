import requests

BASE_URL = "http://127.0.0.1:8000"

def transcribe_audio(audio_path):
    response = requests.post(
        f"{BASE_URL}/transcribe/",
        json={"audio_path": audio_path}  # Send as JSON, not query params
    )
    
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Error:", response.json())

if __name__ == "__main__":
    audio_file = "usecase.mp3"
    transcribe_audio(audio_file)
