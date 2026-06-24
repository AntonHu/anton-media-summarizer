from __future__ import annotations

from pathlib import Path

from common_utils.slug import slugify
from common_utils.time import now_iso


def make_output_dir(base: Path, platform: str, video_id: str) -> Path:
    date = now_iso()[:10]
    label = slugify(f"download-{platform}-{video_id}", "download")
    output = base / date / label
    (output / "media").mkdir(parents=True, exist_ok=True)
    (output / "captions").mkdir(exist_ok=True)
    return output

