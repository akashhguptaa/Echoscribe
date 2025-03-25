// import "./App.css";
import Navbar from "./components/Navbar";
import HeroText from "./components/HeroText";
import Upload from "./components/Upload";
import TranscribedBox from "./components/TranscriptBox";
import { useState } from "react";

function App() {
    const [transcription, setTranscription] = useState<string>("");

    const handleTranscription = (text: string | ((prev: string) => string)): void => {
        if (typeof text === "string") {
            setTranscription((prev) => `${prev} ${text}`);
        } else {
            setTranscription(text);
        }
    };

    const showTranscribedBox = transcription !== "";

    return (
        <div className="bg-background relative overflow-hidden">
            <Navbar />
            <img
              src="background.svg"
              alt="Background"
              className="absolute inset-10 w-full h-full object-cover"
            />
            <div className="relative z-10">
          {!showTranscribedBox && (
              <div className="flex flex-row justify-between ml-32 mt-20 mr-44">
            <HeroText />
            <Upload setTranscription={handleTranscription} />
              </div>
          )}
          {showTranscribedBox && (
              <TranscribedBox
            transcription={transcription}
            setTranscription={handleTranscription}
              />
          )}
            </div>
        </div>
    );
}

export default App;