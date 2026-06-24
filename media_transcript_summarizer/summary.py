from __future__ import annotations

from pathlib import Path

from .models import TranscriptResult


def write_summary(output: Path, result: TranscriptResult, transcript_txt: Path, transcript_srt: Path) -> Path:
    path = output / "summary.md"
    quotes = quoted_segments(result)
    path.write_text(
        f"""# 音视频总结报告

> 说明：这是脚本生成的占位报告。Skill 在 Agent 中使用时，应由 Agent 读取完整文字稿 `{transcript_txt}` 后，用大模型理解内容并重写本文件。

## 基本信息
- 文件：`{result.source_file}`
- 音频：`{result.audio_file}`
- 语言：{result.language}
- 转写模型：{result.model}

## 完整文字稿
- `{transcript_txt}`

## Agent 总结要求
请基于完整文字稿生成：

1. 核心内容概述。
2. 关键观点和结论。
3. 结构化要点。
4. 可引用原文片段。
5. 对业务、产品或选题有价值的洞察。

## 可引用原文片段
{quotes}

## 产物文件
- 源文件：`{result.source_file}`
- 完整文字稿：`{transcript_txt}`
- 字幕文件：`{transcript_srt}`
""",
        encoding="utf-8",
    )
    return path


def compact_summary(text: str) -> str:
    if not text.strip():
        return "未获得可总结的文字内容。"
    compact = " ".join(text.split())
    return compact[:500] + ("..." if len(compact) > 500 else "")


def key_points(text: str) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return "1. 未提取到明确要点。"
    return "\n".join(f"{idx}. {sentence}" for idx, sentence in enumerate(sentences[:8], 1))


def detail(text: str) -> str:
    compact = " ".join(text.split())
    if not compact:
        return "未获得完整文字稿。"
    chunks = [compact[index : index + 320] for index in range(0, len(compact), 320)]
    return "\n\n".join(f"### 段落 {idx}\n{chunk}" for idx, chunk in enumerate(chunks[:10], 1))


def quoted_segments(result: TranscriptResult) -> str:
    if not result.segments:
        return "- 未获得带时间点的原文。"
    return "\n".join(f"- {clock(seg.start)} {seg.text}" for seg in result.segments[:10])


def split_sentences(text: str) -> list[str]:
    normalized = text.replace("\n", " ")
    sentences: list[str] = []
    current: list[str] = []
    for char in normalized:
        current.append(char)
        if char in "。！？!?":
            sentence = "".join(current).strip()
            if len(sentence) >= 3:
                sentences.append(sentence)
            current = []
    tail = "".join(current).strip()
    if tail:
        sentences.append(tail[:160])
    return sentences


def clock(seconds: float) -> str:
    total = int(seconds)
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{secs:02}" if hours else f"{minutes:02}:{secs:02}"
