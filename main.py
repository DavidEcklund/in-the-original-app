from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import aiofiles
import os
import uuid

app = FastAPI()

# Directory to save temporary files
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

async def chunk_text(text, chunk_size=70):
    words = text.split()
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

async def mock_process_chunk(chunk):
    return f"Processed: {chunk}"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    text = contents.decode("utf-8")
    chunks = await chunk_text(text)

    processed_chunks = []
    for chunk in chunks:
        processed = await mock_process_chunk(chunk)
        processed_chunks.append(processed)

    result_text = "\n\n".join(processed_chunks)

    # Save processed text
    output_filename = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.txt")
    async with aiofiles.open(output_filename, 'w') as out_file:
        await out_file.write(result_text)

    return {"download_link": f"/download/{os.path.basename(output_filename)}"}

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    return FileResponse(path=file_path, filename="processed_output.txt", media_type='text/plain')
