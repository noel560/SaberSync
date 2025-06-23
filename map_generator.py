import os
import json
import shutil
import uuid
import librosa
import random

difficulty_density = {
    "Easy": 0.3,
    "Normal": 0.5,
    "Hard": 0.7,
    "Expert": 1.0,
    "ExpertPlus": 1.2
}

def generate_notes(audio_path: str, bpm: int, difficulty: str):
    y, sr = librosa.load(audio_path, sr=None)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # Nehézségi szint alapján szűrés
    difficulty_multipliers = {
        "Easy": 0.25,
        "Normal": 0.5,
        "Hard": 0.75,
        "Expert": 1.0,
        "ExpertPlus": 1.2,
    }

    density = difficulty_multipliers.get(difficulty, 1.0)
    beat_times = beat_times[::max(1, int(1 / density))]

    # Cut directionok
    easy_dirs = [1, 2, 3]  # csak alap vágások
    all_dirs = list(range(0, 9))

    # Jegy pozíciók
    valid_layers = {
        "Easy": [1],
        "Normal": [1],
        "Hard": [1, 2],
        "Expert": [0, 1, 2],
        "ExpertPlus": [0, 1, 2],
    }

    valid_columns = {
        "Easy": [1, 2],
        "Normal": [0, 1, 2, 3],
        "Hard": [0, 1, 2, 3],
        "Expert": [0, 1, 2, 3],
        "ExpertPlus": [0, 1, 2, 3],
    }

    layers = valid_layers.get(difficulty, [1])
    columns = valid_columns.get(difficulty, [0, 1, 2, 3])
    directions = easy_dirs if difficulty in ["Easy", "Normal"] else all_dirs

    notes = []
    last_dir = {0: None, 1: None}

    for idx, time in enumerate(beat_times):
        beat_time = time * (bpm / 60)
        hand = idx % 2  # 0 = bal, 1 = jobb
        dir_choices = [d for d in directions if d != last_dir[hand]]
        cut_direction = random.choice(dir_choices)
        last_dir[hand] = cut_direction

        note = {
            "_time": round(beat_time, 3),
            "_lineIndex": random.choice(columns),
            "_lineLayer": random.choice(layers),
            "_type": hand,  # 0 = bal, 1 = jobb
            "_cutDirection": cut_direction
        }
        notes.append(note)

        # ExpertPlus → néha dupla jegy
        if difficulty == "ExpertPlus" and random.random() < 0.3:
            other_hand = 1 - hand
            dir2 = random.choice([d for d in directions if d != last_dir[other_hand]])
            last_dir[other_hand] = dir2
            note2 = {
                "_time": round(beat_time, 3),
                "_lineIndex": random.choice(columns),
                "_lineLayer": random.choice(layers),
                "_type": other_hand,
                "_cutDirection": dir2
            }
            notes.append(note2)

    return sorted(notes, key=lambda n: n["_time"])

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
