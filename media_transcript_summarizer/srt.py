from __future__ import annotations

from .models import TranscriptSegment


def timestamp(seconds: float) -> str:
    ms_total = int(round(seconds * 1000))
    hours, rest = divmod(ms_total, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, ms = divmod(rest, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def to_srt(segments: list[TranscriptSegment]) -> str:
    blocks = []
    for index, segment in enumerate(segments, 1):
        blocks.append(f"{index}\n{timestamp(segment.start)} --> {timestamp(segment.end)}\n{segment.text.strip()}\n")
    return "\n".join(blocks)

