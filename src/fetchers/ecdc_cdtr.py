"""ECDC Communicable Disease Threats Report (CDTR) fetcher.

Scrapes the ECDC weekly threats listing page and returns report metadata.
PDF parsing is out of scope; records contain title, date, and report URL.
"""

import logging
import re
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_LIST_URL = "https://www.ecdc.europa.eu/en/publications-and-data/monitoring/weekly-threats-reports"
_BASE_URL = "https://www.ecdc.europa.eu"
_CUTOFF_DAYS = 90
_HEADERS = {"User-Agent": "Mozilla/5.0 (infectious-disease-monitor/1.0)"}
_TIMEOUT = 20

_MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def fetch() -> list[dict]:
    """Scrape ECDC CDTR listing. Returns report metadata for the past 90 days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=_CUTOFF_DAYS)
    try:
        resp = requests.get(_LIST_URL, timeout=_TIMEOUT, headers=_HEADERS)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        return _parse(soup, cutoff)
    except Exception as e:
        logger.error("ECDC CDTR fetch failed: %s", e)
        return []


def _parse(soup: BeautifulSoup, cutoff: datetime) -> list[dict]:
    reports: list[dict] = []
    seen: set[str] = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        title = a_tag.get_text(strip=True)
        # Match links to individual CDTR report pages
        if "/publications-data/communicable-disease-threats-report" not in href:
            continue
        if href in seen:
            continue
        seen.add(href)
        url = (_BASE_URL + href) if href.startswith("/") else href
        pub_date = _date_from_title(title) or _date_from_url(href)
        if pub_date and pub_date < cutoff:
            continue
        reports.append({
            "title": title,
            "url": url,
            "date": pub_date.strftime("%Y-%m-%d") if pub_date else "",
            "source": "ECDC CDTR",
        })
    return reports


def _date_from_title(title: str) -> datetime | None:
    """Extract date from titles like 'Communicable disease threats report, 14-22 May 2026, Week 21'."""
    # Look for patterns with month name and 4-digit year
    m = re.search(
        r"(\d{1,2})(?:\s*[-–]\s*\d{1,2})?\s+"
        r"(january|february|march|april|may|june|july|august|september|october|november|december)"
        r"\s+(\d{4})",
        title,
        re.I,
    )
    if m:
        day, month_str, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        month = _MONTH_MAP.get(month_str)
        if month:
            try:
                return datetime(year, month, day, tzinfo=timezone.utc)
            except ValueError:
                pass
    return None


def _date_from_url(href: str) -> datetime | None:
    """Extract date from URL slug like 'communicable-disease-threats-report-14-22-may-2026-week-21'."""
    m = re.search(
        r"(\d{1,2})-(\d{1,2})-"
        r"(january|february|march|april|may|june|july|august|september|october|november|december)"
        r"-(\d{4})",
        href,
        re.I,
    )
    if m:
        day, month_str, year = int(m.group(1)), m.group(3).lower(), int(m.group(4))
        month = _MONTH_MAP.get(month_str)
        if month:
            try:
                return datetime(year, month, day, tzinfo=timezone.utc)
            except ValueError:
                pass
    return None
