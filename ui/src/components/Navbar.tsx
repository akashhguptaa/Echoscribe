function Navbar() {
  return (
    <div
      className="flex justify-between items-center"
      style={{
        mixBlendMode: "multiply",
      }}
    >
      <div
        onClick={() => {
          window.location.href = window.location.href;
          console.log("chutiya");
        }}
      >
        <img src="logo.png" alt="Logo" className="w-50 pt-2 ml-4 hover:cursor-pointer  " />
      </div>
    </div>
  );
}

export default Navbar;
