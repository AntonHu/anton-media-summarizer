from __future__ import annotations

import shutil
from pathlib import Path
from typing import List

from common_utils.jsonio import write_json
from common_utils.time import now_iso

from .audio import ensure_audio
from .models import TranscriptSummaryResult
from .outputs import copy_source, make_output_dir
from .srt import to_srt
from .summary import write_summary
from .transcribe import transcribe_audio


def process(
    source_file: str,
    output_dir: str = "outputs",
    model_size: str = "small",
    language: str = "",
    device: str = "auto",
    compute_type: str = "",
    vad_filter: bool = True,
) -> TranscriptSummaryResult:
    started_at = now_iso()
    errors: List[str] = []
    source = Path(source_file).expanduser().resolve()
    output = make_output_dir(Path(output_dir), source)
    if not source.exists():
        errors.append(f"source file does not exist: {source}")
        write_run(output, "failed", started_at, errors)
        return TranscriptSummaryResult(status="failed", output_dir=str(output), source_file=str(source), errors=errors)

    try:
        copied_source = copy_source(source, output)
        audio = ensure_audio(copied_source, output / "media")
        result = transcribe_audio(audio, copied_source, model_size=model_size, language=language, device=device, compute_type=compute_type, vad_filter=vad_filter)

        transcript_dir = output / "transcript"
        txt = transcript_dir / "transcript.txt"
        srt = transcript_dir / "transcript.srt"
        js = transcript_dir / "transcript.json"
        txt.write_text(result.text.strip() + "\n", encoding="utf-8")
        srt.write_text(to_srt(result.segments), encoding="utf-8")
        write_json(js, result)
        summary = write_summary(output, result, txt, srt)
        write_json(
            output / "metadata.json",
            {
                "source_file": str(copied_source),
                "audio_file": str(audio),
                "language": result.language,
                "model": result.model,
                "duration": result.segments[-1].end if result.segments else 0,
                "fetched_at": now_iso(),
            },
        )
        write_run(output, "success", started_at, errors)
        return TranscriptSummaryResult(
            status="success",
            output_dir=str(output),
            source_file=str(copied_source),
            transcript_txt=str(txt),
            transcript_srt=str(srt),
            transcript_json=str(js),
            summary_md=str(summary),
            errors=errors,
        )
    except Exception as exc:
        errors.append(str(exc))
        write_run(output, "failed", started_at, errors)
        return TranscriptSummaryResult(status="failed", output_dir=str(output), source_file=str(source), errors=errors)


def write_run(output: Path, status: str, started_at: str, errors: list[str]) -> None:
    write_json(
        output / "run.json",
        {
            "skill": "media-transcript-summarizer",
            "status": status,
            "steps": ["copy_source", "extract_audio", "transcribe", "write_transcript", "write_summary"],
            "errors": errors,
            "started_at": started_at,
            "finished_at": now_iso(),
        },
    )


def ensure_tooling() -> dict[str, bool]:
    try:
        import faster_whisper  # noqa: F401

        faster = True
    except Exception:
        faster = False
    return {"ffmpeg": bool(shutil.which("ffmpeg")), "faster-whisper": faster}

