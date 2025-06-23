from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import librosa
import soundfile as sf
import json
import zipfile

from audio_processing import process_audio
from map_generator import create_map_folder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # csak dev alatt
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def detect_bpm(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return round(float(tempo))

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

        bpm = detect_bpm(audio_path)
        print(f"BPM: {bpm}")

        processed_audio = process_audio(audio_path)

        map_folder = create_map_folder(
            song_name=song_name,
            song_author=song_author,
            bpm=bpm,
            audio_path=processed_audio,
            cover_path=cover_path,
            environment=environment,
            difficulties=json.loads(difficulties)
        )

        zip_path = f"{map_folder}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(map_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, map_folder)
                    zipf.write(file_path, arcname)

        return FileResponse(zip_path, filename=os.path.basename(zip_path), media_type='application/zip')
    
    except Exception as e:
        print("💥 ERROR:", str(e))
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
    )