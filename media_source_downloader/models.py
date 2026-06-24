from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class MediaFile:
    kind: str
    path: str
    format: str = ""


@dataclass
class DownloadMetadata:
    input_url: str
    final_url: str = ""
    platform: str = "generic"
    video_id: str = ""
    title: str = ""
    author: str = ""
    duration: float = 0.0
    published_at: str = ""
    description: str = ""
    cover_url: str = ""
    downloaded_media: List[MediaFile] = field(default_factory=list)
    fetched_at: str = ""


@dataclass
class DownloadResult:
    status: str
    output_dir: str
    metadata: DownloadMetadata
    media_files: List[MediaFile] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

