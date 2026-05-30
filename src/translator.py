"""Article title translation module using argos-translate (fully local)."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import argostranslate  # noqa: F401
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False

_CACHE_FILE = Path(__file__).parents[1] / "data" / "cache" / "translations.json"

# Whether models are confirmed ready this session
_models_ready: bool | None = None

# ── Disease name glossary ─────────────────────────────────────────────────────

# English canonical → Japanese canonical (sorted by key length desc)
_DISEASE_EN_JA: list[tuple[str, str]] = sorted([
    ("Crimean-Congo hemorrhagic fever", "クリミア・コンゴ出血熱"),
    ("Crimean-Congo", "クリミア・コンゴ出血熱"),
    ("Avian influenza", "鳥インフルエンザ"),
    ("Ebola virus disease", "エボラウイルス病"),
    ("Yellow fever", "黄熱"),
    ("Lassa fever", "ラッサ熱"),
    ("Dengue fever", "デング熱"),
    ("Hantavirus", "ハンタウイルス感染症"),
    ("Monkeypox", "エムポックス(サル痘)"),
    ("Chikungunya", "チクングニア熱"),
    ("MERS-CoV", "MERS-CoV"),     # keep as-is (established acronym)
    ("Marburg", "マールブルグ病"),
    ("H5N1", "H5N1"),             # pass-through: subtype code, not a word
    ("H7N9", "H7N9"),
    ("H9N2", "H9N2"),
    ("Measles", "麻疹"),
    ("Cholera", "コレラ"),
    ("Ebola", "エボラ出血熱"),
    ("Nipah", "ニパウイルス感染症"),
    ("MERS", "MERS(中東呼吸器症候群)"),
    ("Mpox", "エムポックス(サル痘)"),
    ("Dengue", "デング熱"),
    ("Zika", "ジカ熱"),
    ("Lassa", "ラッサ熱"),
], key=lambda x: len(x[0]), reverse=True)

# Japanese canonical → English canonical (sorted by key length desc)
_DISEASE_JA_EN: list[tuple[str, str]] = sorted([
    ("クリミア・コンゴ出血熱", "Crimean-Congo Hemorrhagic Fever"),
    ("H5N1型鳥インフルエンザ", "H5N1 Avian Influenza"),
    ("H7N9型鳥インフルエンザ", "H7N9 Avian Influenza"),
    ("H9N2型鳥インフルエンザ", "H9N2 Avian Influenza"),
    ("エムポックス(サル痘)", "Mpox (Monkeypox)"),
    ("サル痘 (Mpox)", "Mpox (Monkeypox)"),
    ("MERS(中東呼吸器症候群)", "MERS (Middle East Respiratory Syndrome)"),
    ("ハンタウイルス感染症", "Hantavirus Disease"),
    ("ニパウイルス感染症", "Nipah Virus Disease"),
    ("チクングニア熱", "Chikungunya Fever"),
    ("エボラ出血熱", "Ebola Hemorrhagic Fever"),
    ("マールブルグ病", "Marburg Disease"),
    ("鳥インフルエンザ", "Avian Influenza"),
    ("ラッサ熱", "Lassa Fever"),
    ("デング熱", "Dengue Fever"),
    ("MERS-CoV", "MERS-CoV"),
    ("コレラ", "Cholera"),
    ("黄熱", "Yellow Fever"),
    ("ジカ熱", "Zika Fever"),
    ("麻疹", "Measles"),
], key=lambda x: len(x[0]), reverse=True)

# Post-processing normalization for JA→EN output (normalize model's English output)
_EN_NORMALIZE: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bebola\b", re.IGNORECASE), "Ebola Hemorrhagic Fever"),
    (re.compile(r"\bmarburg\b", re.IGNORECASE), "Marburg Disease"),
    (re.compile(r"\bdengue\b", re.IGNORECASE), "Dengue Fever"),
    (re.compile(r"\bmeasles\b", re.IGNORECASE), "Measles"),
    (re.compile(r"\bcholera\b", re.IGNORECASE), "Cholera"),
    (re.compile(r"\bzika\b", re.IGNORECASE), "Zika Fever"),
    (re.compile(r"\bnipah\b", re.IGNORECASE), "Nipah Virus Disease"),
    (re.compile(r"\bhantavirus\b", re.IGNORECASE), "Hantavirus Disease"),
    (re.compile(r"\bchikungunya\b", re.IGNORECASE), "Chikungunya Fever"),
    (re.compile(r"\bmonkeypox\b", re.IGNORECASE), "Mpox (Monkeypox)"),
    (re.compile(r"\bmpox\b", re.IGNORECASE), "Mpox (Monkeypox)"),
    (re.compile(r"\byellow fever\b", re.IGNORECASE), "Yellow Fever"),
    (re.compile(r"\blassa\b", re.IGNORECASE), "Lassa Fever"),
    (re.compile(r"\bavian influenza\b", re.IGNORECASE), "Avian Influenza"),
    (re.compile(r"\b(h5n1|h7n9|h9n2)\b", re.IGNORECASE), lambda m: m.group(0).upper()),
    (re.compile(r"\bmers\b", re.IGNORECASE), "MERS"),
]


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _load_cache() -> dict[str, str]:
    try:
        if _CACHE_FILE.exists():
            return json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_cache(cache: dict[str, str]) -> None:
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        logger.warning("Failed to save translation cache: %s", e)


_mem_cache: dict[str, str] | None = None


def _get_cache() -> dict[str, str]:
    global _mem_cache
    if _mem_cache is None:
        _mem_cache = _load_cache()
    return _mem_cache


def _put_cache(key: str, value: str) -> None:
    cache = _get_cache()
    cache[key] = value
    _save_cache(cache)


# ── Language detection ────────────────────────────────────────────────────────

_JA_PATTERN = re.compile(r"[ぁ-んァ-ン一-龯]")


def detect_language(text: str) -> str:
    """Return 'ja' if text contains Japanese characters, else 'en'."""
    return "ja" if _JA_PATTERN.search(text) else "en"


# ── Translation helpers ───────────────────────────────────────────────────────

_PLACEHOLDER_BASE = "ZZDZ"  # Unlikely to appear in natural text


def _protect_en_terms(text: str) -> tuple[str, list[tuple[str, str]]]:
    """For EN→JA: replace EN disease keywords with placeholders before translation."""
    replacements: list[tuple[str, str]] = []
    working = text
    for en_term, ja_term in _DISEASE_EN_JA:
        pattern = r"(?<![a-zA-Z])" + re.escape(en_term) + r"(?![a-zA-Z])"
        if re.search(pattern, working, re.IGNORECASE):
            placeholder = f"{_PLACEHOLDER_BASE}{len(replacements)}"
            working = re.sub(pattern, placeholder, working, flags=re.IGNORECASE)
            replacements.append((placeholder, ja_term))
    return working, replacements


def _restore_terms(text: str, replacements: list[tuple[str, str]]) -> str:
    for placeholder, target_term in replacements:
        text = text.replace(placeholder, target_term)
    return text


def _normalize_en_disease_names(text: str) -> str:
    """For JA→EN: normalize disease name variants in the English output."""
    for pattern, replacement in _EN_NORMALIZE:
        if callable(replacement):
            text = pattern.sub(replacement, text)
        else:
            text = pattern.sub(replacement, text)
    return text


# ── Model management ──────────────────────────────────────────────────────────

def check_models_installed() -> bool:
    """Return True if both ja↔en translation models are installed."""
    if not TRANSLATION_AVAILABLE:
        return False
    try:
        from argostranslate import translate
        installed = translate.get_installed_languages()
        codes = {lang.code for lang in installed}
        if "ja" not in codes or "en" not in codes:
            return False
        ja_lang = next(l for l in installed if l.code == "ja")
        en_lang = next(l for l in installed if l.code == "en")
        return bool(ja_lang.get_translation(en_lang) and en_lang.get_translation(ja_lang))
    except Exception:
        return False


def ensure_models() -> bool:
    """Download and install ja↔en models if missing. Returns True if models ready."""
    global _models_ready
    if not TRANSLATION_AVAILABLE:
        _models_ready = False
        return False
    if _models_ready is True:
        return True
    if check_models_installed():
        _models_ready = True
        return True
    try:
        from argostranslate import package
        package.update_package_index()
        available = package.get_available_packages()
        needed = [
            p for p in available
            if (p.from_code == "ja" and p.to_code == "en")
            or (p.from_code == "en" and p.to_code == "ja")
        ]
        if not needed:
            logger.error("Required translation packages not found in index.")
            _models_ready = False
            return False
        for pkg in needed:
            path = pkg.download()
            package.install_from_path(path)
        _models_ready = check_models_installed()
        return bool(_models_ready)
    except Exception as e:
        logger.warning("Failed to install translation models: %s", e)
        _models_ready = False
        return False


# ── Public translation API ────────────────────────────────────────────────────

def translate(text: str, target_lang: str) -> str:
    """Translate text to target_lang ('ja' or 'en'). Returns original on failure."""
    global _models_ready
    if not TRANSLATION_AVAILABLE:
        return text
    if not text.strip():
        return text
    src_lang = detect_language(text)
    if src_lang == target_lang:
        return text

    cache_key = f"{text}|{target_lang}"
    cached = _get_cache().get(cache_key)
    if cached is not None:
        return cached

    if _models_ready is None:
        _models_ready = check_models_installed()
    if not _models_ready:
        return text

    try:
        import argostranslate.translate as at

        if target_lang == "ja":
            # EN→JA: protect disease terms with placeholders, then restore
            protected, replacements = _protect_en_terms(text)
            raw = at.translate(protected, src_lang, target_lang)
            result = _restore_terms(raw, replacements)
        else:
            # JA→EN: translate freely, then normalize disease name variants
            result = at.translate(text, src_lang, target_lang)
            result = _normalize_en_disease_names(result)

        _put_cache(cache_key, result)
        return result
    except Exception as e:
        logger.warning("Translation error for %r: %s", text[:60], e)
        return text
