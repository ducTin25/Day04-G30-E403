from __future__ import annotations

import re
import unicodedata
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit


_TRACKING_QUERY_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def _normalized_url(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""

    parsed = urlsplit(raw)
    if not parsed.netloc:
        return raw.casefold().rstrip("/")

    host = (parsed.hostname or "").casefold()
    if host.startswith("www."):
        host = host[4:]

    port = parsed.port
    if port and not (
        (parsed.scheme.casefold() == "http" and port == 80)
        or (parsed.scheme.casefold() == "https" and port == 443)
    ):
        host = f"{host}:{port}"

    path = re.sub(r"/+", "/", parsed.path or "/").rstrip("/") or "/"
    query = urlencode(sorted(
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.casefold().startswith("utm_")
        and key.casefold() not in _TRACKING_QUERY_KEYS
    ))
    return f"{host}{path}" + (f"?{query}" if query else "")


def _normalized_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(normalized.split())


def _deduplication_key(item: dict[str, Any]) -> tuple[str, str] | None:
    url = _normalized_url(str(item.get("url") or ""))
    if url:
        return ("url", url)

    title = _normalized_title(str(item.get("title") or ""))
    if title:
        return ("title", title)

    return None


def deduplicate_items(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if items is None:
        items = []
    if not isinstance(items, list):
        raise TypeError("items must be a list")

    unique_items: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for item in items:
        if not isinstance(item, dict):
            raise TypeError("each item must be an object")

        key = _deduplication_key(item)
        if key is not None and key in seen:
            continue
        if key is not None:
            seen.add(key)
        unique_items.append(item)

    return {
        "tool": "deduplicate_items",
        "items": unique_items,
        "input_count": len(items),
        "item_count": len(unique_items),
        "removed_count": len(items) - len(unique_items),
    }
