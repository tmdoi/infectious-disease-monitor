"""Shared utilities for RSS/HTML fetchers."""

import html
import re

from bs4 import BeautifulSoup


def clean_text(raw: str, strip_source_suffix: bool = False) -> str:
    """Return cleaned plain text from a raw RSS title or summary field.

    Steps:
    1. Decode HTML entities (&lt; → <, &amp; → &, etc.)
    2. Parse as HTML with BeautifulSoup and extract plain text
       (handles both complete tags and fragments like unclosed <a href="...">)
    3. Truncate at first '<' as a safety net for any unparsed fragment
    4. If strip_source_suffix is True, remove trailing ' - Source Name'
       (Google News format: always the last ' - ' segment)
    """
    cleaned = html.unescape(raw)
    cleaned = BeautifulSoup(cleaned, "html.parser").get_text(separator=" ", strip=True)
    if "<" in cleaned:
        cleaned = cleaned.split("<")[0]
    if strip_source_suffix and " - " in cleaned:
        cleaned = cleaned.rsplit(" - ", 1)[0]
    return cleaned.strip()


# Alias kept for any caller that still imports the old name
clean_rss_title = clean_text
