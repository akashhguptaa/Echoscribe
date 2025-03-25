from pathlib import Path

file_data = Path("C:\\Users\\akash\\OneDrive\\Documents\\web_dev\\just_for_fun\\echoScribe\\ui\\src")

with open("new_output.txt", "a", encoding="utf-8") as f:
    for file in file_data.rglob("*.tsx"):
        content = file.read_text(encoding="utf-8")  # Read file content
        f.write(f"\n----------{file}---------\n")
        f.write(content + "\n")
