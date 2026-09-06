#!/usr/bin/env python3
"""Copy a bounded manifest of official thumbnails as-is; never transform images.

The manifest is hand-reviewed against the linked primary event pages. Artwork is
attributed to its institutional publisher, not asserted to be openly licensed.
Only known public HKU image-host URLs and source-supplied <=1200px variants pass.
Existing different local files are not overwritten. This helper does not ingest
social-media accounts, modify activity evidence, or infer event completion.
"""

import hashlib
import json
from pathlib import Path
import re
import struct
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "scripts/hku_activity_media.json"
MEDIA = ROOT / "public/internal/hku-activity/media"
MAX_ITEMS = 12
MAX_BYTES = 2 * 1024 * 1024


def dimensions(data):
    """Read GIF/JPEG dimensions without decoding, resizing or rewriting pixels."""
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return struct.unpack("<HH", data[6:10])
    if data[:2] != b"\xff\xd8":
        raise ValueError("Expected source JPEG or GIF")
    offset = 2
    while offset < len(data):
        while offset < len(data) and data[offset] != 255:
            offset += 1
        while offset < len(data) and data[offset] == 255:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[offset:offset + 2], "big")
        if length < 2:
            break
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            height, width = struct.unpack(">HH", data[offset + 3:offset + 7])
            return width, height
        offset += length
    raise ValueError("No supported JPEG dimensions found")


def main():
    manifest = json.loads(MANIFEST.read_text())
    if not 1 <= len(manifest) <= MAX_ITEMS:
        raise ValueError("Manifest exceeds bounded item count")
    MEDIA.mkdir(parents=True, exist_ok=True)
    total = 0
    for evidence_url, entry in manifest.items():
        parsed = urlparse(entry["imageUrl"])
        if parsed.scheme != "https" or parsed.netloc != "foa-media.arch.hku.hk":
            raise ValueError("Only the verified official HKU image host is allowed")
        if not evidence_url.startswith("https://www.arch.hku.hk/event_/"):
            raise ValueError("Expected a primary HKU event evidence page")
        relative = entry["src"]
        if not re.fullmatch(r"\./media/[a-z0-9-]+\.(jpg|gif)", relative):
            raise ValueError("Unsafe or unsupported local image path")
        target = MEDIA / relative.rsplit("/", 1)[1]
        request = Request(entry["imageUrl"], headers={
            "User-Agent": "HKU-Activity-Observatory-Thumbnail-Check/1.0",
            "Accept": "image/jpeg,image/gif",
        })
        with urlopen(request, timeout=20) as response:
            final_url = urlparse(response.geturl())
            if final_url.scheme != "https" or final_url.netloc != parsed.netloc:
                raise ValueError("Unexpected image-host redirect")
            if not response.headers.get_content_type().startswith("image/"):
                raise ValueError("Server did not return an image")
            payload = response.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise ValueError("Thumbnail exceeds 2 MiB limit")
        width, height = dimensions(payload)
        if not 1 <= width <= 1200 or not 1 <= height <= 1200:
            raise ValueError("Thumbnail exceeds source-image dimension limit")
        if target.exists() and target.read_bytes() != payload:
            raise ValueError(f"Refusing to replace a different existing file: {target}")
        if not target.exists():
            with target.open("xb") as output:
                output.write(payload)
        total += len(payload)
        print(f"{target.name}: {width}x{height}, {len(payload)} bytes, "
              f"sha256={hashlib.sha256(payload).hexdigest()}")
    print(f"Copied/verified {len(manifest)} original thumbnails; total {total} bytes")


if __name__ == "__main__":
    main()
