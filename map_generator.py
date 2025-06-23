import os
import json
import shutil
import uuid
import librosa
import random

def generate_notes(audio_path: str, bpm: int, difficulty: str):
    y, sr = librosa.load(audio_path, sr=None)
    
    # Beat és onset detektálás
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time', backtrack=True)

    # Nehézséghez skálázás: minden hányadik beatre teszünk blokkot
    difficulty_scale = {
        "Easy": 4,
        "Normal": 2,
        "Hard": 1,
        "Expert": 1,
        "ExpertPlus": 1,
    }
    density = difficulty_scale.get(difficulty, 1)
    
    # Beat listából szűrve generálunk
    selected_beats = [b for i, b in enumerate(beats) if i % density == 0]

    # Extra gyorsítók Expert+ esetén
    if difficulty == "ExpertPlus":
        selected_beats += list(onsets)
        selected_beats = sorted(set(selected_beats))

    # Konverzió időből beat időre
    notes = []
    last_hand = 1  # Kezdjük jobb kézzel (1=jobb, 0=bal)
    last_pos = {"left": (1, 1), "right": (2, 1)}

    for i, t in enumerate(selected_beats):
        _time = round(t * (bpm / 60), 3)
        hand = last_hand ^ 1  # váltogatjuk a kezet

        hand_str = "left" if hand == 0 else "right"
        other_str = "right" if hand == 0 else "left"

        # Pozíció random, de figyelünk ne legyen ütközés
        while True:
            x = random.randint(0, 3)
            y = random.randint(0, 2)
            if (x, y) != last_pos[other_str]:
                break

        last_pos[hand_str] = (x, y)
        last_hand = hand

        note = {
            "_time": _time,
            "_lineIndex": x,
            "_lineLayer": y,
            "_type": hand,  # 0=bal, 1=jobb
            "_cutDirection": random.randint(0, 8)  # irány randomizálva
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
        "_version": "2.1.0",
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
            "_notes": generate_notes(audio_path, bpm, diff),
            "_obstacles": [],
            "_events": []
        }

        beatmap_filename = f"{diff}.dat"
        with open(os.path.join(map_dir, beatmap_filename), "w", encoding="utf-8") as f:
            json.dump(note_data, f, indent=4)

        speed_by_difficulty = {
            "Easy": 10,
            "Normal": 12,
            "Hard": 14,
            "Expert": 16,
            "ExpertPlus": 18
        }

        info_data["_difficultyBeatmapSets"][0]["_difficultyBeatmaps"].append({
            "_difficulty": diff,
            "_beatmapFilename": beatmap_filename,
            "_noteJumpMovementSpeed": speed_by_difficulty.get(diff, 14),
            "_noteJumpStartBeatOffset": 0
        })

    # Save Info.dat
    with open(os.path.join(map_dir, "Info.dat"), "w", encoding="utf-8") as f:
        json.dump(info_data, f, indent=4)

    return map_dir
