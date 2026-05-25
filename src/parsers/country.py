"""Country name → ISO 3166-1 alpha-3 conversion with WHO title parsing."""

import logging
import re

import pycountry

logger = logging.getLogger(__name__)

# Manually curated map for WHO abbreviations and alternate spellings
_MANUAL: dict[str, str] = {
    "DRC": "COD",
    "DR Congo": "COD",
    "Democratic Republic of Congo": "COD",
    "Democratic Republic of the Congo": "COD",
    "Congo, The Democratic Republic of the": "COD",
    "Congo, DR": "COD",
    "Republic of Congo": "COG",
    "Republic of Korea": "KOR",
    "South Korea": "KOR",
    "North Korea": "PRK",
    "DPRK": "PRK",
    "Iran": "IRN",
    "Syria": "SYR",
    "Bolivia": "BOL",
    "Tanzania": "TZA",
    "United Republic of Tanzania": "TZA",
    "Laos": "LAO",
    "Moldova": "MDA",
    "Palestine": "PSE",
    "State of Palestine": "PSE",
    "Türkiye": "TUR",
    "Turkey": "TUR",
    "Viet Nam": "VNM",
    "Vietnam": "VNM",
    "Ivory Coast": "CIV",
    "Côte d'Ivoire": "CIV",
    "Cote d'Ivoire": "CIV",
    "Swaziland": "SWZ",
    "Eswatini": "SWZ",
    "Cape Verde": "CPV",
    "Cabo Verde": "CPV",
    "Czech Republic": "CZE",
    "Czechia": "CZE",
    "Venezuela": "VEN",
    "Russia": "RUS",
    "United States": "USA",
    "United States of America": "USA",
    "USA": "USA",
    "UK": "GBR",
    "United Kingdom": "GBR",
    "UAE": "ARE",
    "Central African Republic": "CAF",
    "Trinidad and Tobago": "TTO",
    "Sao Tome and Principe": "STP",
    "São Tomé and Príncipe": "STP",
    "Bosnia and Herzegovina": "BIH",
    "Bosnia": "BIH",
    "North Macedonia": "MKD",
    "Sudan": "SDN",
    "South Sudan": "SSD",
    "Micronesia": "FSM",
    "Federated States of Micronesia": "FSM",
}

# ISO3 → Japanese display name for common outbreak countries
_ISO3_JA: dict[str, str] = {
    "COD": "コンゴ民主共和国",
    "NGA": "ナイジェリア",
    "CHN": "中国",
    "BRA": "ブラジル",
    "IND": "インド",
    "SAU": "サウジアラビア",
    "SSD": "南スーダン",
    "BGD": "バングラデシュ",
    "UGA": "ウガンダ",
    "KEN": "ケニア",
    "GIN": "ギニア",
    "LBR": "リベリア",
    "SLE": "シエラレオネ",
    "SDN": "スーダン",
    "ETH": "エチオピア",
    "ZMB": "ザンビア",
    "TZA": "タンザニア",
    "CMR": "カメルーン",
    "CAF": "中央アフリカ共和国",
    "CIV": "コートジボワール",
    "SOM": "ソマリア",
    "HTI": "ハイチ",
    "PAK": "パキスタン",
    "IDN": "インドネシア",
    "PHL": "フィリピン",
    "VNM": "ベトナム",
    "KHM": "カンボジア",
    "THA": "タイ",
    "MMR": "ミャンマー",
    "EGY": "エジプト",
    "IRQ": "イラク",
    "IRN": "イラン",
    "YEM": "イエメン",
    "AFG": "アフガニスタン",
    "ARE": "アラブ首長国連邦",
    "COG": "コンゴ共和国",
    "GHA": "ガーナ",
    "ZWE": "ジンバブエ",
    "MOZ": "モザンビーク",
    "MWI": "マラウイ",
    "RWA": "ルワンダ",
    "BDI": "ブルンジ",
    "AGO": "アンゴラ",
    "MEX": "メキシコ",
    "COL": "コロンビア",
    "PER": "ペルー",
    "VEN": "ベネズエラ",
    "ECU": "エクアドル",
    "BOL": "ボリビア",
    "ARG": "アルゼンチン",
    "USA": "アメリカ合衆国",
    "GBR": "イギリス",
    "DEU": "ドイツ",
    "FRA": "フランス",
    "ITA": "イタリア",
    "ESP": "スペイン",
    "RUS": "ロシア",
    "UKR": "ウクライナ",
    "TUR": "トルコ",
    "GRC": "ギリシャ",
    "JPN": "日本",
    "KOR": "韓国",
    "MNG": "モンゴル",
    "KAZ": "カザフスタン",
    "SDN": "スーダン",
    "SSD": "南スーダン",
}


