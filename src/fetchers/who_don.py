"""WHO Disease Outbreak News (DON) fetcher.

Uses the WHO internal OData API to avoid unreliable RSS/HTML scraping.
Falls back to HTML scraping if the API is unavailable.
"""

import logging
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

from src.fetchers import clean_text

logger = logging.getLogger(__name__)

_API_URL = "https://www.who.int/api/emergencies/diseaseoutbreaknews"
_LIST_URL = "https://www.who.int/emergencies/disease-outbreak-news"
_ITEM_BASE = "https://www.who.int/emergencies/disease-outbreak-news/item"
_CUTOFF_DAYS = 90
_PAGE_SIZE = 100
_HEADERS = {"User-Agent": "Mozilla/5.0 (infectious-disease-monitor/1.0)"}
_TIMEOUT = 20


def fetch() -> list[dict]:
    """Fetch WHO DON articles for the past 90 days. Returns raw article list."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=_CUTOFF_DAYS)
    articles = _from_api(cutoff)
    if not articles:
        logger.warning("WHO API returned nothing; falling back to HTML scrape")
        articles = _from_html(cutoff)
    return articles


def _from_api(cutoff: datetime) -> list[dict]:
    """Fetch articles via WHO OData API, paging until cutoff is passed."""
    articles: list[dict] = []
    skip = 0
    while True:
        params = {
            "sf_provider": "dynamicProvider372",
            "sf_culture": "en",
            "$orderby": "PublicationDateAndTime desc",
            "$select": "Title,OverrideTitle,UseOverrideTitle,ItemDefaultUrl,FormattedDate,PublicationDateAndTime",
            "$top": str(_PAGE_SIZE),
            "$skip": str(skip),
        }
        try:
            resp = requests.get(_API_URL, params=params, timeout=_TIMEOUT, headers=_HEADERS)
            resp.raise_for_status()
            batch = resp.json().get("value", [])
        except Exception as e:
            logger.error("WHO API request failed (skip=%d): %s", skip, e)
            break
        if not batch:
            break
        for item in batch:
            pub_str = item.get("PublicationDateAndTime", "")
            try:
                pub_date = datetime.fromisoformat(pub_str.rstrip("Z")).replace(tzinfo=timezone.utc)
            except (ValueError, AttributeError):
                pub_date = None
            if pub_date and pub_date < cutoff:
                return articles  # API is sorted desc; stop here
            title = clean_text(
                item["OverrideTitle"] if item.get("UseOverrideTitle") and item.get("OverrideTitle")
                else item.get("Title", "")
            )
            url_path = item.get("ItemDefaultUrl", "")
            url = _ITEM_BASE + url_path if url_path else ""
            articles.append({
                "title": title,
                "url": url,
                "date": pub_date.strftime("%Y-%m-%d") if pub_date else item.get("FormattedDate", ""),
                "source": "WHO DON",
            })
        skip += len(batch)
        if len(batch) < _PAGE_SIZE:
            break
    return articles


def _from_html(cutoff: datetime) -> list[dict]:
    """Fallback: scrape the WHO DON listing page."""
    try:
        resp = requests.get(_LIST_URL, timeout=_TIMEOUT, headers=_HEADERS)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        articles = []
        for a_tag in soup.select("a[href*='/emergencies/disease-outbreak-news/item/']"):
            title = clean_text(a_tag.get_text(strip=True))
            if not title:
                continue
            href = a_tag.get("href", "")
            url = ("https://www.who.int" + href) if href.startswith("/") else href
            pub_date = _nearby_date(a_tag)
            if pub_date and pub_date < cutoff:
                continue
            articles.append({
                "title": title,
                "url": url,
                "date": pub_date.strftime("%Y-%m-%d") if pub_date else "",
                "source": "WHO DON",
            })
        return articles
    except Exception as e:
        logger.error("HTML fallback failed: %s", e)
        return []


def _nearby_date(tag) -> datetime | None:
    """Search parent elements for a parseable date string."""
    for elem in (tag.parent, tag.find_parent("li"), tag.find_parent("div")):
        if elem is None:
            continue
        for text in elem.find_all(string=True):
            text = text.strip()
            if 5 < len(text) < 30:
                dt = _parse_date(text)
                if dt:
                    return dt
    return None


def _parse_date(text: str) -> datetime | None:
    for fmt in ("%d %B %Y", "%B %d, %Y", "%Y-%m-%d", "%d %b %Y"):
        try:
            return datetime.strptime(text.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None
