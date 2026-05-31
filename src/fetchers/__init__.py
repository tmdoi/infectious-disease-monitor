"""Shared utilities for RSS/HTML fetchers."""

import re


def strip_html(text: str) -> str:
    """Remove HTML tags from *text* and return plain text."""
    return re.sub(r"<[^>]+>", "", text).strip()


def clean_rss_title(raw: str, strip_source_suffix: bool = False) -> str:
    """Return a cleaned RSS article title.

    Steps:
    1. Truncate at the first '<' (catches HTML fragments that bleed past tags).
    2. Strip any residual inline HTML tags.
    3. If *strip_source_suffix* is True, remove trailing ' - Source Name'
       (Google News format: always the *last* ' - ' segment).
    """
    # Cut off everything from the first '<' — it's always junk in a title
    cleaned = re.sub(r"\s*<.*", "", raw, flags=re.DOTALL)
    # Belt-and-suspenders: remove any stray tags left behind
    cleaned = strip_html(cleaned)
    if strip_source_suffix and " - " in cleaned:
        cleaned = cleaned.rsplit(" - ", 1)[0]
    return cleaned.strip()
