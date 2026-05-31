"""Google News RSS fetcher for infectious disease topics (Japanese)."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from urllib.parse import quote

import feedparser

from src.fetchers import clean_text
from src.parsers import source_whitelist

logger = logging.getLogger(__name__)

_CUTOFF_DAYS = 90
_BASE_URL = "https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"

_QUERIES = [
    "エボラ出血熱",
    "マールブルグ病",
    "鳥インフルエンザ H5N1",
    "MERS コロナウイルス",
    "ラッサ熱",
    "デング熱 アウトブレイク",
    "ジカ熱",
    "ニパウイルス",
    "サル痘 Mpox",
    "コレラ アウトブレイク",
    "黄熱",
    "感染症 アウトブレイク",
]


class _LinkExtractor(HTMLParser):
    """Collect href values from <a> tags in an HTML fragment."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.links.append(value)


def _extract_source_url(entry) -> str | None:
    """Return the original publisher URL from a feedparser Google News entry."""
    # feedparser exposes <source> as entry.source (FeedParserDict with href/title)
    src = getattr(entry, "source", None)
    if src:
        href = src.get("href", "") if isinstance(src, dict) else getattr(src, "href", "")
        if href and not href.startswith("https://news.google.com"):
            return href

    # Fall back to first non-Google <a href> in the description HTML
    description = entry.get("summary", "") or entry.get("description", "")
    if description:
        extractor = _LinkExtractor()
        extractor.feed(description)
        for link in extractor.links:
            if link and not link.startswith("https://news.google.com"):
                return link

    return None


def fetch() -> list[dict]:
    """Fetch Google News RSS for each disease query in parallel. Returns trusted-source articles only."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=_CUTOFF_DAYS)
    seen: set[str] = set()
    articles: list[dict] = []
    discarded = 0

    def _fetch_query(query: str) -> tuple[list[dict], int]:
        url = _BASE_URL.format(query=quote(query))
        try:
            feed = feedparser.parse(url)
            results: list[dict] = []
            dropped = 0
            for entry in feed.entries:
                link = entry.get("link", "")
                if not link:
                    continue
                pub_date = _parse_date(entry)
                if pub_date and pub_date < cutoff:
                    continue

                source_url = _extract_source_url(entry)
                if not source_url:
                    dropped += 1
                    continue
                publisher = source_whitelist.get_trusted_label(source_url)
                if not publisher:
                    dropped += 1
                    continue

                results.append({
                    "title": clean_text(entry.get("title", ""), strip_source_suffix=True),
                    "url": link,
                    "date": pub_date.strftime("%Y-%m-%d") if pub_date else "",
                    "source": "Google ニュース",
                    "publisher": publisher,
                    "summary": clean_text(entry.get("summary", "")),
                })
            return results, dropped
        except Exception as e:
            logger.warning("Google News fetch failed for query %r: %s", query, e)
            return [], 0

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_fetch_query, q): q for q in _QUERIES}
        for future in as_completed(futures):
            results, dropped = future.result()
            discarded += dropped
            for art in results:
                if art["url"] not in seen:
                    seen.add(art["url"])
                    articles.append(art)

    logger.info(
        "Google News: fetched %d unique trusted articles (%d discarded) across %d queries",
        len(articles),
        discarded,
        len(_QUERIES),
    )
    return articles


def _parse_date(entry) -> datetime | None:
    for field in ("published_parsed", "updated_parsed"):
        t = getattr(entry, field, None)
        if t:
            try:
                return datetime(t.tm_year, t.tm_mon, t.tm_mday, tzinfo=timezone.utc)
            except (ValueError, TypeError):
                pass
    return None
