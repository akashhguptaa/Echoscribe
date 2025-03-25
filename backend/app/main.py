import os
import io
import json
import asyncio
import tempfile
import numpy as np
import whisper
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState
from moviepy import *
app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Whisper model at startup
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded successfully!")

async def extract_audio_from_mp4(video_path):
    """
    Extract audio from MP4 file using MoviePy
    """
    try:
        # Extract audio from video
        video = VideoFileClip(video_path)
        
        # Create a temporary file for audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            audio_path = temp_audio_file.name
        
        # Write audio to temp file
        video.audio.write_audiofile(audio_path)
        
        # Close video to free up resources
        video.close()
        
        return audio_path
    
    except Exception as e:
        print(f"Error extracting audio: {str(e)}")
        raise

async def transcribe_audio(audio_path):
    """
    Transcribe audio using Whisper
    """
    try:
        # Transcribe using Whisper
        result = await asyncio.to_thread(model.transcribe, audio_path, fp16=False)
        
        transcript = result["text"].strip()
        print(f"Final Transcription: {transcript}")
        return transcript
    
    except Exception as e:
        print(f"Transcription error: {str(e)}")
        raise

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")

    try:
        # Receive MP4 file in chunks
        audio_chunks = []
        file_received = False
        total_size = 0

        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "status": "connected",
            "message": "Ready to receive MP4 file"
        }))

        # Create a temporary file to store the incoming MP4
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            video_path = temp_video_file.name

            try:
                while True:
                    data = await websocket.receive()

                    # Handle binary chunks
                    if data.get('type') == 'websocket.receive' and data.get('bytes'):
                        chunk = data['bytes']
                        total_size += len(chunk)
                        temp_video_file.write(chunk)
                        file_received = True

                        # Optional: Send progress updates
                        await websocket.send_text(json.dumps({
                            "status": "uploading",
                            "progress": f"Received {total_size} bytes"
                        }))

                    # Handle end of file marker
                    elif data.get('type') == 'websocket.receive.text':
                        try:
                            text_data = json.loads(data['text'])
                            if text_data.get('type') == 'end_of_file':
                                # Ensure file was received
                                if not file_received:
                                    await websocket.send_text(json.dumps({
                                        "status": "error",
                                        "message": "No MP4 file received"
                                    }))
                                    break

                                # Close the temporary file
                                temp_video_file.close()

                                # Send transcription start notification
                                await websocket.send_text(json.dumps({
                                    "status": "processing",
                                    "message": "Extracting audio and transcribing"
                                }))

                                # Extract audio from MP4
                                audio_path = await extract_audio_from_mp4(video_path)

                                try:
                                    # Transcribe the extracted audio
                                    full_transcript = await transcribe_audio(audio_path)

                                    # Send final transcript
                                    await websocket.send_text(json.dumps({
                                        "status": "completed",
                                        "full_transcript": full_transcript
                                    }))

                                finally:
                                    # Clean up audio file
                                    if os.path.exists(audio_path):
                                        os.unlink(audio_path)

                                break

                        except json.JSONDecodeError:
                            print("Invalid JSON received")

            except WebSocketDisconnect:
                print("Client disconnected")
            except Exception as e:
                print(f"Error processing MP4: {str(e)}")
                await websocket.send_text(json.dumps({
                    "status": "error", 
                    "message": str(e)
                }))
            finally:
                # Always clean up the temporary video file
                if os.path.exists(video_path):
                    os.unlink(video_path)

    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.send_text(json.dumps({
            "status": "error", 
            "message": str(e)
        }))

@app.get("/")
async def root():
    return {"message": "MP4 transcription WebSocket server is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005, timeout_keep_alive=120)