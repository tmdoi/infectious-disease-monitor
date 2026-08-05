"""Shared utilities for RSS/HTML fetchers."""

import html
import re

from bs4 import BeautifulSoup

# 写真クレジットとして頻出する語（小文字で比較）。1つでも含まれる場合のみ除去する。
_CREDIT_KEYWORDS: frozenset[str] = frozenset({
    "getty images", "getty", "getty images/istockphoto", "istock", "istockphoto",
    "shutterstock", "adobe stock", "e+", "moment", "digitalvision", "file",
    "ap", "afp", "afp=時事", "reuters", "ロイター", "epa", "afpbb news",
    "cdc", "fda", "who", "cnn", "bbc", "nhk", "共同通信", "時事通信",
    "提供", "撮影", "写真", "画像",
})

# クレジット断片として許容する形（英数字と一部記号のみ。括弧・数字のみは不可）。
# 例: "Melanie Moser", "Getty Images", "E+", "deepblue4you", "File"
_CREDIT_SEGMENT = re.compile(r"^[A-Za-z][A-Za-z0-9 .,'&+_-]{0,29}$")

# クレジット除去後に残すべき最小文字数（過剰除去の防止）
_MIN_TITLE_LEN = 8


def _is_credit_segment(seg: str) -> bool:
    """Return True if a '/'-separated segment looks like a photo credit fragment."""
    return seg.lower() in _CREDIT_KEYWORDS or bool(_CREDIT_SEGMENT.match(seg))


def strip_photo_credit(text: str) -> str:
    """Remove a trailing '/'-separated photo credit chain (e.g. '…/Getty Images/File').

    Only strips when the trailing chain contains at least one known credit keyword
    and enough text remains, so titles that legitimately contain '/' are preserved.
    """
    if "/" not in text:
        return text

    segments = re.split(r"\s*/\s*", text)
    if len(segments) < 2:
        return text

    # 末尾から連続するクレジット断片を集める
    cut = len(segments)
    while cut > 1 and _is_credit_segment(segments[cut - 1]):
        cut -= 1

    stripped = segments[cut:]
    if not stripped or not any(s.lower() in _CREDIT_KEYWORDS for s in stripped):
        return text

    head = " / ".join(segments[:cut]).strip()
    if len(head) < _MIN_TITLE_LEN:
        return text
    return head


def clean_text(raw: str, strip_source_suffix: bool = False) -> str:
    """Return cleaned plain text from a raw RSS title or summary field.

    Steps:
    1. Decode HTML entities (&lt; → <, &amp; → &, etc.)
    2. Parse as HTML with BeautifulSoup and extract plain text
       (handles both complete tags and fragments like unclosed <a href="...">)
    3. Truncate at first '<' as a safety net for any unparsed fragment
    4. If strip_source_suffix is True, remove trailing ' - Source Name'
       (Google News format: always the last ' - ' segment)
    5. Remove a trailing photo-credit chain ('…/Melanie Moser/CDC/AP')
    """
    cleaned = html.unescape(raw)
    cleaned = BeautifulSoup(cleaned, "html.parser").get_text(separator=" ", strip=True)
    if "<" in cleaned:
        cleaned = cleaned.split("<")[0]
    if strip_source_suffix and " - " in cleaned:
        cleaned = cleaned.rsplit(" - ", 1)[0]
    cleaned = strip_photo_credit(cleaned)
    return cleaned.strip()


# Alias kept for any caller that still imports the old name
clean_rss_title = clean_text
