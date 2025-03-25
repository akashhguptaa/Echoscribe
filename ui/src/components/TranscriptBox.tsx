import React from "react";

interface TranscribedBoxProps {
  transcription: string;
  setTranscription: (transcription: string) => void;
}

const TranscribedBox: React.FC<TranscribedBoxProps> = ({
  transcription,
  setTranscription,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div
        className="relative bg-white p-8 rounded-[33px] w-[700px]"
        style={{ boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.15)" }}
      >
        {/* <div
                    className="absolute top-[-78px] left-1/2 transform -translate-x-1/2"
                    style={{ mixBlendMode: "multiply" }}
                >
                    <img
                        src="/assets/doctor_images.png"
                        alt="Doctor icon"
                        className="w-[320px] h-auto"
                    />
                </div> */}
        <div className="absolute top-[-40px] left-0">
          <p className="text-primary font-semibold mb-4">File Transcribed:</p>
        </div>
        <p className="text-gray-600 mb-8 text-lg">{transcription}</p>
      </div>
      <div className="flex justify-center mt-4">
        <button
          className="bg-teal-700 text-white px-6 py-2 rounded-full font-semibold hover:bg-teal-700 focus:outline-none"
          onClick={() => window.location.reload()}
        >
          Upload New Audio
        </button>
      </div>
    </div>
  );
};

export default TranscribedBox;
