from media_transcript_summarizer.models import TranscriptSegment
from media_transcript_summarizer.srt import timestamp, to_srt
from media_transcript_summarizer.summary import split_sentences


def test_timestamp():
    assert timestamp(65.123) == "00:01:05,123"


def test_srt_output():
    content = to_srt([TranscriptSegment(start=0, end=1.5, text="你好")])
    assert "00:00:00,000 --> 00:00:01,500" in content
    assert "你好" in content


def test_split_sentences():
    assert split_sentences("第一句。第二句！") == ["第一句。", "第二句！"]

