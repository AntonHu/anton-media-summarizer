---
name: media-transcript-summarizer
description: Transcribe local audio/video files such as mp4, mov, mp3, m4a, wav, and produce transcript.txt, transcript.srt, transcript.json, plus summary.md.
---

# Media Transcript Summarizer

Process local media files only.

Command:

```bash
python -m media_transcript_summarizer process "/path/to/source.mp4"
```

Outputs:

- `media/source.*`
- `transcript/transcript.txt`
- `transcript/transcript.srt`
- `transcript/transcript.json`
- `summary.md`
- `metadata.json`
- `run.json`

Important:

- The Python command is responsible for reliable media handling and complete transcript output.
- Read `transcript/transcript.txt` and write the final `summary.md` using language-model understanding.
- If the script creates a placeholder `summary.md`, replace it with a content-aware summary before presenting results to the user.
