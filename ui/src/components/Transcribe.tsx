import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import Navbar from './Navbar';

const Transcribe: React.FC = () => {
  const router = useRouter();
  const transcriptionRef = useRef<HTMLDivElement>(null);
  const [isTranscribing, setIsTranscribing] = useState(true);
  const [transcription, setTranscription] = useState<string>('');
  const [fileName, setFileName] = useState<string>('');

  useEffect(() => {
    // Check if transcript is passed in query
    const encodedTranscript = router.query.transcript as string;
    const fileNameFromQuery = router.query.fileName as string;

    if (encodedTranscript) {
      const decodedTranscript = decodeURIComponent(encodedTranscript);
      
      // Simulate transcription loading
      const timer = setTimeout(() => {
        setTranscription(decodedTranscript);
        setFileName(fileNameFromQuery);
        setIsTranscribing(false);
      }, 1500);

      return () => clearTimeout(timer);
    }
  }, [router.query]);

  const handleReset = () => {
    router.push('/');
  };

  const handleCopyTranscript = () => {
    navigator.clipboard.writeText(transcription);
    alert('Transcript copied to clipboard!');
  };

  return (
    <div className="min-h-screen bg-gray-50">
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
                {transcription || "No transcription available."}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Transcribe;