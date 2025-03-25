import subprocess
import os
import time
import json
import threading
import queue
import numpy as np
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import whisper
import torch
from pydub import AudioSegment
import io
from starlette.websockets import WebSocketState

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Whisper model at startup to avoid loading delays during WebSocket connection
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded successfully!")

# Verify the model works
print("Verifying Whisper model...")
try:
    # Create a simple test audio file if it doesn't exist
    test_file = "test_audio.wav"
    if not os.path.exists(test_file):
        print("Creating test audio file...")
        from scipy.io import wavfile
        sample_rate = 16000
        duration = 1  # 1 second
        t = np.linspace(0, duration, sample_rate * duration)
        audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
        wavfile.write(test_file, sample_rate, audio.astype(np.float32))
    
    test_result = model.transcribe(test_file, fp16=False)
    print("Test transcription result:", test_result["text"])
except Exception as e:
    print(f"Error testing Whisper model: {str(e)}")

# Global flag to control transcription thread
transcription_active = False

def convert_to_compressed_wav(input_file, output_file):
    """
    Converts a given video file to a WAV audio file with a 16kHz sample rate,
    optimizing speed by skipping video processing and using 8-bit PCM.
    """
    # Check if the input file exists and has content
    if not os.path.exists(input_file):
        print(f"Input file does not exist: {input_file}")
        return False
    
    if os.path.getsize(input_file) == 0:
        print(f"Input file is empty: {input_file}")
        return False
    
    cmd = [
        'ffmpeg', '-i', input_file,
        '-vn', '-ac', '1', '-ar', '16000', '-acodec', 'pcm_u8',
        '-f', 'wav', '-preset', 'ultrafast', output_file
    ]
    
    print("Running ffmpeg command:", " ".join(cmd))
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        print("ffmpeg stderr:", result.stderr)
        return False
    
    # Verify the output file exists and is not empty
    if not os.path.exists(output_file):
        print(f"Output file was not created: {output_file}")
        return False
    
    if os.path.getsize(output_file) == 0:
        print(f"Output file is empty: {output_file}")
        return False
    
    print(f"Conversion successful: {output_file}, size: {os.path.getsize(output_file)} bytes")
    return True

async def process_audio_chunk(chunk_path):
    """
    Process an audio chunk using Whisper model asynchronously.
    Returns the transcription text.
    """
    try:
        print(f"Processing chunk: {chunk_path}")
        if not os.path.exists(chunk_path):
            print(f"Chunk file does not exist: {chunk_path}")
            return ""
        
        if os.path.getsize(chunk_path) == 0:
            print(f"Chunk file is empty: {chunk_path}")
            return ""
        
        # Load the audio file
        try:
            audio = AudioSegment.from_wav(chunk_path)
            print(f"Chunk loaded successfully: {len(audio)}ms")
        except Exception as e:
            print(f"Error loading audio chunk: {str(e)}")
            return ""
        
        # Process with Whisper
        result = await asyncio.to_thread(model.transcribe, chunk_path, fp16=False)
        transcript = result["text"].strip()
        print(f"Transcription result: {transcript}")
        return transcript
    except Exception as e:
        print(f"Error transcribing chunk: {str(e)}")
        return ""

