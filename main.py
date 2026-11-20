#!/usr/bin/env python3
"""Entry for news-image-20261120: copy the front-page image to the output dir.

Stdlib only, no network. The image (news.png, drawn for Friday 20 November
2026) sits beside this program; both runs write the exact same bytes.
"""

import hashlib
import os
import struct
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576
MAX_DIM = 1024
SOURCE_NAME = "news.png"


def png_dimensions(data):
    """Return (width, height) from the IHDR chunk of a PNG byte string."""
    if len(data) < 33 or data[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file")
    if data[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk first")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    with open(source, "rb") as fh:
        data = fh.read()

    if data[:8] != PNG_MAGIC:
        raise SystemExit("news.png: bad PNG magic")
    if len(data) > MAX_BYTES:
        raise SystemExit("news.png: %d bytes exceeds 1 MiB" % len(data))
    width, height = png_dimensions(data)
    if width > MAX_DIM or height > MAX_DIM:
        raise SystemExit("news.png: %dx%d exceeds 1024x1024" % (width, height))

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as fh:
        fh.write(data)

    # Integrity check: what landed on disk must be byte-identical to the
    # validated source, or the run has not produced a trustworthy entry.
    with open(target, "rb") as fh:
        written = fh.read()
    if written != data:
        raise SystemExit("entry.png: bytes written differ from news.png")
    if hashlib.sha256(written).hexdigest() != hashlib.sha256(data).hexdigest():
        raise SystemExit("entry.png: sha256 mismatch after write")

    digest = hashlib.sha256(data).hexdigest()
    print("entry.png: %d bytes, %dx%d, sha256 %s" % (len(data), width, height, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
