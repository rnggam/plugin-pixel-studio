#!/usr/bin/env python3
"""Validate a PNG for a Pixel Studio import workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--max-colors", type=int)
    parser.add_argument("--require-alpha", action="store_true")
    args = parser.parse_args()

    try:
        from PIL import Image
    except ImportError:
        print("Pillow is required to validate PNG assets.", file=sys.stderr)
        return 2

    if not args.image.is_file():
        print(f"File not found: {args.image}", file=sys.stderr)
        return 2

    with Image.open(args.image) as image:
        image.load()
        rgba = image.convert("RGBA")
        colors = len(rgba.getcolors(maxcolors=16_777_216) or [])
        has_transparency = any(alpha < 255 for _, _, _, alpha in rgba.getdata())
        result = {
            "file": str(args.image.resolve()),
            "format": image.format,
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "colors": colors,
            "has_transparency": has_transparency,
            "valid": True,
            "errors": [],
        }

    if result["format"] != "PNG":
        result["valid"] = False
        result["errors"].append("File is not a PNG.")
    if args.width is not None and result["width"] != args.width:
        result["valid"] = False
        result["errors"].append(f"Expected width {args.width}, got {result['width']}.")
    if args.height is not None and result["height"] != args.height:
        result["valid"] = False
        result["errors"].append(f"Expected height {args.height}, got {result['height']}.")
    if args.max_colors is not None and result["colors"] > args.max_colors:
        result["valid"] = False
        result["errors"].append(
            f"Expected at most {args.max_colors} colors, got {result['colors']}."
        )
    if args.require_alpha and not result["has_transparency"]:
        result["valid"] = False
        result["errors"].append("Expected transparent pixels, but none were found.")

    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
