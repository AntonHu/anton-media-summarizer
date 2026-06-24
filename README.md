# Anton Media Summarizer

把公开视频链接或本地音视频文件转换成源文件、完整文字稿、字幕和总结报告。

## Quick Start

### 1. 创建环境

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
brew install ffmpeg
```

### 2. 检查依赖

```bash
.venv/bin/python -m media_pipeline doctor
```

期望输出：

```text
yt-dlp: ok
ffmpeg: ok
faster-whisper: ok
```

### 3. 处理公开视频链接

```bash
.venv/bin/python -m media_pipeline process "<video-url-or-share-text>" \
  --output-dir outputs \
  --model-size small \
  --language zh
```

示例：

```bash
.venv/bin/python -m media_pipeline process "3.82 复制打开抖音，看看【云策AI的作品】企业Agent实践：从需求到落地的6个关键节点 客... https://v.douyin.com/TbxfuLAcnis/ :2pm G@v.fo 12/03 DHV:/" \
  --output-dir outputs-final \
  --model-size small \
  --language zh
```

### 4. 处理本地音视频文件

```bash
.venv/bin/python -m media_pipeline process "/path/to/source.mp4" \
  --output-dir outputs \
  --model-size small \
  --language zh
```

也可以处理音频文件：

```bash
.venv/bin/python -m media_pipeline process "/path/to/source.mp3" \
  --output-dir outputs \
  --model-size small \
  --language zh
```

## 输出结果

处理 URL 时，输出目录类似：

```text
outputs/YYYY-MM-DD/pipeline_slug/
  pipeline.json
  download/
    YYYY-MM-DD/download-platform-videoid/
      metadata.json
      run.json
      media/source.mp4
  transcript_summary/
    YYYY-MM-DD/transcript-source/
      metadata.json
      run.json
      media/source.mp4
      media/source.mp3
      transcript/transcript.txt
      transcript/transcript.srt
      transcript/transcript.json
      summary.md
```

处理本地文件时，不会生成 `download/` 阶段，只会生成 `transcript_summary/`。

关键文件：

- `media/source.mp4`：下载或复制得到的源视频
- `media/source.mp3`：从视频抽取的音频
- `transcript/transcript.txt`：完整文字稿
- `transcript/transcript.srt`：带时间轴字幕
- `transcript/transcript.json`：结构化转写结果
- `summary.md`：总结报告
- `pipeline.json`：总流程状态和关键产物路径
- `metadata.json`：媒体信息
- `run.json`：执行状态、步骤和错误信息

## 常用命令

### 自动处理 URL 或本地文件

```bash
.venv/bin/python -m media_pipeline process "<url-or-local-file>"
```

### 只下载公开视频

```bash
.venv/bin/python -m media_source_downloader download "<video-url-or-share-text>"
```

### 只转写本地音视频

```bash
.venv/bin/python -m media_transcript_summarizer process "/path/to/source.mp4"
```

### 运行测试

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B tests/run_tests.py
```

## 使用流程

### 输入是 URL

```text
URL / 分享文本
  -> 下载源视频
  -> 抽取音频
  -> ASR 转写
  -> 输出 transcript.txt / transcript.srt / transcript.json
  -> 根据 transcript.txt 生成 summary.md
```

### 输入是本地视频

```text
本地 mp4 / mov / mkv / webm
  -> 复制源视频
  -> 抽取音频
  -> ASR 转写
  -> 输出 transcript.txt / transcript.srt / transcript.json
  -> 根据 transcript.txt 生成 summary.md
```

### 输入是本地音频

```text
本地 mp3 / m4a / wav / flac
  -> 复制源音频
  -> ASR 转写
  -> 输出 transcript.txt / transcript.srt / transcript.json
  -> 根据 transcript.txt 生成 summary.md
```

## 抖音处理链路

抖音分享文本通常包含短链和额外口令文本，例如：

```text
3.82 复制打开抖音，看看【云策AI的作品】企业Agent实践：从需求到落地的6个关键节点 客... https://v.douyin.com/TbxfuLAcnis/ :2pm G@v.fo 12/03 DHV:/
```

处理步骤：

1. `extract_url` 从整段分享文本中提取短链。
2. `resolve_final_url` 使用移动端 User-Agent 解析短链。
3. 短链跳转到 `iesdouyin.com/share/video/...` 公开分享页。
4. `download_douyin_public_page` 请求分享页 HTML。
5. `parse_douyin_page` 提取 `video.play_addr.url_list`、标题、作者、时长和封面。
6. 使用 `requests` 下载 `play_addr` 指向的视频，保存为 `media/source.mp4`。
7. 使用 `ffmpeg` 抽取 `media/source.mp3`。
8. 使用 `faster-whisper` 生成完整文字稿和字幕。
9. 调用方读取 `transcript.txt`，生成最终 `summary.md`。

## 技术栈

- Python：CLI、流程编排、文件输出
- requests：页面请求和视频下载
- yt-dlp：通用公开视频下载
- ffmpeg：音视频处理和音频抽取
- faster-whisper：语音识别

## Skills

项目包含两个可单独使用的 Skill。

### media-source-downloader

负责下载公开视频链接并保存基础元数据。

入口：

```bash
.venv/bin/python -m media_source_downloader download "<video-url-or-share-text>"
```

产物：

```text
metadata.json
run.json
media/source.*
```

### media-transcript-summarizer

负责处理本地音视频文件，生成完整文字稿、字幕和总结入口文件。

入口：

```bash
.venv/bin/python -m media_transcript_summarizer process "/path/to/source.mp4"
```

产物：

```text
metadata.json
run.json
media/source.*
transcript/transcript.txt
transcript/transcript.srt
transcript/transcript.json
summary.md
```

## 项目结构

```text
anton-media-summarizer/
  SKILL.md
  README.md
  pyproject.toml
  requirements.txt
  config.example.json
  skills/
    media-source-downloader/
      SKILL.md
    media-transcript-summarizer/
      SKILL.md
  media_source_downloader/
    cli.py
    downloader.py
    router.py
    models.py
    outputs.py
  media_transcript_summarizer/
    cli.py
    processor.py
    transcribe.py
    audio.py
    summary.py
    srt.py
    models.py
    outputs.py
  media_pipeline/
    cli.py
    pipeline.py
  common_utils/
  tests/
```

## 当前支持

- 抖音公开分享链接下载
- `yt-dlp` 支持的公开视频下载
- 本地视频转写：mp4、mov、mkv、webm 等
- 本地音频转写：mp3、m4a、wav、flac 等
- 输出完整文字稿、SRT 字幕、结构化 JSON
- 根据完整文字稿生成总结报告

## 待增强

- 平台字幕优先提取
- 用户提供 `.srt` / `.vtt` 后直接总结
- 视频画面 OCR
- 更多平台专项解析
- 登录态或强风控内容处理
