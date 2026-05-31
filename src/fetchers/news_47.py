"""47NEWS RSS fetcher for infectious disease news."""

import logging
from datetime import datetime, timedelta, timezone

import feedparser

from src.fetchers import clean_rss_title

logger = logging.getLogger(__name__)

_RSS_CANDIDATES = [
    "https://www.47news.jp/feed/index.rdf",
    "https://www.47news.jp/rss/index.rdf",
    "https://www.47news.jp/feed/",
]
_CUTOFF_DAYS = 90


def fetch() -> list[dict]:
    """Fetch 47NEWS RSS feed. Returns raw article list (no disease filter applied)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=_CUTOFF_DAYS)
    for url in _RSS_CANDIDATES:
        try:
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                logger.debug("47NEWS RSS parse issue at %s: %s", url, feed.bozo_exception)
                continue
            if not feed.entries:
                logger.debug("47NEWS RSS returned no entries at %s", url)
                continue
            articles: list[dict] = []
            seen: set[str] = set()
            for entry in feed.entries:
                link = entry.get("link", "")
                if not link or link in seen:
                    continue
                seen.add(link)
                pub_date = _parse_date(entry)
                if pub_date and pub_date < cutoff:
                    continue
                articles.append({
                    "title": clean_rss_title(entry.get("title", "")),
                    "url": link,
                    "date": pub_date.strftime("%Y-%m-%d") if pub_date else "",
                    "source": "47NEWS",
                    "summary": entry.get("summary", "").strip(),
                })
            logger.info("47NEWS: fetched %d articles from %s", len(articles), url)
            return articles
        except Exception as e:
            logger.warning("47NEWS RSS fetch failed for %s: %s", url, e)
    logger.warning("47NEWS: all RSS URLs failed, returning empty list")
    return []


def _parse_date(entry) -> datetime | None:
    for field in ("published_parsed", "updated_parsed"):
        t = getattr(entry, field, None)
        if t:
            try:
                return datetime(t.tm_year, t.tm_mon, t.tm_mday, tzinfo=timezone.utc)
            except (ValueError, TypeError):
                pass
    return None
