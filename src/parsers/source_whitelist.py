"""Whitelist of trusted news sources for Google News RSS filtering."""

from __future__ import annotations

import re
from urllib.parse import urlparse

TRUSTED_SOURCES: dict[str, str] = {
    # 公共放送
    "nhk.or.jp": "NHK",
    "nhk.jp": "NHK",
    "www3.nhk.or.jp": "NHK",
    # 全国紙
    "asahi.com": "朝日新聞",
    "mainichi.jp": "毎日新聞",
    "yomiuri.co.jp": "読売新聞",
    "nikkei.com": "日経新聞",
    "sankei.com": "産経新聞",
    "tokyo-np.co.jp": "東京新聞",
    "chunichi.co.jp": "中日新聞",
    # 通信社
    "kyodo.co.jp": "共同通信",
    "kyodonews.net": "共同通信",
    "nordot.app": "共同通信(ノアドット)",
    "this.kiji.is": "共同通信(旧)",
    "jiji.com": "時事通信",
    "47news.jp": "47NEWS",
    # 経済・全国メディア
    "bloomberg.co.jp": "Bloomberg Japan",
    "reuters.com": "Reuters",
    "jp.reuters.com": "Reuters Japan",
    "afpbb.com": "AFP通信",
    "cnn.co.jp": "CNN日本版",
    "bbc.com": "BBC",
    # 公的機関(国)
    "mhlw.go.jp": "厚生労働省",
    "niid.go.jp": "国立感染症研究所",
    "cao.go.jp": "内閣府",
    "kantei.go.jp": "首相官邸",
    "mofa.go.jp": "外務省",
    "maff.go.jp": "農林水産省",
    "env.go.jp": "環境省",
    # 公的機関(国際)
    "who.int": "WHO",
    "ecdc.europa.eu": "ECDC",
    "cdc.gov": "CDC(米国)",
    "ema.europa.eu": "EMA(欧州医薬品庁)",
    "pmda.go.jp": "PMDA",
    # アカデミア・研究機関
    "u-tokyo.ac.jp": "東京大学",
    "kyoto-u.ac.jp": "京都大学",
    "osaka-u.ac.jp": "大阪大学",
    "tohoku.ac.jp": "東北大学",
    "nagoya-u.ac.jp": "名古屋大学",
    "kyushu-u.ac.jp": "九州大学",
    "hokudai.ac.jp": "北海道大学",
    "amed.go.jp": "AMED(日本医療研究開発機構)",
    "riken.jp": "理化学研究所",
    # 学会
    "kansensho.or.jp": "日本感染症学会",
    "kankyokansen.org": "日本環境感染学会",
    "jsv.umin.jp": "日本ウイルス学会",
}

# *.lg.jp にマッチさせるための正規表現パターン
_LG_JP = re.compile(r"^.+\.lg\.jp$")
# *.pref.??.jp
_PREF_JP = re.compile(r"^.+\.pref\.[a-z]+\.jp$")
# *.metro.tokyo.lg.jp
_TOKYO_METRO = re.compile(r"^.+\.metro\.tokyo\.lg\.jp$")
# *.city.***.jp (政令市等)
_CITY_JP = re.compile(r"^.+\.city\..+\.jp$")


def extract_domain(url: str) -> str | None:
    """Extract the hostname (lowercase, no port) from a URL."""
    try:
        host = urlparse(url).hostname
        return host if host else None
    except Exception:
        return None


def get_trusted_label(url: str) -> str | None:
    """Return a publisher label if the URL's domain is a trusted source, else None."""
    domain = extract_domain(url)
    if not domain:
        return None

    # Exact match in whitelist
    if domain in TRUSTED_SOURCES:
        return TRUSTED_SOURCES[domain]

    # Subdomain of a whitelisted domain (e.g. www.reuters.com → reuters.com)
    for key, label in TRUSTED_SOURCES.items():
        if domain.endswith("." + key):
            return label

    # Dynamic patterns: 自治体 (*.lg.jp / *.pref.*.jp / *.city.*.jp etc.)
    if (
        _LG_JP.match(domain)
        or _PREF_JP.match(domain)
        or _TOKYO_METRO.match(domain)
        or _CITY_JP.match(domain)
    ):
        return "自治体"

    # アカデミア (*.ac.jp / *.edu)
    if domain.endswith(".ac.jp") or domain.endswith(".edu"):
        return "大学"

    return None
