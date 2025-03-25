import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import Navbar from '@/components/Navbar';
import { useWebSocket } from '@/context/WebSocketContext';

const Transcribe: React.FC = () => {
  const router = useRouter();
  const { fileName } = router.query;
  const transcriptionRef = useRef<HTMLDivElement>(null);
  
  const { ws, disconnectWebSocket } = useWebSocket();
  const [isTranscribing, setIsTranscribing] = useState(true);
  const [transcription, setTranscription] = useState('');
  const [fullTranscript, setFullTranscript] = useState('');

  // Handle reset functionality
  const handleReset = useCallback(() => {
    // Close WebSocket and clear connection
    disconnectWebSocket();
    
    // Navigate back to upload page
    router.push('/');
  }, [disconnectWebSocket, router]);

  // Copy transcript to clipboard
  const handleCopyTranscript = useCallback(() => {
    if (fullTranscript) {
      navigator.clipboard.writeText(fullTranscript)
        .then(() => {
          alert('Transcript copied to clipboard');
        })
        .catch(err => {
          console.error('Failed to copy transcript', err);
        });
    }
  }, [fullTranscript]);

  // Listen to WebSocket messages
  useEffect(() => {
    if (!ws) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received WebSocket message:', data); // Debugging log

        switch (data.status) {
          case "transcribing":
            // Accumulate partial transcriptions
            setTranscription(prev => prev + (data.text || ''));
            break;
          case "chunk_update":
            // Handle chunk updates if needed
            console.log('Chunk update:', data);
            break;
          case "completed":
            setIsTranscribing(false);
            setFullTranscript(data.full_transcript || data.text || '');
            break;
          case "error":
            setIsTranscribing(false);
            setTranscription('Error during transcription');
            break;
          default:
            console.log('Unhandled message:', data);
        }
      } catch (err) {
        console.error("Error parsing WebSocket message:", err);
      }
    };

    ws.addEventListener('message', handleMessage);

    return () => {
      ws.removeEventListener('message', handleMessage);
    };
  }, [ws]);

  return (
    <div className="min-h-screen bg-gradient-to-r from-[#E0F5F8] to-transparent pt-20">
      <Navbar resetStart={handleReset} />
      <div className="container max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-8 text-teal-800">
          Audio Transcription
        </h1>
        <div className="mb-8 transition-all duration-500">
          {isTranscribing ? (
            <div className="text-center py-12">
              <div className="inline-block animate-bounce mb-4">
                <svg
                  className="w-8 h-8 text-[#22BDBD]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 14l-7 7m0 0l-7-7m7 7V3"
                  />
                </svg>
              </div>
              <p className="text-gray-500">Processing your audio...</p>
              <p className="text-sm text-gray-400 mt-2">
                Transcribing: {fileName}
              </p>
              {transcription && (
                <div className="mt-4 text-left max-w-2xl mx-auto bg-white p-4 rounded-lg shadow-md">
                  <p className="text-gray-700">{transcription}</p>
                </div>
              )}
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="bg-white rounded-xl shadow-lg p-6 mb-6"
            >
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-700">
                  Transcript: {fileName}
                </h2>
                <button
                  onClick={handleCopyTranscript}
                  className="text-[#22BDBD] hover:text-teal-700 transition-colors"
                >
                  Copy Transcript
                </button>
              </div>
              <div
                ref={transcriptionRef}
                className="max-h-[500px] overflow-y-auto whitespace-pre-wrap prose prose-lg text-gray-800"
              >
                {fullTranscript || "No transcription available."}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Transcribe;