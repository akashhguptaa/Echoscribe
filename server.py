from fastapi import FastAPI
from pydantic import BaseModel
import whisper
import json

app = FastAPI()

# Load Whisper model once at startup
model = whisper.load_model("base")


# Define a request schema
class TranscriptionRequest(BaseModel):
    audio_path: str


@app.get("/")
def health_check():
    return {"message": "STT Model Server is Running"}


@app.post("/transcribe/")
def transcribe(request: TranscriptionRequest):
    print("andar to hoon")
    try:
        # Load and process audio
        print("bhai kamse kam try toh hua")
        audio = whisper.load_audio(request.audio_path)
        # audio = whisper.pad_or_trim(audio)
        count = 1
        print(type(audio))
        while not audio.size == 0:
            print("atlease while loop me aa gaya")
            audio = whisper.pad_or_trim(audio)
            audio_data = {count: audio}
            count += 1
            print("bro im in while loop")

        # Convert to Mel spectrogram
        for key, val in audio_data.items():
            mel = whisper.log_mel_spectrogram(val).to(model.device)
            audio_data[key] = mel

        # Detect language
        # _, probs = model.detect_language(mel)
        # detected_language = max(probs, key=probs.get)

        # Decode the audio
        options = whisper.DecodingOptions()
        for key, val in audio_data:

            result = whisper.decode(model, val, options)
            audio_data[key] = result.text
            print(result.text)

        return {
            # "detected_language": detected_language,
            "transcription": json(audio_data)
        }

    except Exception as e:
        print("last error bro")
        return {"error": str(e)}
