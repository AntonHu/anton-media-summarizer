from media_source_downloader.router import extract_url, platform_for_url, video_id_from_url


def test_extract_url_from_douyin_share_text():
    text = "3.82 复制打开抖音 https://v.douyin.com/TbxfuLAcnis/ :2pm"
    assert extract_url(text) == "https://v.douyin.com/TbxfuLAcnis/"


def test_platform_for_douyin():
    assert platform_for_url("https://v.douyin.com/TbxfuLAcnis/") == "douyin"


def test_youtube_video_id():
    assert video_id_from_url("https://www.youtube.com/watch?v=abc123") == "abc123"

