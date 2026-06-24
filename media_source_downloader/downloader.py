from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests

from common_utils.jsonio import write_json
from common_utils.time import now_iso

from .models import DownloadMetadata, DownloadResult, MediaFile
from .outputs import make_output_dir
from .router import extract_url, platform_for_url, video_id_from_url


MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 aweme/30.0.0"


class DownloadError(RuntimeError):
    pass


def download(
    input_text: str,
    output_dir: str = "outputs",
    prefer_video: bool = True,
    cookies: str = "",
    cookies_from_browser: str = "",
) -> DownloadResult:
    started_at = now_iso()
    errors: List[str] = []
    input_url = extract_url(input_text)
    final_url = resolve_final_url(input_url)
    platform = platform_for_url(final_url or input_url)
    video_id = video_id_from_url(final_url or input_url)
    output = make_output_dir(Path(output_dir), platform, video_id)
    metadata = DownloadMetadata(
        input_url=input_url,
        final_url=final_url or input_url,
        platform=platform,
        video_id=video_id,
        fetched_at=now_iso(),
    )
    provider = "local-page-parser" if platform == "douyin" else "yt-dlp"
    media_files: List[MediaFile] = []

    try:
        if platform == "douyin":
            try:
                media_path = download_douyin_public_page(metadata, output)
                media_files = [MediaFile(kind="video", path=str(media_path), format=media_path.suffix.lstrip("."))]
                metadata.downloaded_media = media_files
                status = "success"
            except Exception as page_exc:
                errors.append(f"douyin local page parser failed: {page_exc}")
                provider = "yt-dlp"
                raise page_exc
        else:
            raise RuntimeError("use yt-dlp")
    except Exception:
        try:
            info, downloaded = download_with_ytdlp(
                metadata.final_url,
                output,
                prefer_video=prefer_video,
                cookies=cookies,
                cookies_from_browser=cookies_from_browser,
            )
        except Exception:
            raise
        apply_info(metadata, info)
        media_files = [MediaFile(kind=kind_for_path(path), path=str(path), format=path.suffix.lstrip(".")) for path in downloaded]
        metadata.downloaded_media = media_files
        status = "success"
    except Exception as exc:
        errors.append(str(exc))
        status = "failed"

    write_json(output / "metadata.json", metadata)
    write_json(
        output / "run.json",
        {
            "skill": "media-source-downloader",
            "status": status,
            "input": input_text,
            "steps": ["detect_platform", "extract_metadata", "resolve_media_url", "download_media"],
            "provider": provider,
            "errors": errors,
            "started_at": started_at,
            "finished_at": now_iso(),
        },
    )
    return DownloadResult(status=status, output_dir=str(output), metadata=metadata, media_files=media_files, errors=errors)


def resolve_final_url(url: str) -> str:
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=15,
            headers={
                "User-Agent": MOBILE_UA,
            },
        )
        return response.url or url
    except Exception:
        return url


def download_with_ytdlp(
    url: str,
    output: Path,
    prefer_video: bool = True,
    cookies: str = "",
    cookies_from_browser: str = "",
) -> Tuple[Dict[str, Any], List[Path]]:
    try:
        import yt_dlp
    except Exception as exc:
        raise DownloadError("yt-dlp is not installed") from exc

    media_dir = output / "media"
    outtmpl = str(media_dir / "source.%(ext)s")
    format_selector = "bv*+ba/best" if prefer_video else "ba/bestaudio/best"
    options: Dict[str, Any] = {
        "format": format_selector,
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": False,
        "restrictfilenames": True,
        "merge_output_format": "mp4" if prefer_video else None,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["zh-Hans", "zh", "en"],
        "paths": {"home": str(output)},
    }
    if cookies:
        options["cookiefile"] = cookies
    if cookies_from_browser:
        options["cookiesfrombrowser"] = (cookies_from_browser,)

    before = set(media_dir.glob("*"))
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
    after = set(media_dir.glob("*"))
    downloaded = sorted(path for path in (after - before) if path.is_file())
    if not downloaded:
        downloaded = sorted(path for path in media_dir.glob("source.*") if path.is_file())
    if not downloaded:
        raise DownloadError("yt-dlp completed without creating a source media file")
    return info, downloaded


