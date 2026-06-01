"""Country name → ISO 3166-1 alpha-3 conversion with multi-language support."""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path

import pycountry

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO))

_LOG_DIR = Path(__file__).parents[2] / "data" / "cache"
_LOG_FILE = _LOG_DIR / "country_extraction.log"


def _setup_log() -> None:
    if any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        return
    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(_LOG_FILE, mode="a", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
    except Exception:
        pass


_setup_log()


# ── Legacy lookup tables (kept for name_to_iso3 backward compat) ─────────────

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
    "CAN": "カナダ",
    "AUS": "オーストラリア",
    "NZL": "ニュージーランド",
    "MYS": "マレーシア",
    "SGP": "シンガポール",
    "TWN": "台湾",
    "HKG": "香港",
    "ISR": "イスラエル",
    "PSE": "パレスチナ",
    "LBN": "レバノン",
    "SYR": "シリア",
    "ZAF": "南アフリカ",
    "SEN": "セネガル",
    "UZB": "ウズベキスタン",
    "NPL": "ネパール",
    "LKA": "スリランカ",
    "LAO": "ラオス",
    "PRK": "北朝鮮",
}

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
    "コンゴ": "COD",
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
    "ネパール": "NPL",
    "スリランカ": "LKA",
    "ラオス": "LAO",
    "ジンバブエ": "ZWE",
    "マダガスカル": "MDG",
    "ニュージーランド": "NZL",
    "チリ": "CHL",
    "チェコ": "CZE",
    "ハンガリー": "HUN",
    "ポーランド": "POL",
    "ルーマニア": "ROU",
    "ギリシャ": "GRC",
    "ポルトガル": "PRT",
    "アイルランド": "IRL",
    "スウェーデン": "SWE",
    "ノルウェー": "NOR",
    "デンマーク": "DNK",
    "フィンランド": "FIN",
    "オランダ": "NLD",
    "ベルギー": "BEL",
    "スイス": "CHE",
    "オーストリア": "AUT",
}


# ── Comprehensive alias dictionary (ISO3 → list of name variants) ─────────────

