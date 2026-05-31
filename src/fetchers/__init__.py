"""Shared utilities for RSS/HTML fetchers."""

import html
import re


def strip_html(text: str) -> str:
    """Remove HTML tags from *text* and return plain text."""
    return re.sub(r"<[^>]+>", "", text).strip()


def clean_rss_title(raw: str, strip_source_suffix: bool = False) -> str:
    """Return a cleaned RSS article title.

    Steps:
    1. Decode HTML entities (&lt; → <, &amp; → &, etc.).
    2. Truncate at the first '<' — everything from '<' onward is always junk.
    3. If *strip_source_suffix* is True, remove trailing ' - Source Name'
       (Google News format: always the *last* ' - ' segment).
    """
    # Decode entities first so both '&lt;a' and literal '<a' are handled uniformly
    cleaned = html.unescape(raw)
    # Cut at the first '<' — simpler and handles unclosed tags too
    cleaned = cleaned.split("<")[0]
    if strip_source_suffix and " - " in cleaned:
        cleaned = cleaned.rsplit(" - ", 1)[0]
    return cleaned.strip()
