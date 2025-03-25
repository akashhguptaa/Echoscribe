import React, { useCallback, useRef, useState } from "react";
import { useDropzone } from "react-dropzone";

interface UploadProps {
  setTranscription: (text: string) => void;
}

const Upload: React.FC<UploadProps> = ({ setTranscription }) => {
  const ws = useRef<WebSocket | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;
      const file = acceptedFiles[0];
      setTranscription("");
      setUploading(true);

      const fileKey = `${Date.now()}_${file.name}`;

      ws.current = new WebSocket("ws://localhost:8005/ws/transcription");

      ws.current.onopen = () => {
        console.log("WebSocket connected");
        const reader = new FileReader();
        reader.onload = async () => {
          const arrayBuffer = reader.result as ArrayBuffer;
          const clonedArrayBuffer = arrayBuffer.slice(0);

          // 1. decode the original audio.
          const audioContext = new AudioContext();
          let audioBuffer = await audioContext.decodeAudioData(
            clonedArrayBuffer
          );

          // 2. convert to mono if necessary.
          if (audioBuffer.numberOfChannels > 1) {
            const monoBuffer = audioContext.createBuffer(
              1,
              audioBuffer.length,
              audioBuffer.sampleRate
            );
            const monoData = monoBuffer.getChannelData(0);
            // average the channels.
            for (let ch = 0; ch < audioBuffer.numberOfChannels; ch++) {
              const channelData = audioBuffer.getChannelData(ch);
              for (let i = 0; i < channelData.length; i++) {
                monoData[i] += channelData[i] / audioBuffer.numberOfChannels;
              }
            }
            audioBuffer = monoBuffer;
          }

          // 3. resample the audio to 16kHz.
          const targetSampleRate = 16000;
          const offlineContext = new OfflineAudioContext(
            1,
            Math.ceil(audioBuffer.duration * targetSampleRate),
            targetSampleRate
          );
          const source = offlineContext.createBufferSource();
          source.buffer = audioBuffer;
          source.connect(offlineContext.destination);
          source.start(0);
          const resampledBuffer = await offlineContext.startRendering();

          // 4. convert the resampled Float32 data to 16-bit PCM.
          const float32Data = resampledBuffer.getChannelData(0);
          const int16Data = new Int16Array(float32Data.length);
          for (let i = 0; i < float32Data.length; i++) {
            // clamp the value between -1 and 1.
            const s = Math.max(-1, Math.min(1, float32Data[i]));
            int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
          }

          // 5. define chunking parameters (in samples).
          const chunkDurationSec = 2; // 2 seconds per chunk.
          const paddingDurationSec = 0.15; // 150ms padding.
          const chunkSamples = targetSampleRate * chunkDurationSec;
          const paddingSamples = Math.floor(
            targetSampleRate * paddingDurationSec
          );
          const totalSamples = int16Data.length;
          let offset = 0;

          function int16ArrayToBase64(buffer: Int16Array) {
            let binary = "";
            // each 16-bit value is split into two bytes (little endian).
            for (let i = 0; i < buffer.length; i++) {
              binary += String.fromCharCode(
                buffer[i] & 0xff,
                (buffer[i] >> 8) & 0xff
              );
            }
            return btoa(binary);
          }

          // 6. chuk the audio with overlap and send over WebSocket.
          const sendChunk = () => {
            if (offset < totalSamples) {
              // calculate start and end indices (with padding on both sides).
              const start = Math.max(0, offset - paddingSamples);
              const end = Math.min(
                totalSamples,
                offset + chunkSamples + paddingSamples
              );
              const chunk = int16Data.slice(start, end);
              offset += chunkSamples;

              // convert the PCM chunk to base64.
              const base64Chunk = int16ArrayToBase64(chunk);
              const isFinal = offset >= totalSamples;
              const message = {
                key: `${fileKey}_${offset}`,
                chunk: base64Chunk,
                final: isFinal,
              };
              ws.current?.send(JSON.stringify(message));

              setTimeout(sendChunk, 10);
            }
          };

          sendChunk();
        };
        reader.readAsArrayBuffer(file);
      };

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.key.startsWith(fileKey) && data.text) {
          console.log("Received transcription:", data.text);
          setTranscription(data.text);
          if (data.final) {
            setUploading(false);
          }
        }
      };

      ws.current.onerror = (error) => {
        console.error("WebSocket error", error);
        setUploading(false);
      };

      ws.current.onclose = () => {
        console.log("WebSocket closed");
      };
    },
    [setTranscription]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "audio/*": [".wav"],
    },
  });

  return (
    <div className="flex flex-col items-center justify-center">
      {/* <div className="relative w-[420px] mb-6">
                <img
                    src="/assets/doctor_images.png"
                    alt="Stick figures"
                    className="absolute left-1/2 top-0 w-[320px] h-auto transform -translate-x-1/2 -translate-y-3/4"
                    style={{ mixBlendMode: "multiply" }}
                />
            </div> */}

      <div
        className="bg-background p-8 rounded-[49px]"
        style={{ boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.15)" }}
      >
        <div
          {...getRootProps()}
          className="border-2 border-dashed border-gray-300 rounded-[33px] p-8 text-center cursor-pointer hover:border-teal-400 flex flex-col items-center justify-center"
          style={{ width: "420px", height: "350px" }}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p>Land it here...</p>
          ) : (
            <>
              <button className="bg-teal-700 text-white px-6 py-2 rounded-full font-semibold hover:bg-teal-700 focus:outline-none">
                Upload Audio
              </button>
              <p className="text-gray-600 mt-4">or drop a file</p>
            </>
          )}
        </div>
      </div>
      {uploading && <p>Streaming audio and waiting for transcription...</p>}
    </div>
  );
};

export default Upload;
