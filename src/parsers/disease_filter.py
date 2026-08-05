"""Keyword-based disease filter for WHO DON and ECDC articles."""

# keyword (case-insensitive match) → Japanese display name
# More-specific subtype keywords must come before "Avian influenza" to match first.
DISEASE_KEYWORDS: dict[str, str] = {
    "Ebola": "エボラ出血熱",
    "Marburg": "マールブルグ病",
    "H5N1": "H5N1型鳥インフルエンザ",
    "H7N9": "H7N9型鳥インフルエンザ",
    "H9N2": "H9N2型鳥インフルエンザ",
    "Avian influenza": "鳥インフルエンザ",
    "MERS": "MERS-CoV",
    "Lassa": "ラッサ熱",
    "Dengue": "デング熱",
    "Zika": "ジカ熱",
    "Hantavirus": "ハンタウイルス感染症",
    "Nipah": "ニパウイルス感染症",
    "Mpox": "サル痘 (Mpox)",
    "Monkeypox": "サル痘 (Mpox)",
    "Cholera": "コレラ",
    "Yellow fever": "黄熱",
    "Chikungunya": "チクングニア熱",
    "Crimean-Congo": "クリミア・コンゴ出血熱",
    "Measles": "麻疹",
    # "Cyclosporiasis" does not contain the substring "Cyclospora", so both are needed.
    "Cyclospora cayetanensis": "サイクロスポラ症",
    "Cyclosporiasis": "サイクロスポラ症",
    "Cyclospora": "サイクロスポラ症",
}

# De-duplicated list of Japanese names for UI multiselect
ALL_DISEASES_JA: list[str] = list(dict.fromkeys(DISEASE_KEYWORDS.values()))


def detect_disease(title: str) -> str | None:
    """Return Japanese disease name if title matches a target disease keyword, else None."""
    title_lower = title.lower()
    for keyword, ja_name in DISEASE_KEYWORDS.items():
        if keyword.lower() in title_lower:
            return ja_name
    return None


def filter_articles(articles: list[dict]) -> list[dict]:
    """Filter to target diseases only, adding 'disease_ja' field to each match."""
    result = []
    for article in articles:
        disease_ja = detect_disease(article.get("title", ""))
        if disease_ja:
            result.append({**article, "disease_ja": disease_ja})
    return result


# ── Japanese keyword support (for Yahoo Japan articles) ───────────────────────

# Japanese disease keywords → Japanese display name.
# English subtypes (H5N1, MERS, etc.) are intentionally omitted here because
# detect_disease() (English check) is run first inside detect_disease_ja().
DISEASE_KEYWORDS_JA: dict[str, str] = {
    "エボラ": "エボラ出血熱",
    "マールブルグ": "マールブルグ病",
    "鳥インフルエンザ": "鳥インフルエンザ",
    "ラッサ": "ラッサ熱",
    "デング": "デング熱",
    "ジカ": "ジカ熱",
    "ハンタウイルス": "ハンタウイルス感染症",
    "ニパウイルス": "ニパウイルス感染症",
    "ニパ": "ニパウイルス感染症",
    "サル痘": "サル痘 (Mpox)",
    "コレラ": "コレラ",
    "黄熱": "黄熱",
    "チクングニア": "チクングニア熱",
    "クリミア・コンゴ": "クリミア・コンゴ出血熱",
    "麻疹": "麻疹",
    "サイクロスポラ症": "サイクロスポラ症",
    "サイクロスポラ": "サイクロスポラ症",
}

# General epidemic terms: only produce "未分類" when no specific keyword matches.
_GENERAL_JA: list[str] = [
    "感染症", "アウトブレイク", "集団感染", "感染拡大", "パンデミック",
]


def detect_disease_ja(title: str) -> str | None:
    """Detect disease from a Japanese-language title.

    Returns a Japanese disease name, '未分類' (general epidemic news), or None.
    English subtype keywords (H5N1, MERS, etc.) are checked first via detect_disease().
    """
    # English keywords first — preserves H5N1 > Avian influenza priority ordering.
    result = detect_disease(title)
    if result:
        return result
    # Japanese-specific disease keywords.
    for keyword, disease_ja in DISEASE_KEYWORDS_JA.items():
        if keyword in title:
            return disease_ja
    # General epidemic vocabulary → low-confidence match.
    if any(kw in title for kw in _GENERAL_JA):
        return "未分類"
    return None


def filter_yahoo_articles(articles: list[dict]) -> list[dict]:
    """Filter Yahoo articles to target diseases, adding 'disease_ja'. Excludes 未分類."""
    result = []
    for article in articles:
        disease_ja = detect_disease_ja(article.get("title", ""))
        if disease_ja and disease_ja != "未分類":
            result.append({**article, "disease_ja": disease_ja})
    return result