async def transcription_worker(websocket: WebSocket, audio_file_path):
    """
    Worker function that processes the audio file in chunks
    and sends transcription results back to the client.
    """
    global transcription_active
    
    try:
        # Verify the audio file exists
        if not os.path.exists(audio_file_path):
            print(f"Audio file does not exist: {audio_file_path}")
            await websocket.send_text(json.dumps({
                "status": "error",
                "message": f"Audio file not found: {audio_file_path}"
            }))
            return
        
        if os.path.getsize(audio_file_path) == 0:
            print(f"Audio file is empty: {audio_file_path}")
            await websocket.send_text(json.dumps({
                "status": "error",
                "message": "Audio file is empty"
            }))
            return
        
        print(f"Starting transcription for: {audio_file_path}")
        
        # Load the audio file using pydub for easier chunking
        try:
            audio = AudioSegment.from_wav(audio_file_path)
            print(f"Audio loaded successfully: {len(audio)}ms")
        except Exception as e:
            print(f"Error loading audio: {str(e)}")
            await websocket.send_text(json.dumps({
                "status": "error",
                "message": f"Error loading audio: {str(e)}"
            }))
            return
        
        os.makedirs("chunks", exist_ok=True)  # Ensure directory exists

        # Break audio into chunks (3-second chunks work well for Whisper)
        chunk_length_ms = 3000
        chunks = [audio[i:i+chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
        print(f"Created {len(chunks)} chunks of {chunk_length_ms}ms each")
        
        full_transcript = ""

        for i, chunk in enumerate(chunks):
            if not transcription_active:
                print("Transcription was cancelled")
                break
            
            # Check WebSocket connection
            if websocket.application_state != WebSocketState.CONNECTED:
                print("WebSocket disconnected during transcription")
                break
                
            # Save chunk to temporary file
            chunk_path = f"chunks/chunk_{i}.wav"
            print(f"Exporting chunk {i+1}/{len(chunks)} to {chunk_path}")
            chunk.export(chunk_path, format="wav")
            
            # Check if chunk file exists and has content
            if not os.path.exists(chunk_path):
                print(f"Chunk file was not created: {chunk_path}")
                continue
            
            if os.path.getsize(chunk_path) == 0:
                print(f"Chunk file is empty: {chunk_path}")
                continue
            
            # Process the chunk asynchronously
            print(f"Processing chunk {i+1}/{len(chunks)}")
            transcript_segment = await process_audio_chunk(chunk_path)

            if transcript_segment:
                full_transcript += " " + transcript_segment
                print(f"Sending transcription update for chunk {i+1}/{len(chunks)}")
                
                # Send the incremental update to the client
                if websocket.application_state == WebSocketState.CONNECTED:
                    try:
                        message = json.dumps({
                            "status": "transcribing",
                            "chunk": i + 1,
                            "total_chunks": len(chunks),
                            "text": transcript_segment,
                            "full_transcript": full_transcript.strip()
                        })
                        await websocket.send_text(message)
                        print(f"Update sent successfully, current progress: {i+1}/{len(chunks)}")
                    except Exception as e:
                        print(f"Error sending update: {str(e)}")
                        break
            else:
                print(f"No transcription result for chunk {i+1}")

            # Clean up
            try:
                os.remove(chunk_path)
                print(f"Removed chunk file: {chunk_path}")
            except Exception as e:
                print(f"Error removing chunk file: {str(e)}")

        # Send final transcript
        if transcription_active and websocket.application_state == WebSocketState.CONNECTED:
            try:
                print("Sending final transcript")
                await websocket.send_text(json.dumps({
                    "status": "completed",
                    "full_transcript": full_transcript.strip()
                }))
                print("Final transcript sent successfully")
            except Exception as e:
                print(f"Error sending final transcript: {str(e)}")
            
    except Exception as e:
        print(f"Error in transcription worker: {str(e)}")
        if websocket.application_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_text(json.dumps({
                    "status": "error",
                    "message": f"Transcription error: {str(e)}"
                }))
            except:
                print("Could not send error message to client")
    finally:
        transcription_active = False
        print("Transcription worker finished")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")
    
    global transcription_active
    transcription_active = False
    
    try:
        print(f"Initial WebSocket state: {websocket.application_state}")
        os.makedirs("uploads", exist_ok=True)  # Ensure directory exists
        
        timestamp = int(time.time())
        input_file = f"uploads/uploaded_{timestamp}.mp4"
        output_file = f"uploads/converted_{timestamp}.wav"

        # Receive the file data
        total_bytes = 0
        chunks_received = 0
        
        with open(input_file, "wb") as f:
            print("Receiving file data...")
            while True:
                try:
                    data = await websocket.receive_bytes()
                    if not data or len(data) < 10:  # Check for very small EOF marker
                        print("Received EOF marker or empty data")
                        break
                    
                    f.write(data)
                    total_bytes += len(data)
                    chunks_received += 1
                    
                    if chunks_received % 10 == 0:
                        print(f"Received {chunks_received} chunks, total size: {total_bytes} bytes")
                        
                except WebSocketDisconnect:
                    print("Client disconnected during upload")
                    return

        file_size = os.path.getsize(input_file)
        print(f"File saved as {input_file}, size: {file_size} bytes")
        
        if file_size == 0:
            print("Received empty file")
            await websocket.send_text(json.dumps({
                "status": "error", 
                "message": "Received empty file"
            }))
            return

        print("Starting conversion process...")
        start_time = time.time()
        success = convert_to_compressed_wav(input_file, output_file)
        elapsed_time = time.time() - start_time
        print(f"Conversion finished in {elapsed_time:.2f} seconds, success: {success}")

        if success:
            print(f"Sending success message for file: {output_file}")
            await websocket.send_text(json.dumps({
                "status": "success",
                "output_file": output_file,
                "time": elapsed_time
            }))

            print(f"WebSocket state before transcription: {websocket.application_state}")
            print("Starting transcription process...")
            await websocket.send_text(json.dumps({"status": "starting_transcription"}))

            transcription_active = True
            await transcription_worker(websocket, output_file)
        else:
            error_msg = "Conversion failed"
            print(error_msg)
            await websocket.send_text(json.dumps({"status": "error", "message": error_msg}))

    except WebSocketDisconnect:
        print("Client disconnected")
        transcription_active = False
    except Exception as e:
        print(f"Error in websocket endpoint: {str(e)}")
        transcription_active = False
        if websocket.application_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_text(json.dumps({"status": "error", "message": str(e)}))
            except:
                print("Could not send error message to client")

@app.get("/")
async def root():
    return {"message": "WebSocket server is running. Connect to /ws endpoint."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)