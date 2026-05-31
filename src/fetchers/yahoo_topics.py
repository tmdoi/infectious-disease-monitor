"""Yahoo Japan Topics RSS fetcher for infectious disease news."""

import logging
from datetime import datetime, timedelta, timezone

import feedparser

from src.fetchers import clean_rss_title

logger = logging.getLogger(__name__)

_RSS_URLS = [
    "https://news.yahoo.co.jp/rss/topics/top-picks.xml",
    "https://news.yahoo.co.jp/rss/topics/world.xml",
]
_CUTOFF_DAYS = 90


def fetch() -> list[dict]:
    """Fetch Yahoo Japan Topics RSS feeds. Returns raw article list (no disease filter applied)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=_CUTOFF_DAYS)
    articles: list[dict] = []
    seen: set[str] = set()
    for url in _RSS_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                link = entry.get("link", "")
                if not link or link in seen:
                    continue
                seen.add(link)
                pub_date = _parse_struct_time(entry)
                if pub_date and pub_date < cutoff:
                    continue
                articles.append({
                    "title": clean_rss_title(entry.get("title", "")),
                    "url": link,
                    "date": pub_date.strftime("%Y-%m-%d") if pub_date else "",
                    "source": "Yahoo Japan",
                    "summary": entry.get("summary", "").strip(),
                })
        except Exception as e:
            logger.warning("Yahoo RSS fetch failed for %s: %s", url, e)
    return articles


def _parse_struct_time(entry) -> datetime | None:
    for field in ("published_parsed", "updated_parsed"):
        t = getattr(entry, field, None)
        if t:
            try:
                return datetime(t.tm_year, t.tm_mon, t.tm_mday, tzinfo=timezone.utc)
            except (ValueError, TypeError):
                pass
    return None
