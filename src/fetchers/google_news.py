"""Google News RSS fetcher for infectious disease topics (Japanese)."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import feedparser

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


def fetch() -> list[dict]:
    """Fetch Google News RSS for each disease query in parallel. Returns raw article list."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=_CUTOFF_DAYS)
    seen: set[str] = set()
    articles: list[dict] = []

    def _fetch_query(query: str) -> list[dict]:
        url = _BASE_URL.format(query=quote(query))
        try:
            feed = feedparser.parse(url)
            results = []
            for entry in feed.entries:
                link = entry.get("link", "")
                if not link:
                    continue
                pub_date = _parse_date(entry)
                if pub_date and pub_date < cutoff:
                    continue
                results.append({
                    "title": entry.get("title", "").strip(),
                    "url": link,
                    "date": pub_date.strftime("%Y-%m-%d") if pub_date else "",
                    "source": "Google ニュース",
                    "summary": entry.get("summary", "").strip(),
                })
            return results
        except Exception as e:
            logger.warning("Google News fetch failed for query %r: %s", query, e)
            return []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_fetch_query, q): q for q in _QUERIES}
        for future in as_completed(futures):
            for art in future.result():
                if art["url"] not in seen:
                    seen.add(art["url"])
                    articles.append(art)

    logger.info("Google News: fetched %d unique articles across %d queries", len(articles), len(_QUERIES))
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
