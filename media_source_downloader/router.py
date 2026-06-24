from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse


URL_RE = re.compile(r"https?://[^\s，。；;]+")


def extract_url(text: str) -> str:
    match = URL_RE.search(text.strip())
    return match.group(0).rstrip(":/") + ("/" if match and match.group(0).endswith("/") else "") if match else text.strip()


def platform_for_url(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "douyin.com" in host:
        return "douyin"
    if "xiaohongshu.com" in host or "xhslink.com" in host:
        return "xiaohongshu"
    if "bilibili.com" in host or "b23.tv" in host:
        return "bilibili"
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    if "tiktok.com" in host:
        return "tiktok"
    return "generic"


def video_id_from_url(url: str) -> str:
    parsed = urlparse(url)
    if "youtube.com" in parsed.netloc:
        value = parse_qs(parsed.query).get("v", [""])[0]
        if value:
            return value
    parts = [part for part in parsed.path.split("/") if part]
    return parts[-1] if parts else ""

