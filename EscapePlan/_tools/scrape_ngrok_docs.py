#!/usr/bin/env python3
"""Recursively mirror ngrok docs pages inside a constrained path prefix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Set, Tuple
from http.client import RemoteDisconnected
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urldefrag, urlparse, urlunparse
from urllib.request import Request, urlopen


USER_AGENT = "Mozilla/5.0 (compatible; EscapePlanDocMirror/1.0)"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: Set[str] = set()

    def handle_starttag(self, _tag: str, attrs: List[Tuple[str, str]]) -> None:
        for key, value in attrs:
            if value is None:
                continue
            key_lower = key.lower()
            if key_lower in {"href", "src"}:
                self.links.add(value.strip())


@dataclass
class FetchResult:
    status: int
    content_type: str
    body: bytes
    from_cache: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonicalize(raw_url: str, base_url: str | None = None) -> str | None:
    candidate = raw_url.strip()
    if not candidate:
        return None
    if candidate.startswith(("mailto:", "javascript:", "tel:")):
        return None

    joined = urljoin(base_url or "", candidate)
    joined, _ = urldefrag(joined)
    parsed = urlparse(joined)

    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None

    path = parsed.path or "/"
    while "//" in path:
        path = path.replace("//", "/")

    normalized = parsed._replace(scheme="https", path=path, params="", query="")
    return urlunparse(normalized)


def in_scope(url: str, host: str, allowed_prefixes: Tuple[str, ...]) -> bool:
    parsed = urlparse(url)
    if parsed.netloc != host:
        return False
    return any(parsed.path == prefix.rstrip("/") or parsed.path.startswith(prefix) for prefix in allowed_prefixes)


def cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def fetch_url(url: str, cache_dir: Path, timeout: int, retries: int = 3) -> FetchResult:
    key = cache_key(url)
    cache_file = cache_dir / f"{key}.json"
    if cache_file.exists():
        payload = json.loads(cache_file.read_text(encoding="utf-8"))
        return FetchResult(
            status=int(payload.get("status", 0)),
            content_type=str(payload.get("content_type", "")),
            body=bytes.fromhex(payload.get("body_hex", "")),
            from_cache=True,
        )

    req = Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, retries + 1):
        try:
            with urlopen(req, timeout=timeout) as response:
                status = int(getattr(response, "status", 200))
                content_type = response.headers.get("Content-Type", "")
                body = response.read()
            break
        except HTTPError as exc:  # server responded with error page
            status = int(exc.code)
            content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
            body = exc.read() if exc.fp else b""
            break
        except (URLError, RemoteDisconnected) as exc:
            if attempt == retries:
                raise RuntimeError(f"Network failure for {url} after {retries} attempts: {exc}") from exc
            time.sleep(attempt)
            continue

    cache_payload = {
        "url": url,
        "status": status,
        "content_type": content_type,
        "fetched_at": utc_now(),
        "body_hex": body.hex(),
    }
    cache_file.write_text(json.dumps(cache_payload, indent=2), encoding="utf-8")
    return FetchResult(status=status, content_type=content_type, body=body, from_cache=False)


def url_to_local_path(url: str, root_out: Path) -> Path:
    parsed = urlparse(url)
    segments = [seg for seg in parsed.path.split("/") if seg]

    if not segments:
        return root_out / parsed.netloc / "index.html"

    last = segments[-1]
    has_extension = "." in last

    if has_extension:
        dir_part = root_out / parsed.netloc
        if len(segments) > 1:
            dir_part = dir_part.joinpath(*segments[:-1])
        return dir_part / last

    dir_part = root_out / parsed.netloc / Path(*segments)
    return dir_part / "index.html"


def extract_links(html_bytes: bytes, page_url: str) -> Set[str]:
    parser = LinkParser()
    text = html_bytes.decode("utf-8", errors="ignore")
    parser.feed(text)

    normalized: Set[str] = set()
    for raw in parser.links:
        clean = canonicalize(raw, base_url=page_url)
        if clean:
            normalized.add(clean)
    return normalized


def mirror(start_url: str, output_dir: Path, allowed_prefixes: Tuple[str, ...], timeout: int, delay_sec: float) -> Dict[str, object]:
    parsed_start = urlparse(start_url)
    host = parsed_start.netloc

    raw_dir = output_dir / "raw"
    cache_dir = output_dir / ".cache" / "http"
    cache_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    to_visit = deque([start_url])
    seen: Set[str] = set()
    manifest_pages: List[Dict[str, object]] = []

    while to_visit:
        current = to_visit.popleft()
        if current in seen:
            continue
        seen.add(current)

        result = fetch_url(current, cache_dir, timeout=timeout)
        local_path = url_to_local_path(current, raw_dir)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(result.body)

        discovered_links: Set[str] = set()
        is_html = "text/html" in result.content_type.lower() or local_path.suffix.lower() in {"", ".html"}
        if result.status == 200 and is_html:
            discovered_links = extract_links(result.body, current)
            for link in sorted(discovered_links):
                if in_scope(link, host=host, allowed_prefixes=allowed_prefixes) and link not in seen:
                    to_visit.append(link)

        manifest_pages.append(
            {
                "url": current,
                "status": result.status,
                "content_type": result.content_type,
                "from_cache": result.from_cache,
                "saved_to": str(local_path.relative_to(output_dir)).replace("\\", "/"),
                "bytes": len(result.body),
                "discovered_links": sorted(discovered_links),
            }
        )

        if delay_sec > 0:
            time.sleep(delay_sec)

    manifest = {
        "start_url": start_url,
        "captured_at": utc_now(),
        "scope": {
            "host": host,
            "allowed_prefixes": list(allowed_prefixes),
        },
        "page_count": len(manifest_pages),
        "pages": manifest_pages,
    }

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    index_lines = [
        "# EscapePlan Capture",
        "",
        f"Start URL: {start_url}",
        f"Captured at (UTC): {manifest['captured_at']}",
        f"Page count: {manifest['page_count']}",
        "",
        "## Pages",
    ]
    for page in manifest_pages:
        index_lines.append(f"- {page['url']} -> {page['saved_to']} (status {page['status']})")

    (output_dir / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror ngrok docs under a constrained prefix.")
    parser.add_argument("--start-url", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--allowed-prefix", action="append", required=True)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--delay", type=float, default=0.1)
    args = parser.parse_args()

    start = canonicalize(args.start_url)
    if not start:
        raise SystemExit("Invalid start URL")

    prefixes = tuple(sorted({p if p.endswith("/") else p + "/" for p in args.allowed_prefix}))

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = mirror(
        start_url=start,
        output_dir=out_dir,
        allowed_prefixes=prefixes,
        timeout=args.timeout,
        delay_sec=max(args.delay, 0.0),
    )

    print(json.dumps({"page_count": manifest["page_count"], "manifest": str(out_dir / "manifest.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
