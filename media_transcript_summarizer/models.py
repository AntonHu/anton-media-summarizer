from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptResult:
    source_file: str
    audio_file: str
    language: str = ""
    model: str = ""
    text: str = ""
    segments: List[TranscriptSegment] = field(default_factory=list)


@dataclass
class TranscriptSummaryResult:
    status: str
    output_dir: str
    source_file: str
    transcript_txt: str = ""
    transcript_srt: str = ""
    transcript_json: str = ""
    summary_md: str = ""
    errors: List[str] = field(default_factory=list)

