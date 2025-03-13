import Button from "./Button";
import { useState } from "react";
import Upload from "./upload";

interface HeroProps{
    start: boolean;
    setStart: (value: boolean) => void;
}

export default function HeroSection({start, setStart}: HeroProps) {

  return (
    <div className="h-screen flex items-center justify-between pt-16">
      <div className="ml-20 max-w-lg">
        <h1 className="text-4xl font-bold mb-4 text-slate-800">
          Transform Your Audio & Video into Clear, Structured Text
        </h1>
        <p className="text-lg text-slate-600 mb-6">
          Effortlessly convert your recordings into accurate transcriptions,
          concise summaries, and well-formatted text. Let our AI handle the
          work—fast and efficiently—so you can save time and focus on what
          matters.
        </p>
        <Button text="Get Started" onClick={() => setStart(true)} />
      </div>
      {!start &&(
      <div className="mr-20 pt-6 pb-6 ">
        <img
          src="/Group 4 (1).png"
          alt="Illustration showing AI transcription"
          className="max-w-md object-contain max-h-[calc(100vh-10rem)]"
        />
      </div>
      )}
      

      {start &&(
      <div className = "mr-20">
          <Upload />
        </div>
        )}
    </div>
  );
}
