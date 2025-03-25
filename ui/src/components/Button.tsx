import React from "react";

interface ButtonProps {
  text: string;
  onClick: () => void;
}

const Button: React.FC<ButtonProps> = ({ text, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="cursor-pointer px-6 py-2 bg-teal-700 text-white rounded-full shadow-md hover:bg-teal-500 transition duration-300"
    >
      {text}
    </button>
  );
};

export default Button;