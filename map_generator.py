import os
import json
import shutil
import uuid
import librosa

def generate_notes(audio_path: str, bpm: int):
    y, sr = librosa.load(audio_path, sr=None)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    notes = []
    for idx, time in enumerate(onset_times):
        beat_time = time * (bpm / 60)
        note = {
            "_time": round(beat_time, 3),
            "_lineIndex": idx % 4,         # váltakozó oszlop (0–3)
            "_lineLayer": (idx // 4) % 3,  # váltakozó sor (0–2)
            "_type": 0 if idx % 2 == 0 else 1,  # váltogatja a kezeket
            "_cutDirection": 1  # lefelé vágás
        }
        notes.append(note)
    
    return notes

def create_map_folder(
    song_name: str,
    song_author: str,
    bpm: int,
    audio_path: str,
    cover_path: str,
    environment: str = "DefaultEnvironment",
    difficulties: list = ["Normal"]
) -> str:
    """
    Creates a Beat Saber map folder with Info.dat and placeholder difficulty files.
    Returns the path to the map folder.
    """
    folder_name = f"map_{uuid.uuid4().hex[:8]}"
    map_dir = os.path.join("uploads", folder_name)
    os.makedirs(map_dir, exist_ok=True)

    # Copy audio and cover to map folder
    song_file_name = "song.ogg"
    cover_file_name = "cover.png"
    shutil.copy(audio_path, os.path.join(map_dir, song_file_name))
    shutil.copy(cover_path, os.path.join(map_dir, cover_file_name))

    # Create Info.dat structure
    info_data = {
        "_version": "2.0.0",
        "_songName": song_name,
        "_songAuthorName": song_author,
        "_beatsPerMinute": bpm,
        "_songFilename": song_file_name,
        "_coverImageFilename": cover_file_name,
        "_environmentName": environment,
        "_difficultyBeatmapSets": [
            {
                "_beatmapCharacteristicName": "Standard",
                "_difficultyBeatmaps": []
            }
        ]
    }

    for diff in difficulties:
        note_data = {
            "_notes": generate_notes(audio_path, bpm),
            "_obstacles": [],
            "_events": []
        }

        beatmap_filename = f"{diff}.dat"
        with open(os.path.join(map_dir, beatmap_filename), "w", encoding="utf-8") as f:
            json.dump(note_data, f, indent=4)

        info_data["_difficultyBeatmapSets"][0]["_difficultyBeatmaps"].append({
            "_difficulty": diff,
            "_beatmapFilename": beatmap_filename,
            "_noteJumpMovementSpeed": 10,
            "_noteJumpStartBeatOffset": 0
        })

    # Save Info.dat
    with open(os.path.join(map_dir, "Info.dat"), "w", encoding="utf-8") as f:
        json.dump(info_data, f, indent=4)

    # Create empty difficulty files
    #for diff in difficulties:
    #    with open(os.path.join(map_dir, f"{diff}.dat"), "w", encoding="utf-8") as f:
    #        json.dump({"_notes": [], "_obstacles": [], "_events": []}, f)

    return map_dir