COUNTRY_ALIASES: dict[str, list[str]] = {
    "USA": ["米国", "アメリカ", "アメリカ合衆国", "合衆国", "USA", "US", "U.S.", "U.S.A.",
            "United States", "United States of America"],
    "KOR": ["韓国", "南朝鮮", "大韓民国", "Korea", "South Korea", "Republic of Korea", "ROK"],
    "PRK": ["北朝鮮", "朝鮮民主主義人民共和国", "DPRK", "North Korea",
            "Democratic People's Republic of Korea"],
    "CHN": ["中国", "中華人民共和国", "China", "PRC", "People's Republic of China"],
    "TWN": ["台湾", "Taiwan", "Republic of China", "ROC", "Chinese Taipei"],
    "HKG": ["香港", "Hong Kong"],
    "JPN": ["日本", "Japan", "ニッポン"],
    "GBR": ["英国", "イギリス", "UK", "U.K.", "United Kingdom", "Britain", "Great Britain"],
    "DEU": ["ドイツ", "Germany", "独国"],
    "FRA": ["フランス", "France", "仏国"],
    "ITA": ["イタリア", "Italy", "伊国"],
    "ESP": ["スペイン", "Spain", "西国"],
    "RUS": ["ロシア", "Russia", "ロシア連邦", "Russian Federation", "露"],
    "UKR": ["ウクライナ", "Ukraine"],
    "TUR": ["トルコ", "Turkey", "Türkiye"],
    "IND": ["インド", "India"],
    "PAK": ["パキスタン", "Pakistan"],
    "BGD": ["バングラデシュ", "Bangladesh"],
    "IDN": ["インドネシア", "Indonesia"],
    "THA": ["タイ", "タイ国", "Thailand"],
    "VNM": ["ベトナム", "Vietnam", "Viet Nam"],
    "PHL": ["フィリピン", "Philippines"],
    "MYS": ["マレーシア", "Malaysia"],
    "SGP": ["シンガポール", "Singapore"],
    "MMR": ["ミャンマー", "ビルマ", "Myanmar", "Burma"],
    "AUS": ["オーストラリア", "Australia", "豪州"],
    "NZL": ["ニュージーランド", "New Zealand"],
    "CAN": ["カナダ", "Canada"],
    "MEX": ["メキシコ", "Mexico"],
    "BRA": ["ブラジル", "Brazil"],
    "ARG": ["アルゼンチン", "Argentina"],
    "PER": ["ペルー", "Peru"],
    "CHL": ["チリ", "Chile"],
    "COL": ["コロンビア", "Colombia"],
    "VEN": ["ベネズエラ", "Venezuela"],
    "COD": ["コンゴ民主共和国", "DRC", "Democratic Republic of the Congo",
            "Democratic Republic of Congo", "コンゴ(民)", "民主コンゴ"],
    "COG": ["コンゴ共和国", "Republic of the Congo", "Congo-Brazzaville"],
    "NGA": ["ナイジェリア", "Nigeria"],
    "ETH": ["エチオピア", "Ethiopia"],
    "KEN": ["ケニア", "Kenya"],
    "UGA": ["ウガンダ", "Uganda"],
    "TZA": ["タンザニア", "Tanzania", "United Republic of Tanzania"],
    "ZAF": ["南アフリカ", "南ア", "South Africa"],
    "EGY": ["エジプト", "Egypt"],
    "GHA": ["ガーナ", "Ghana"],
    "SEN": ["セネガル", "Senegal"],
    "SDN": ["スーダン", "Sudan"],
    "SSD": ["南スーダン", "South Sudan"],
    "SOM": ["ソマリア", "Somalia"],
    "MOZ": ["モザンビーク", "Mozambique"],
    "MWI": ["マラウイ", "Malawi"],
    "ZMB": ["ザンビア", "Zambia"],
    "ZWE": ["ジンバブエ", "Zimbabwe"],
    "MDG": ["マダガスカル", "Madagascar"],
    "SAU": ["サウジアラビア", "Saudi Arabia"],
    "ARE": ["アラブ首長国連邦", "UAE", "United Arab Emirates"],
    "IRN": ["イラン", "Iran"],
    "IRQ": ["イラク", "Iraq"],
    "SYR": ["シリア", "Syria"],
    "YEM": ["イエメン", "Yemen"],
    "JOR": ["ヨルダン", "Jordan"],
    "ISR": ["イスラエル", "Israel"],
    "PSE": ["パレスチナ", "Palestine"],
    "LBN": ["レバノン", "Lebanon"],
    "NLD": ["オランダ", "Netherlands", "蘭"],
    "BEL": ["ベルギー", "Belgium"],
    "CHE": ["スイス", "Switzerland"],
    "AUT": ["オーストリア", "Austria"],
    "SWE": ["スウェーデン", "Sweden"],
    "NOR": ["ノルウェー", "Norway"],
    "DNK": ["デンマーク", "Denmark"],
    "FIN": ["フィンランド", "Finland"],
    "POL": ["ポーランド", "Poland"],
    "CZE": ["チェコ", "Czech Republic", "Czechia"],
    "HUN": ["ハンガリー", "Hungary"],
    "ROU": ["ルーマニア", "Romania"],
    "GRC": ["ギリシャ", "Greece"],
    "PRT": ["ポルトガル", "Portugal"],
    "IRL": ["アイルランド", "Ireland"],
    "KAZ": ["カザフスタン", "Kazakhstan"],
    "UZB": ["ウズベキスタン", "Uzbekistan"],
    "AFG": ["アフガニスタン", "Afghanistan"],
    "NPL": ["ネパール", "Nepal"],
    "LKA": ["スリランカ", "Sri Lanka"],
    "KHM": ["カンボジア", "Cambodia"],
    "LAO": ["ラオス", "Laos"],
    "MNG": ["モンゴル", "Mongolia"],
    "GIN": ["ギニア", "Guinea"],
    "SLE": ["シエラレオネ", "Sierra Leone"],
    "LBR": ["リベリア", "Liberia"],
    "CIV": ["コートジボワール", "Ivory Coast", "Côte d'Ivoire", "Cote d'Ivoire"],
    "CMR": ["カメルーン", "Cameroon"],
    "CAF": ["中央アフリカ共和国", "中央アフリカ", "Central African Republic"],
    "AGO": ["アンゴラ", "Angola"],
    "RWA": ["ルワンダ", "Rwanda"],
    "BDI": ["ブルンジ", "Burundi"],
    "HTI": ["ハイチ", "Haiti"],
    "ECU": ["エクアドル", "Ecuador"],
    "BOL": ["ボリビア", "Bolivia"],
    "CHL": ["チリ", "Chile"],
    "BGD": ["バングラデシュ", "Bangladesh"],
}


