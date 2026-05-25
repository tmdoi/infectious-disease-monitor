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
