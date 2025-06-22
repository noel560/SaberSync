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
    environment: str = Form(...),
    difficulties: str = Form(...)
):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        audio_path = os.path.join(UPLOAD_DIR, audio.filename)
        cover_path = os.path.join(UPLOAD_DIR, cover.filename)

        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(cover.file, buffer)

        return {
            "message": "Fájlok feltöltve!",
            "song_name": song_name,
            "song_author": song_author,
            "audio_path": audio_path,
            "cover_path": cover_path
        }
    except Exception as e:
        print("💥 ERROR:", str(e))
        raise