# ── Japan domestic place names → JPN ─────────────────────────────────────────

# 短縮形として JPN に紐付けない語句（方角・一般名詞・区名など）
_JPN_PLACE_BLOCKLIST: frozenset[str] = frozenset({
    # 1文字
    "津",
    # 方角（単独では一般語）
    "南", "北", "東", "西",
    # 一般名詞と衝突しやすい語
    "中央", "港", "緑", "花", "泉", "城", "宮", "野", "里",
    "山", "川", "田", "森", "原", "池", "江", "浦", "谷", "坂",
    "橋", "丘", "浜", "石", "金", "銀", "水", "松", "竹", "梅", "桜",
    # 区名（単独では地名扱いしない）
    "南区", "北区", "東区", "西区", "中央区", "港区", "緑区",
})

# Tier A: 都道府県・地方区分・政令指定都市略称（ハードコード）
_JPN_TIER_A: list[str] = [
    # ── 47 都道府県（正式名）
    "北海道",
    "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
    "岐阜県", "静岡県", "愛知県",
    "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
    "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県",
    "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
    # ── 都道府県（略称 = 都/道/府/県 なし）
    "青森", "岩手", "宮城", "秋田", "山形", "福島",
    "茨城", "栃木", "群馬", "埼玉", "千葉", "東京", "神奈川",
    "新潟", "富山", "石川", "福井", "山梨", "長野",
    "岐阜", "静岡", "愛知",
    "三重", "滋賀", "京都", "大阪", "兵庫", "奈良", "和歌山",
    "鳥取", "島根", "岡山", "広島", "山口",
    "徳島", "香川", "愛媛", "高知",
    "福岡", "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄",
    # ── 地方区分
    # 「中国地方」を登録し「中国」(2文字=CHN) よりも長い別名を優先させる
    "北海道地方",
    "東北地方",           # 「東北」単独は「東北アジア」と混同するため 地方 付きのみ
    "関東地方", "関東",
    "甲信越地方", "甲信越",
    "北陸地方", "北陸",
    "東海地方", "東海",
    "近畿地方", "近畿", "関西",
    "中国地方", "中四国地方", "中四国",  # CHN 誤検出ガード
    "四国地方", "四国",
    "九州地方", "九州",
    "南西諸島", "琉球",
    # ── 政令指定都市・主要都市（略称）
    "札幌", "仙台", "横浜", "川崎", "浜松", "名古屋", "神戸",
    "岡山", "広島", "福岡", "熊本",
    "函館", "旭川", "小樽", "釧路", "帯広", "網走", "稚内", "千歳",
    "盛岡", "石巻", "郡山", "会津若松",
    "水戸", "宇都宮", "高崎", "横須賀", "藤沢",
    "金沢", "長野", "松本",
    "宇治", "奈良", "和歌山",
    "鳥取", "松江", "倉敷", "福山", "下関",
    "高松", "松山", "高知",
    "久留米", "佐世保", "別府", "宮崎", "鹿児島", "那覇",
]


def _load_jpn_tier_b() -> list[str]:
    """Load municipality names from the bundled JSON data file."""
    try:
        data_file = Path(__file__).parents[1] / "data" / "japan_municipalities.json"
        names = json.loads(data_file.read_text(encoding="utf-8"))
        return names if isinstance(names, list) else []
    except Exception:
        return []


def _jpn_short_form(name: str) -> str | None:
    """Return the base name without 市/町/村/区 suffix if safe to use as a JPN alias."""
    for suffix in ("市", "町", "村", "区"):
        if name.endswith(suffix):
            base = name[: -len(suffix)]
            if len(base) >= 2 and base not in _JPN_PLACE_BLOCKLIST:
                return base
    return None


