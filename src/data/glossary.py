"""Disease name glossary: internal IDs ↔ Japanese/English display names.

All components (filter, table, map, translator) import from here so that
disease names stay consistent and language-switching is handled in one place.
"""

from __future__ import annotations

# Order matches disease_filter.ALL_DISEASES_JA for consistent UI display.
DISEASE_ENTRIES: list[dict[str, str]] = [
    {"id": "ebola",        "ja": "エボラ出血熱",         "en": "Ebola"},
    {"id": "marburg",      "ja": "マールブルグ病",         "en": "Marburg"},
    {"id": "h5n1",         "ja": "H5N1型鳥インフルエンザ", "en": "H5N1 Avian Influenza"},
    {"id": "h7n9",         "ja": "H7N9型鳥インフルエンザ", "en": "H7N9 Avian Influenza"},
    {"id": "h9n2",         "ja": "H9N2型鳥インフルエンザ", "en": "H9N2 Avian Influenza"},
    {"id": "avian_flu",    "ja": "鳥インフルエンザ",       "en": "Avian Influenza"},
    {"id": "mers",         "ja": "MERS-CoV",             "en": "MERS-CoV"},
    {"id": "lassa",        "ja": "ラッサ熱",              "en": "Lassa Fever"},
    {"id": "dengue",       "ja": "デング熱",              "en": "Dengue"},
    {"id": "zika",         "ja": "ジカ熱",               "en": "Zika"},
    {"id": "hantavirus",   "ja": "ハンタウイルス感染症",    "en": "Hantavirus"},
    {"id": "nipah",        "ja": "ニパウイルス感染症",     "en": "Nipah"},
    {"id": "mpox",         "ja": "サル痘 (Mpox)",         "en": "Mpox"},
    {"id": "cholera",      "ja": "コレラ",               "en": "Cholera"},
    {"id": "yellow_fever", "ja": "黄熱",                 "en": "Yellow Fever"},
    {"id": "chikungunya",  "ja": "チクングニア熱",         "en": "Chikungunya"},
    {"id": "cchf",         "ja": "クリミア・コンゴ出血熱", "en": "Crimean-Congo Hemorrhagic Fever"},
    {"id": "measles",      "ja": "麻疹",                 "en": "Measles"},
]

# Derived lookup tables
_ID_TO_JA: dict[str, str] = {e["id"]: e["ja"] for e in DISEASE_ENTRIES}
_ID_TO_EN: dict[str, str] = {e["id"]: e["en"] for e in DISEASE_ENTRIES}
_JA_TO_ID: dict[str, str] = {e["ja"]: e["id"] for e in DISEASE_ENTRIES}
_JA_TO_EN: dict[str, str] = {e["ja"]: e["en"] for e in DISEASE_ENTRIES}

# Ordered list of all internal IDs (mirrors ALL_DISEASES_JA order)
ALL_DISEASE_IDS: list[str] = [e["id"] for e in DISEASE_ENTRIES]


def disease_display_name(disease_id: str, lang: str) -> str:
    """Return the display name for a disease ID in the given language."""
    if lang == "en":
        return _ID_TO_EN.get(disease_id, disease_id)
    return _ID_TO_JA.get(disease_id, disease_id)


def disease_id_from_ja(ja_name: str) -> str | None:
    """Return the internal ID for a Japanese disease name, or None if unknown."""
    return _JA_TO_ID.get(ja_name)


def ja_name_from_id(disease_id: str) -> str:
    """Return the Japanese disease name for an internal ID."""
    return _ID_TO_JA.get(disease_id, disease_id)


def disease_ja_to_display(ja_name: str, lang: str) -> str:
    """Convert a stored Japanese disease name to the target language display name."""
    if lang == "en":
        return _JA_TO_EN.get(ja_name, ja_name)
    return ja_name
