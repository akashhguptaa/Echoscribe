import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

const Upload = () => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    console.log("Uploaded files:", acceptedFiles);
    // Handle file uploads (e.g., send to API, process locally, etc.)
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "video/mp4": [".mp4"],
      "audio/mpeg": [".mp3"],
      "audio/wav": [".wav"],
    },
  });

  return (
    <div className="bg-background p-8 rounded-[33px] shadow-lg">
      <div
        {...getRootProps()}
        className="border-2 border-dashed border-gray-300 rounded-[33px] p-8 text-center cursor-pointer hover:border-[#22BDBD] flex flex-col items-center justify-center"
        style={{ width: "420px", height: "350px" }}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p className="text-gray-600">Drop your file here...</p>
        ) : (
          <>
            <button className="bg-[#22BDBD] text-white px-6 py-2 rounded-full font-semibold hover:bg-teal-600 focus:outline-none">
              Upload Video or Audio
            </button>
            <p className="text-gray-600 mt-4">or drag & drop a file</p>
          </>
        )}
      </div>
    </div>
  );
};

export default Upload;
