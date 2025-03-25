import os
import base64
import numpy as np
import ssl
import asyncio
import json

from abc import ABC, abstractmethod
from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)
import whisper
import tempfile

from faster_whisper import WhisperModel
import soundfile as sf
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

ssl._create_default_https_context = ssl._create_unverified_context


class TranscriptionEngine(ABC):
    @abstractmethod
    def transcribe(self, audio_data: bytes):
        pass


class WhisperEngine(TranscriptionEngine):
    def __init__(self, model_name: str = "base.en"):

        self.model = whisper.load_model(model_name)

    async def transcribe(self, audio_data: bytes):
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                with sf.SoundFile(
                    temp_wav.name,
                    mode="w",
                    samplerate=16000,
                    channels=1,
                    subtype="PCM_16",
                ) as file:
                    file.write(np.frombuffer(audio_data, dtype=np.int16))

                result = self.model.transcribe(temp_wav.name)
            text = result.get("text", "")
            return text
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return ""


whisper_engine = WhisperEngine("base.en")
logger.info("VoscEngine initialized and will be used for websocket transcription.")


async def handle_transcriptions(
    audio_data: bytes, final_chunk: bool, file_key: str, websocket: WebSocket
):
    text = await whisper_engine.transcribe(audio_data)
    logger.info(f"Transcription for key {file_key}: {text}")
    response = {"key": file_key, "text": text, "final": final_chunk}
    # logger.debug(f"Sending response: {response}")
    await websocket.send_text(json.dumps(response))


@app.websocket("/ws/transcription")
async def websocket_transcription(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            file_key = message.get("key")
            chunk_base64 = message.get("chunk")
            final_chunk = message.get("final", False)

            if not file_key or not chunk_base64:
                await websocket.send_json(
                    {"error": "Invalid message: missing 'key' or 'chunk'."}
                )
                continue

            try:
                chunk_bytes = base64.b64decode(chunk_base64)
            except Exception as decode_err:
                logger.error(f"Decoding error for key {file_key}: {decode_err}")
                await websocket.send_json(
                    {"key": file_key, "error": "Failed to decode audio chunk."}
                )
                continue

            asyncio.create_task(
                handle_transcriptions(chunk_bytes, final_chunk, file_key, websocket)
            )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)