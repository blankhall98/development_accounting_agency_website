from __future__ import annotations

import re
from urllib.parse import parse_qs, quote, urlencode, urlparse, urlunparse


def whatsapp_link(number: str) -> str:
    digits = re.sub(r"\D", "", number or "")
    if not digits:
        return "https://wa.me/"
    return f"https://wa.me/{digits}"


def youtube_embed_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    video_id = ""

    if "youtu.be" in host:
        video_id = parsed.path.lstrip("/")
    elif "youtube.com" in host:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/embed/")[-1]
        elif parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/")[-1]

    if not video_id:
        return url
    return f"https://www.youtube.com/embed/{video_id}"


def maps_embed_url(url: str, fallback_query: str = "Ciudad de Mexico, Mexico") -> str:
    if not url:
        return f"https://www.google.com/maps?q={quote(fallback_query)}&output=embed"

    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if "google.com" in host and "/maps/embed" in parsed.path:
        return url

    if "google.com" in host or "maps.google.com" in host:
        query = parse_qs(parsed.query)
        query.setdefault("output", ["embed"])

        if not parsed.path or parsed.path == "/":
            query.setdefault("q", [fallback_query])

        new_query = urlencode({key: value[0] for key, value in query.items()}, doseq=False)
        return urlunparse(
            (
                parsed.scheme or "https",
                parsed.netloc,
                parsed.path or "/maps",
                parsed.params,
                new_query,
                parsed.fragment,
            )
        )

    return f"https://www.google.com/maps?q={quote(url)}&output=embed"
