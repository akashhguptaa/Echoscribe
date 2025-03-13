import React from "react";

interface ButtonProps {
  text: string;
  onClick: () => void;
}

const Button: React.FC<ButtonProps> = ({ text, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="px-6 py-2 bg-[#22BDBD] text-white rounded-full shadow-md hover:bg-teal-500 transition duration-300"
    >
      {text}
    </button>
  );
};

export default Button;
