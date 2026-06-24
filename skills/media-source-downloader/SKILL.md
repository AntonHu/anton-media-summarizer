---
name: media-source-downloader
description: Download public media URLs from Douyin, Xiaohongshu, Bilibili, YouTube, TikTok, or yt-dlp-supported sites to local source media and metadata. Use for URL inputs only.
---

# Media Source Downloader

Download public media URLs to local files.

Command:

```bash
python -m media_source_downloader download "<url-or-share-text>"
```

Outputs:

- `metadata.json`
- `run.json`
- `media/source.*`
- optional `captions/`

Notes:

- Uses public page data and `yt-dlp`.
- If a platform blocks access, report the failure reason.