# ── Region keywords (broad geographic terms, not specific countries) ──────────

_REGION_KEYWORDS: list[tuple[str, str]] = sorted([
    ("アジア太平洋", "アジア太平洋"),
    ("Asia-Pacific", "アジア太平洋"),
    ("Asia Pacific", "アジア太平洋"),
    ("Latin America", "中南米"),
    ("Middle East", "中東"),
    ("Multiple countries", "複数国"),
    ("Multiple locations", "複数地域"),
    ("Multi-locations", "複数地域"),
    ("Multi-location", "複数地域"),
    ("Multi-country", "複数国"),
    ("Multi country", "複数国"),
    ("multiple countries", "複数国"),
    ("several countries", "複数国"),
    ("Multinational", "複数国"),
    ("International", "国際"),
    ("Worldwide", "世界"),
    ("Globally", "世界"),
    ("Global", "世界"),
    ("アフリカ", "アフリカ"),
    ("Africa", "アフリカ"),
    ("ヨーロッパ", "ヨーロッパ"),
    ("欧州", "ヨーロッパ"),
    ("Europe", "ヨーロッパ"),
    ("中南米", "中南米"),
    ("ラテンアメリカ", "中南米"),
    ("アジア", "アジア"),
    ("Asia", "アジア"),
    ("中東", "中東"),
    ("世界各地", "世界"),
    ("複数の国", "複数国"),
    ("複数国", "複数国"),
], key=lambda x: len(x[0]), reverse=True)


# ── Build inverted alias index ─────────────────────────────────────────────────

_alias_to_iso3: dict[str, str] = {}

# Seed from legacy dicts
for _name, _iso3 in {**_MANUAL, **_MANUAL_JA}.items():
    _alias_to_iso3[_name] = _iso3

# Override/extend with COUNTRY_ALIASES (higher priority for conflicts)
for _iso3, _aliases in COUNTRY_ALIASES.items():
    for _alias in _aliases:
        # Skip single CJK character aliases (too ambiguous for substring matching)
        if len(_alias) == 1 and any(0x3000 <= ord(c) <= 0x9FFF for c in _alias):
            continue
        _alias_to_iso3[_alias] = _iso3

# ── Japan place names (Tier A inline + Tier B from JSON) → JPN ───────────────
# Uses `if not in` to avoid overriding any explicitly registered foreign country.
# 「中国地方」(5 chars) is longer than 「中国」(2 chars=CHN), so longest-match-first
# ensures correct disambiguation when both appear in the alias list.
_jpn_all: list[str] = _JPN_TIER_A + _load_jpn_tier_b()
for _jp in _jpn_all:
    if _jp in _JPN_PLACE_BLOCKLIST:
        continue
    if _jp not in _alias_to_iso3:
        _alias_to_iso3[_jp] = "JPN"
    # Also register the short form (without 市/町/村/区) where unambiguous
    _sf = _jpn_short_form(_jp)
    if _sf and _sf not in _alias_to_iso3:
        _alias_to_iso3[_sf] = "JPN"

# Sort by alias length descending for longest-match-first disambiguation
_SORTED_ALIASES: list[tuple[str, str]] = sorted(
    _alias_to_iso3.items(),
    key=lambda x: len(x[0]),
    reverse=True,
)


# ── Core extraction helpers ────────────────────────────────────────────────────

def _is_cjk_alias(alias: str) -> bool:
    """Return True if the alias contains any Japanese/Chinese/Korean character."""
    return any(0x3000 <= ord(c) <= 0x9FFF for c in alias)


def _match_pos(text: str, alias: str) -> int:
    """Return the start position of alias in text, or -1 if not found."""
    if _is_cjk_alias(alias):
        return text.find(alias)
    # ASCII/Latin: require non-letter boundary on both sides to avoid false partial matches
    pattern = r"(?<![a-zA-Z])" + re.escape(alias) + r"(?![a-zA-Z])"
    m = re.search(pattern, text, re.IGNORECASE)
    return m.start() if m else -1