def download_douyin_public_page(metadata: DownloadMetadata, output: Path) -> Path:
    headers = {
        "User-Agent": MOBILE_UA,
        "Referer": metadata.final_url,
    }
    response = requests.get(metadata.final_url, allow_redirects=True, timeout=20, headers=headers)
    response.raise_for_status()
    metadata.final_url = response.url or metadata.final_url
    text = response.text
    metadata.video_id = video_id_from_url(metadata.final_url) or metadata.video_id
    metadata.platform = "douyin"
    parsed = parse_douyin_page(text)
    metadata.title = parsed.get("title") or metadata.title
    metadata.author = parsed.get("author") or metadata.author
    metadata.duration = parsed.get("duration") or metadata.duration
    metadata.description = parsed.get("description") or metadata.description
    metadata.cover_url = parsed.get("cover_url") or metadata.cover_url
    play_url = parsed["play_url"]
    media_dir = output / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    target = media_dir / "source.mp4"
    download_response = requests.get(play_url, headers=headers, timeout=60, stream=True, allow_redirects=True)
    download_response.raise_for_status()
    content_type = download_response.headers.get("content-type", "")
    if "text/html" in content_type:
        raise DownloadError(f"play url returned html instead of media: {play_url}")
    with target.open("wb") as handle:
        for chunk in download_response.iter_content(chunk_size=1024 * 512):
            if chunk:
                handle.write(chunk)
    if target.stat().st_size < 1024:
        raise DownloadError("downloaded douyin media is unexpectedly small")
    return target


def parse_douyin_page(text: str) -> Dict[str, Any]:
    url_decoded = text.replace("\\u002F", "/").replace("\\/", "/")
    play_match = re.search(r'"play_addr"\s*:\s*\{.*?"url_list"\s*:\s*\[\s*"([^"]+)"', url_decoded, re.S)
    if not play_match:
        play_match = re.search(r'https://aweme\.snssdk\.com/aweme/v1/playwm/\?video_id=[^"&<\\]+', url_decoded)
    if not play_match:
        raise DownloadError("could not find play_addr url_list in douyin page")
    play_url = play_match.group(1).replace("\\/", "/") if play_match.lastindex else play_match.group(0)

    def find_string(key: str) -> str:
        match = re.search(rf'"{key}"\s*:\s*"((?:\\.|[^"\\])*)"', text)
        if not match:
            return ""
        try:
            return json.loads(f'"{match.group(1)}"')
        except Exception:
            return match.group(1).replace("\\/", "/")

    cover_match = re.search(r'"cover"\s*:\s*\{.*?"url_list"\s*:\s*\[\s*"([^"]+)"', url_decoded, re.S)
    duration_match = re.search(r'"duration"\s*:\s*(\d+)', url_decoded)
    duration = 0.0
    if duration_match:
        raw_duration = int(duration_match.group(1))
        duration = raw_duration / 1000 if raw_duration > 10000 else raw_duration
    desc = find_string("desc")
    nickname = find_string("nickname")
    return {
        "play_url": play_url,
        "title": desc,
        "description": desc,
        "author": nickname,
        "duration": duration,
        "cover_url": cover_match.group(1).replace("\\/", "/") if cover_match else "",
    }


def apply_info(metadata: DownloadMetadata, info: Dict[str, Any]) -> None:
    metadata.final_url = info.get("webpage_url") or metadata.final_url
    metadata.video_id = str(info.get("id") or metadata.video_id)
    metadata.title = info.get("title") or metadata.title
    metadata.author = info.get("uploader") or info.get("channel") or metadata.author
    metadata.duration = float(info.get("duration") or 0)
    metadata.published_at = str(info.get("upload_date") or metadata.published_at)
    metadata.description = info.get("description") or metadata.description
    metadata.cover_url = info.get("thumbnail") or metadata.cover_url


def kind_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".mp3", ".m4a", ".aac", ".wav", ".flac", ".opus", ".ogg"}:
        return "audio"
    if suffix in {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}:
        return "video"
    return "media"


def ensure_tooling() -> Dict[str, bool]:
    try:
        import yt_dlp  # noqa: F401

        ytdlp = True
    except Exception:
        ytdlp = False
    return {"yt-dlp": ytdlp, "network": True, "ffmpeg": bool(shutil.which("ffmpeg"))}
