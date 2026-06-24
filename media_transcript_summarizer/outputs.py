from __future__ import annotations

import shutil
from pathlib import Path

from common_utils.slug import slugify
from common_utils.time import now_iso


def make_output_dir(base: Path, source: Path) -> Path:
    date = now_iso()[:10]
    output = base / date / slugify(f"transcript-{source.stem}", "transcript")
    (output / "media").mkdir(parents=True, exist_ok=True)
    (output / "transcript").mkdir(exist_ok=True)
    return output


def copy_source(source: Path, output: Path) -> Path:
    target = output / "media" / f"source{source.suffix.lower()}"
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    return target