def extract_countries(text: str) -> list[str]:
    """Extract ISO3 codes for all countries mentioned in text, in order of appearance.

    Scans title + description/summary combined text. Uses longest-match-first to
    resolve ambiguous sub-strings (e.g. 'コンゴ民主共和国' before 'コンゴ').
    Matched spans are blanked to prevent shorter aliases from overlapping.
    """
    if not text.strip():
        return []

    working = text
    matches: list[tuple[int, str]] = []  # (position, iso3)
    seen_iso3: set[str] = set()

    for alias, iso3 in _SORTED_ALIASES:
        if iso3 in seen_iso3:
            continue
        pos = _match_pos(working, alias)
        if pos >= 0:
            matches.append((pos, iso3))
            seen_iso3.add(iso3)
            # Blank out the matched span so shorter sub-aliases cannot overlap
            working = working[:pos] + "\x00" * len(alias) + working[pos + len(alias):]

    matches.sort(key=lambda x: x[0])
    result = [iso3 for _, iso3 in matches]

    preview = text[:100].replace("\n", " ")
    if result:
        logger.debug("countries=%s from %r", result, preview)
    elif is_broad_scope(text):
        logger.info("broad scope detected (no specific countries) in %r", preview)
    else:
        logger.warning("no countries found in %r", preview)

    return result


def detect_region(text: str) -> str | None:
    """Return a broad region/situation label if text contains a geographic region keyword."""
    text_lower = text.lower()
    for kw, label in _REGION_KEYWORDS:
        if kw.lower() in text_lower:
            return label
    return None


def is_broad_scope(text: str) -> bool:
    """Return True if text contains a broad geographic or multi-country scope marker."""
    return detect_region(text) is not None


# ── Backward-compat wrappers ───────────────────────────────────────────────────

def name_to_iso3(name: str) -> str | None:
    """Convert a single country name string to ISO3. Returns None if unresolvable."""
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


# Clean English display names for countries whose pycountry name is verbose
_ISO3_EN_OVERRIDE: dict[str, str] = {
    "COD": "DR Congo",
    "PRK": "North Korea",
    "KOR": "South Korea",
    "IRN": "Iran",
    "SYR": "Syria",
    "VNM": "Vietnam",
    "BOL": "Bolivia",
    "TZA": "Tanzania",
    "LAO": "Laos",
    "MDA": "Moldova",
    "PSE": "Palestine",
    "TUR": "Turkey",
    "COG": "Republic of Congo",
    "CZE": "Czech Republic",
    "VEN": "Venezuela",
    "GBR": "United Kingdom",
    "USA": "United States",
    "ARE": "UAE",
    "FSM": "Micronesia",
    "SWZ": "Eswatini",
    "CAF": "Central African Republic",
    "TTO": "Trinidad and Tobago",
    "STP": "São Tomé and Príncipe",
    "BIH": "Bosnia and Herzegovina",
    "MKD": "North Macedonia",
    "SDN": "Sudan",
    "SSD": "South Sudan",
}


def get_country_name(iso3: str, lang: str = "ja") -> str:
    """Return the display name for iso3 in the given language ('ja' or 'en')."""
    if lang == "en":
        if iso3 in _ISO3_EN_OVERRIDE:
            return _ISO3_EN_OVERRIDE[iso3]
        country = pycountry.countries.get(alpha_3=iso3)
        return country.name if country else iso3
    return iso3_to_display_name(iso3)


def extract_countries_from_title_ja(title: str) -> list[str]:
    """Legacy wrapper: delegates to extract_countries."""
    return extract_countries(title)


def extract_countries_from_title(title: str) -> list[str]:
    """Legacy wrapper: delegates to extract_countries.

    Preserves WHO DON skip-list behaviour for broad multi-country markers.
    """
    _SKIP = {"multi-country", "multiple countries", "worldwide", "global", "several countries"}
    dash_parts = re.split(r"\s*[–—]\s*|\s+-\s+", title, maxsplit=1)
    if len(dash_parts) >= 2:
        country_part = dash_parts[1].strip().rstrip(".")
        if country_part.lower() in _SKIP:
            return []
    return extract_countries(title)
