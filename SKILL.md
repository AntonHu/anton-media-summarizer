---
name: anton-media-summarizer
description: Use when a user provides a media URL or local audio/video file and wants a local source file, complete transcript, and summary report. Routes URL inputs through media-source-downloader and local files through media-transcript-summarizer.
---

# Anton Media Summarizer

This project exposes two skills:

- `skills/media-source-downloader`: downloads public media URLs to local source files and metadata.
- `skills/media-transcript-summarizer`: transcribes and summarizes local audio/video files.

Use the pipeline when the input type is unknown:

```bash
python -m media_pipeline process "<url-or-local-file>"
```

After the command succeeds:

1. Read the generated `transcript/transcript.txt`.
2. Use language-model reasoning to write the final `summary.md`.
3. Do not treat the script-generated `summary.md` as the final summary; it is only a placeholder/draft unless rewritten.

Rules:

- URL input first runs the downloader, then transcribes the downloaded media.
- Local file input skips downloading and runs transcription plus summary directly.
