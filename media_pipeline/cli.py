from __future__ import annotations

import argparse
import sys

from .pipeline import ensure_tooling, process


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="media-pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    proc = sub.add_parser("process")
    proc.add_argument("input")
    proc.add_argument("--output-dir", default="outputs")
    proc.add_argument("--model-size", default="small")
    proc.add_argument("--language", default="")
    args = parser.parse_args(argv)

    if args.command == "doctor":
        checks = ensure_tooling()
        for name, ok in checks.items():
            print(f"{name}: {'ok' if ok else 'missing'}")
        return 0 if all(checks.values()) else 1

    result = process(args.input, output_dir=args.output_dir, model_size=args.model_size, language=args.language)
    print(f"status: {result['status']}")
    print(f"output_dir: {result['output_dir']}")
    print(f"source_media: {result.get('source_media', '')}")
    print(f"transcript_txt: {result.get('transcript_txt', '')}")
    print(f"summary_md: {result.get('summary_md', '')}")
    for error in result.get("errors", []):
        print(error, file=sys.stderr)
    return 0 if result["status"] == "success" else 1

