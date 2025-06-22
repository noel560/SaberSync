import os
from pydub import AudioSegment
import uuid

def process_audio(file_path: str, output_dir: str = "uploads") -> str:
    """
    - Converting into ogg
    - Adds 2 second silence to the beggining
    """
    silence = AudioSegment.silent(duration=2000)

    audio = AudioSegment.from_file(file_path)

    final_audio = silence + audio

    filename = f"processed_{uuid.uuid4().hex[:8]}.ogg"
    output_path = os.path.join(output_dir, filename)

    final_audio.export(output_path, format="ogg")

    return output_path
