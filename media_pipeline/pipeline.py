from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional

from common_utils.jsonio import write_json
from common_utils.slug import slugify
from common_utils.time import now_iso
from media_source_downloader.downloader import download
from media_source_downloader.router import URL_RE
from media_transcript_summarizer.processor import process as process_media


def process(input_value: str, output_dir: str = "outputs", model_size: str = "small", language: str = "") -> dict:
    started_at = now_iso()
    base = Path(output_dir) / now_iso()[:10] / slugify(f"pipeline-{input_value}", "pipeline", limit=60)
    base.mkdir(parents=True, exist_ok=True)
    errors: List[str] = []
    download_result = None
    transcript_result = None

    if is_url_input(input_value):
        download_root = base / "download"
        dl = download(input_value, output_dir=str(download_root), prefer_video=True)
        download_result = dl
        if dl.status != "success":
            errors.extend(dl.errors)
        media_file = first_media_file(dl.media_files)
        if media_file:
            transcript_result = process_media(media_file, output_dir=str(base / "transcript_summary"), model_size=model_size, language=language)
            if transcript_result.status != "success":
                errors.extend(transcript_result.errors)
        else:
            errors.append("download did not produce a media file for transcription")
    else:
        path = Path(input_value).expanduser()
        transcript_result = process_media(str(path), output_dir=str(base / "transcript_summary"), model_size=model_size, language=language)
        if transcript_result.status != "success":
            errors.extend(transcript_result.errors)

    status = "success" if not errors and transcript_result and transcript_result.status == "success" else "failed"
    data = {
        "status": status,
        "input": input_value,
        "download_output_dir": download_result.output_dir if download_result else "",
        "transcript_output_dir": transcript_result.output_dir if transcript_result else "",
        "source_media": first_media_file(download_result.media_files) if download_result else str(Path(input_value).expanduser()),
        "transcript_txt": transcript_result.transcript_txt if transcript_result else "",
        "transcript_srt": transcript_result.transcript_srt if transcript_result else "",
        "summary_md": transcript_result.summary_md if transcript_result else "",
        "errors": errors,
        "started_at": started_at,
        "finished_at": now_iso(),
    }
    write_json(base / "pipeline.json", data)
    data["output_dir"] = str(base)
    return data


def is_url_input(value: str) -> bool:
    return bool(URL_RE.search(value.strip()))


def first_media_file(media_files) -> Optional[str]:
    if not media_files:
        return None
    preferred = [item for item in media_files if item.kind in {"video", "audio"}]
    return (preferred or media_files)[0].path


def ensure_tooling() -> dict[str, bool]:
    try:
        import yt_dlp  # noqa: F401

        ytdlp = True
    except Exception:
        ytdlp = False
    try:
        import faster_whisper  # noqa: F401

        faster = True
    except Exception:
        faster = False
    return {"yt-dlp": ytdlp, "ffmpeg": bool(shutil.which("ffmpeg")), "faster-whisper": faster}
