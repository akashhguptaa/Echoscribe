import React, { useCallback, useState, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/router";
import Button from "@/components/Button";
import { useWebSocket } from "@/context/WebSocketContext";

interface FileUploadProps {
  onUploadStart?: (fileName: string) => void;
}

const Upload: React.FC<FileUploadProps> = ({ onUploadStart }) => {
  const router = useRouter();
  const { ws, connectWebSocket, isConnected } = useWebSocket();
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Constants
  const CHUNK_SIZE: number = 1024 * 1024; // 1MB chunks
  const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

  // Send file in chunks via WebSocket
  const sendFileInChunks = useCallback(
    async (websocket: WebSocket, file: File) => {
      return new Promise<void>((resolve, reject) => {
        const fileSize = file.size;
        let offset = 0;

        const reader = new FileReader();

        const sendChunk = () => {
          const chunk = file.slice(
            offset,
            Math.min(offset + CHUNK_SIZE, fileSize)
          );
          reader.readAsArrayBuffer(chunk);
        };

        reader.onload = (e) => {
          if (websocket.readyState === WebSocket.OPEN && e.target?.result) {
            websocket.send(e.target.result);
            offset += (e.target.result as ArrayBuffer).byteLength;

            if (offset < fileSize) {
              setTimeout(sendChunk, 0);
            } else {
              // Send small EOF marker
              const eofMarker = new ArrayBuffer(8);
              websocket.send(eofMarker);
              resolve();
            }
          } else {
            reject(new Error("WebSocket is not open"));
          }
        };

        reader.onerror = (err) => {
          reject(err);
        };

        sendChunk();
      });
    },
    []
  );

  // Handle file upload
  const handleUpload = useCallback(
    async (file: File) => {
      if (!file) {
        setError("Please select a file first");
        return;
      }

      if (file.size > MAX_FILE_SIZE) {
        setError("File size exceeds 100MB limit");
        return;
      }

      // Ensure WebSocket connection
      const websocket = ws || connectWebSocket();

      // Wait a bit to ensure connection is established
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Redirect to transcription page immediately
      router.push({
        pathname: "/transcribe",
        query: { fileName: file.name },
      });

      // Trigger onUploadStart callback if provided
      onUploadStart?.(file.name);

      try {
        await sendFileInChunks(websocket, file);
      } catch (err) {
        console.error("Error sending file:", err);
        setError(`Failed to send file: ${(err as Error).message}`);
        websocket.close();
      }
    },
    [router, sendFileInChunks, onUploadStart, ws, connectWebSocket]
  );

  // Dropzone configuration
  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      const allowedTypes = ["video/mp4"];

      if (allowedTypes.includes(file.type)) {
        setFile(file);
        setError(null);
        await handleUpload(file);
      } else {
        setError("Please upload an MP4 file");
      }
    },
    [handleUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "video/*": [".mp4"],
    },
  });

  // Add a useEffect to handle connection status
  useEffect(() => {
    if (!isConnected) {
      connectWebSocket();
    }
  }, [isConnected, connectWebSocket]);

  return (
    <div className="flex flex-col items-center justify-center">
      <div
        className="bg-background p-8 rounded-[49px]"
        style={{ boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.15)" }}
      >
        <div
          {...getRootProps()}
          className="border-2 border-dashed border-gray-300 rounded-[33px] p-8 text-center cursor-pointer hover:border-teal-600 flex flex-col items-center justify-center"
          style={{ width: "420px", height: "350px" }}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p>Drop the file here...</p>
          ) : (
            <>
              <button className="cursor-pointer px-6 py-2 bg-teal-700 text-white rounded-full shadow-md hover:bg-teal-500 transition duration-300">
                Upload Video(mp4)
              </button>
              <p className="text-gray-600 mt-4">or drop a file</p>
              <p className="text-gray-500 mt-2 text-sm">
                Supported formats: MP4
              </p>
              {error && <p className="text-red-500 mt-2">{error}</p>}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Upload;