# Japanese country name → ISO3 (for Yahoo Japan article title parsing)
_MANUAL_JA: dict[str, str] = {
    "日本": "JPN",
    "米国": "USA",
    "アメリカ": "USA",
    "アメリカ合衆国": "USA",
    "中国": "CHN",
    "韓国": "KOR",
    "北朝鮮": "PRK",
    "ドイツ": "DEU",
    "フランス": "FRA",
    "イタリア": "ITA",
    "スペイン": "ESP",
    "英国": "GBR",
    "イギリス": "GBR",
    "ロシア": "RUS",
    "ウクライナ": "UKR",
    "オーストラリア": "AUS",
    "カナダ": "CAN",
    "ブラジル": "BRA",
    "メキシコ": "MEX",
    "コロンビア": "COL",
    "ペルー": "PER",
    "エクアドル": "ECU",
    "ボリビア": "BOL",
    "アルゼンチン": "ARG",
    "ベネズエラ": "VEN",
    "インド": "IND",
    "パキスタン": "PAK",
    "バングラデシュ": "BGD",
    "フィリピン": "PHL",
    "インドネシア": "IDN",
    "マレーシア": "MYS",
    "シンガポール": "SGP",
    "タイ": "THA",
    "ベトナム": "VNM",
    "ミャンマー": "MMR",
    "カンボジア": "KHM",
    "台湾": "TWN",
    "香港": "HKG",
    "イラン": "IRN",
    "イラク": "IRQ",
    "サウジアラビア": "SAU",
    "アラブ首長国連邦": "ARE",
    "UAE": "ARE",
    "トルコ": "TUR",
    "シリア": "SYR",
    "レバノン": "LBN",
    "イスラエル": "ISR",
    "パレスチナ": "PSE",
    "エジプト": "EGY",
    "ナイジェリア": "NGA",
    "南アフリカ": "ZAF",
    "エチオピア": "ETH",
    "ウガンダ": "UGA",
    "ケニア": "KEN",
    "タンザニア": "TZA",
    "ガーナ": "GHA",
    "セネガル": "SEN",
    "ギニア": "GIN",
    "シエラレオネ": "SLE",
    "リベリア": "LBR",
    "コートジボワール": "CIV",
    "コンゴ民主共和国": "COD",
    "コンゴ共和国": "COG",
    "コンゴ": "COD",   # ambiguous; default to DRC as more common in outbreak news
    "南スーダン": "SSD",
    "スーダン": "SDN",
    "ソマリア": "SOM",
    "イエメン": "YEM",
    "アフガニスタン": "AFG",
    "カメルーン": "CMR",
    "中央アフリカ共和国": "CAF",
    "中央アフリカ": "CAF",
    "アンゴラ": "AGO",
    "モザンビーク": "MOZ",
    "マラウイ": "MWI",
    "ザンビア": "ZMB",
    "ルワンダ": "RWA",
    "ブルンジ": "BDI",
    "ハイチ": "HTI",
    "モンゴル": "MNG",
    "カザフスタン": "KAZ",
    "ウズベキスタン": "UZB",
}


def name_to_iso3(name: str) -> str | None:
    """Convert country name to ISO3 code. Returns None if unresolvable."""
    name = name.strip()
    if not name:
        return None
    if name in _MANUAL:
        return _MANUAL[name]
    name_lower = name.lower()
    for k, v in _MANUAL.items():
        if k.lower() == name_lower:
            return v
    result = pycountry.countries.get(name=name)
    if result:
        return result.alpha_3
    try:
        results = pycountry.countries.search_fuzzy(name)
        if results:
            return results[0].alpha_3
    except LookupError:
        pass
    logger.debug("Unresolved country name: %r", name)
    return None


def iso3_to_display_name(iso3: str) -> str:
    """Return Japanese name for ISO3, falling back to pycountry English name."""
    if iso3 in _ISO3_JA:
        return _ISO3_JA[iso3]
    country = pycountry.countries.get(alpha_3=iso3)
    return country.name if country else iso3


def extract_countries_from_title_ja(title: str) -> list[str]:
    """Scan a Japanese-language title for known country names and return ISO3 codes.

    Longer/more-specific names are checked first to avoid partial shadowing
    (e.g. 'コンゴ民主共和国' matches before 'コンゴ').
    """
    iso3_list: list[str] = []
    seen: set[str] = set()
    for ja_name, iso3 in sorted(_MANUAL_JA.items(), key=lambda x: len(x[0]), reverse=True):
        if ja_name in title and iso3 not in seen:
            iso3_list.append(iso3)
            seen.add(iso3)
    return iso3_list


def extract_countries_from_title(title: str) -> list[str]:
    """Parse WHO DON title and return list of ISO3 codes.

    Handles two formats:
    - Standard: 'Disease – Country' (em-dash separator)
    - Override:  'Disease, Country1 & Country2' (comma separator)
    Returns empty list for multi-country/worldwide entries.
    """
    # Standard format: em-dash or en-dash separator
    dash_parts = re.split(r"\s*[–—]\s*|\s+-\s+", title, maxsplit=1)
    if len(dash_parts) >= 2:
        country_part = dash_parts[1].strip().rstrip(".")
    else:
        # Override format: split on last ", " and take the tail as countries
        comma_parts = title.rsplit(", ", 1)
        if len(comma_parts) < 2:
            return []
        country_part = comma_parts[1].strip().rstrip(".")

    # Skip generic multi-country entries
    _SKIP = {"multi-country", "multiple countries", "worldwide", "global", "several countries"}
    if country_part.lower() in _SKIP:
        return []

    # Split compound country names: "Italy and France", "COD & Uganda"
    country_names = re.split(r"\s+and\s+|\s*&\s*", country_part, flags=re.I)
    iso3_list: list[str] = []
    for cname in country_names:
        cname = cname.strip().rstrip(".")
        iso3 = name_to_iso3(cname)
        if iso3:
            iso3_list.append(iso3)
        else:
            logger.info("Unresolved country %r in title: %r", cname, title)
    return iso3_list
