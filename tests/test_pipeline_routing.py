from media_pipeline.pipeline import is_url_input


def test_url_input():
    assert is_url_input("看这个 https://v.douyin.com/TbxfuLAcnis/ :2pm")


def test_local_input():
    assert not is_url_input("/tmp/source.mp4")

