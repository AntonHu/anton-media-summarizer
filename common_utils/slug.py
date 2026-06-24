from __future__ import annotations

import re


def slugify(value: str, fallback: str = "item", limit: int = 80) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"https?://", "", value)
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = value.strip("-")
    return (value[:limit].strip("-") or fallback)

