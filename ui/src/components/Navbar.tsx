import Button from "./Button";
import { AudioWaveform } from "lucide-react";

interface NavbarProps {
  resetStart: (prop: boolean) => void;
}

export default function Navbar({ resetStart }: NavbarProps) {
  return (
    <div className="fixed top-0 left-0 w-full p-4 flex items-center justify-between bg-white/40 backdrop-filter backdrop-blur-md border-b border-white/20 shadow-sm">
      <div
        className=" cursor-pointer ml-20 flex items-center gap-2"
        onClick={() => resetStart(false)}
      >
        <AudioWaveform className="text-[#22BDBD] font-bold" />
        <span className="text-black text-3xl">
          Echo<span className="font-bold text-teal-700">Scribe</span>
        </span>
      </div>
      <nav id="navbar-content" className="text-md text-slate-500 mr-20 flex">
        <div className="flex gap-6 items-center">
          <a href="#contact">Contact</a>
          <a href="#about">About</a>
          <Button text="Start" onClick={() => resetStart(true)} />
        </div>
      </nav>
    </div>
  );
}
