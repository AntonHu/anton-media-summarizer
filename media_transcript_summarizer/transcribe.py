from __future__ import annotations

from pathlib import Path

from .models import TranscriptResult, TranscriptSegment


class TranscribeError(RuntimeError):
    pass


def transcribe_audio(
    audio: Path,
    source: Path,
    model_size: str = "small",
    language: str = "",
    device: str = "auto",
    compute_type: str = "",
    vad_filter: bool = True,
) -> TranscriptResult:
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:
        raise TranscribeError("faster-whisper is not installed") from exc

    resolved_device = "cpu" if device == "auto" else device
    kwargs = {}
    if compute_type:
        kwargs["compute_type"] = compute_type
    model = WhisperModel(model_size, device=resolved_device, **kwargs)
    segments_iter, info = model.transcribe(str(audio), language=language or None, vad_filter=vad_filter)
    segments = [
        TranscriptSegment(start=float(seg.start), end=float(seg.end), text=seg.text.strip())
        for seg in segments_iter
        if seg.text and seg.text.strip()
    ]
    return TranscriptResult(
        source_file=str(source),
        audio_file=str(audio),
        language=getattr(info, "language", language or ""),
        model=model_size,
        text="\n".join(segment.text for segment in segments),
        segments=segments,
    )

