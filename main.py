from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import librosa
import soundfile as sf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # csak dev alatt
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_files(
    song_name: str = Form(...),
    song_author: str = Form(...),
    audio: UploadFile = File(...),
    cover: UploadFile = File(...),
):
    audio_path = os.path.join(UPLOAD_DIR, audio.filename)
    cover_path = os.path.join(UPLOAD_DIR, cover.filename)

    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    with open(cover_path, "wb") as buffer:
        shutil.copyfileobj(cover.file, buffer)

    # Load audio & detect BPM
    try:
        y, sr = librosa.load(audio_path, sr=None)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    return {
        "message": "Files received",
        "song_name": song_name,
        "song_author": song_author,
        "audio_path": audio_path,
        "cover_path": cover_path,
        "bpm": round(tempo, 2)
    }
