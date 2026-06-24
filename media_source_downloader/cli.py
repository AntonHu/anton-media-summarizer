from __future__ import annotations

import argparse
import sys

from .downloader import download, ensure_tooling


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="media-source-downloader")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    dl = sub.add_parser("download")
    dl.add_argument("input")
    dl.add_argument("--output-dir", default="outputs")
    dl.add_argument("--audio-only", action="store_true")
    dl.add_argument("--cookies", default="")
    dl.add_argument("--cookies-from-browser", default="")
    args = parser.parse_args(argv)

    if args.command == "doctor":
        checks = ensure_tooling()
        for name, ok in checks.items():
            print(f"{name}: {'ok' if ok else 'missing'}")
        return 0 if all(checks.values()) else 1

    result = download(
        args.input,
        output_dir=args.output_dir,
        prefer_video=not args.audio_only,
        cookies=args.cookies,
        cookies_from_browser=args.cookies_from_browser,
    )
    print(f"status: {result.status}")
    print(f"output_dir: {result.output_dir}")
    for error in result.errors:
        print(error, file=sys.stderr)
    return 0 if result.status == "success" else 1
