from __future__ import annotations

import argparse
import sys

from .processor import ensure_tooling, process


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="media-transcript-summarizer")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    proc = sub.add_parser("process")
    proc.add_argument("source_file")
    proc.add_argument("--output-dir", default="outputs")
    proc.add_argument("--model-size", default="small")
    proc.add_argument("--language", default="")
    proc.add_argument("--device", default="auto")
    proc.add_argument("--compute-type", default="")
    proc.add_argument("--no-vad", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "doctor":
        checks = ensure_tooling()
        for name, ok in checks.items():
            print(f"{name}: {'ok' if ok else 'missing'}")
        return 0 if all(checks.values()) else 1

    result = process(
        args.source_file,
        output_dir=args.output_dir,
        model_size=args.model_size,
        language=args.language,
        device=args.device,
        compute_type=args.compute_type,
        vad_filter=not args.no_vad,
    )
    print(f"status: {result.status}")
    print(f"output_dir: {result.output_dir}")
    for error in result.errors:
        print(error, file=sys.stderr)
    return 0 if result.status == "success" else 1

