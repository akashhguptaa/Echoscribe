import os
import base64
import numpy as np
import ssl
import asyncio
import concurrent.futures
from abc import ABC, abstractmethod
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import whisper
from loguru import logger
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()
app = FastAPI()
ssl._create_default_https_context = ssl._create_unverified_context

# Configure thread pool
MAX_WORKERS = os.cpu_count() or 4
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
logger.info(f"Initialized thread pool with {MAX_WORKERS} workers")

# Cache for storing audio chunks by session
chunk_cache: Dict[str, List[bytes]] = {}
# Cache for storing transcribed text by session
transcription_cache: Dict[str, str] = {}

class TranscriptionEngine(ABC):
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        pass

    @abstractmethod
    async def transcribe_stream(self, audio_data: List[bytes]) -> str:
        pass

class WhisperEngine(TranscriptionEngine):
    def __init__(self, model_name: str = "base.en"):
        logger.info(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        logger.info(f"Whisper model {model_name} loaded successfully")
    
    async def transcribe(self, audio_data: bytes) -> str:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            thread_pool, self._transcribe_stream_in_thread, [audio_data]
        )
        return result.get("text", "")
    
    def _transcribe_stream_in_thread(self, audio_data_list: List[bytes]) -> Dict[str, Any]:
        try:
            all_audio = b''.join(audio_data_list)
            
            if not all_audio:
                logger.warning("Received empty audio data, skipping transcription.")
                return {"text": ""}

            audio_np = np.frombuffer(all_audio, dtype=np.int16)
            
            if audio_np.size == 0:
                logger.warning("Converted audio data is empty, skipping transcription.")
                return {"text": ""}

            logger.info(f"Audio NumPy array shape: {audio_np.shape}, dtype: {audio_np.dtype}")

            audio_np = audio_np.astype(np.float32) / 32768.0

            logger.info(f"Normalized audio shape: {audio_np.shape}, min: {audio_np.min()}, max: {audio_np.max()}")

            result = self.model.transcribe(audio_np.tolist())
            logger.info(f"Whisper transcription result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in stream transcription thread: {e}")
            return {"text": ""}

    async def transcribe_stream(self, audio_data_list: List[bytes]) -> str:
        try:
            if not audio_data_list:
                return ""
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                thread_pool, self._transcribe_stream_in_thread, audio_data_list
            )
            return result.get("text", "")
        except Exception as e:
            logger.error(f"Whisper stream transcription error: {e}")
            return ""

# Initialize Whisper engine globally
whisper_engine = WhisperEngine("base.en")
logger.info("WhisperEngine initialized and will be used for websocket transcription.")

def get_session_id(file_key: str) -> str:
    parts = file_key.split('_')
    if len(parts) >= 2:
        return '_'.join(parts[:-1])
    return file_key

async def handle_transcriptions(audio_data: bytes, final_chunk: bool, file_key: str, websocket: WebSocket):
    session_id = get_session_id(file_key)
    
    if session_id not in chunk_cache:
        chunk_cache[session_id] = []
    chunk_cache[session_id].append(audio_data)
    
    logger.info(f"Received chunk {len(chunk_cache[session_id])} for session {session_id}")

    if final_chunk or len(chunk_cache[session_id]) >= 5:
        logger.info(f"Processing {len(chunk_cache[session_id])} chunks for session {session_id}")

        text = await whisper_engine.transcribe_stream(chunk_cache[session_id])
        transcription_cache[session_id] = transcription_cache.get(session_id, "") + " " + text

        await websocket.send_json({
            "key": file_key,
            "text": transcription_cache[session_id],
            "final": final_chunk
        })

        if final_chunk:
            logger.info(f"Final chunk processed for session {session_id}, clearing cache")
            del chunk_cache[session_id]
            del transcription_cache[session_id]

@app.websocket("/ws/transcription")
async def websocket_transcription(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            logger.info(f"Received message: {message}")

            if message.get("action") == "connect_to_session":
                logger.info(f"Client connected to session: {message.get('key')}")
                continue

            file_key = message.get("key")
            chunk_base64 = message.get("chunk")
            final_chunk = message.get("final", False)

            if not file_key or not chunk_base64:
                logger.error("Invalid message received: Missing 'key' or 'chunk'")
                await websocket.send_json({"error": "Invalid message format."})
                continue

            try:
                chunk_bytes = base64.b64decode(chunk_base64)
                logger.info(f"Decoded {len(chunk_bytes)} bytes for {file_key}")
            except Exception as decode_err:
                logger.error(f"Base64 decoding failed for {file_key}: {decode_err}")
                await websocket.send_json({"key": file_key, "error": "Failed to decode chunk."})
                continue

            asyncio.create_task(handle_transcriptions(chunk_bytes, final_chunk, file_key, websocket))

    except WebSocketDisconnect:
        logger.warning("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Critical WebSocket Error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    thread_pool.shutdown(wait=False)
    logger.info("Thread pool shut down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)