from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


AUDIO_EXTENSIONS = {".mp3", ".m4a", ".aac", ".wav", ".flac", ".opus", ".ogg"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}


class AudioError(RuntimeError):
    pass


def is_audio(path: Path) -> bool:
    return path.suffix.lower() in AUDIO_EXTENSIONS


def ensure_audio(source: Path, output_media_dir: Path) -> Path:
    if is_audio(source):
        return source
    if not shutil.which("ffmpeg"):
        raise AudioError("ffmpeg is not installed")
    target = output_media_dir / "source.mp3"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-vn",
        "-acodec",
        "libmp3lame",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(target),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode:
        raise AudioError(result.stderr.strip() or "ffmpeg failed to extract audio")
    return target

