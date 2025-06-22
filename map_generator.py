import os
import json
import shutil
import uuid

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
                "_difficultyBeatmaps": [
                    {
                        "_difficulty": diff,
                        "_beatmapFilename": f"{diff}.dat",
                        "_noteJumpMovementSpeed": 10,
                        "_noteJumpStartBeatOffset": 0
                    } for diff in difficulties
                ]
            }
        ]
    }

    # Save Info.dat
    with open(os.path.join(map_dir, "Info.dat"), "w", encoding="utf-8") as f:
        json.dump(info_data, f, indent=4)

    # Create empty difficulty files
    for diff in difficulties:
        with open(os.path.join(map_dir, f"{diff}.dat"), "w", encoding="utf-8") as f:
            json.dump({"_notes": [], "_obstacles": [], "_events": []}, f)

    return map_dir
