import os
import wave
import json
import vosk
from pydub import AudioSegment

from fastapi import FastAPI
from pydantic import BaseModel
import whisper

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
    try:
        # Load and process audio
        audio = whisper.load_audio(request.audio_path)
        audio = whisper.pad_or_trim(audio)

        # Convert to Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # Detect language
        # _, probs = model.detect_language(mel)
        # detected_language = max(probs, key=probs.get)

        # Decode the audio
        options = whisper.DecodingOptions()
        result = whisper.decode(model, mel, options)

        return {"detected_language": detected_language, "transcription": result.text}

    except Exception as e:
        return {"error": str(e)}


class SpeechToText:
    audio_data = {}
    def __init__(self, model_type="base"):

        self.model = whisper.load_model(model_type)

    def trim_audio(audio_path):
        audio = whisper.load_audio(audio_path)
        # audio = whisper.pad_or_trim(audio)
        count = 1
        while audio != None:
            audio = whisper.pad_or_trim(audio)
            audio_data = {count: audio}
            count += 1

        return audio, audio_data

    def transcribe_audio(self, audio_path):
        """Transcribes speech from an audio file using Vosk."""
        audio_path = self.ensure_wav_format(audio_path)

        with wave.open(audio_path, "rb") as wf:
            recognizer = vosk.KaldiRecognizer(self.model, wf.getframerate())
            text_result = ""

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    text_result += json.loads(recognizer.Result())["text"] + " "

            text_result += json.loads(recognizer.FinalResult())["text"]

        return text_result.strip()


# Example usage
if __name__ == "__main__":
    model_path = "vosk-model-small-en-us-0.15" 
    audio_file = "usecase.wav"  

    stt = SpeechToText(model_path)
    transcript = stt.transcribe_audio(audio_file)
    print("Transcription:\n", transcript)
