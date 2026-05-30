"""新興感染症 世界モニタリングダッシュボード"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import streamlit as st

from src import cache, translator
from src.data.glossary import (
    ALL_DISEASE_IDS,
    disease_display_name,
    disease_ja_to_display,
    ja_name_from_id,
)
from src.data.mock_articles import ARTICLES as _MOCK_ARTICLES
from src.data.ui_labels import t
from src.fetchers import ecdc_cdtr, google_news, news_47, who_don, yahoo_topics
from src.parsers import country as country_parser
from src.parsers import disease_filter
from src.parsers.source_whitelist import localize_label
from src.visualizers.choropleth import build

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="新興感染症モニタリング",
    page_icon="🦠",
    layout="wide",
)

_SOURCE_LABEL_JA: dict[str, str] = {
    "WHO DON": "🌐 WHO",
    "ECDC CDTR": "🇪🇺 ECDC",
    "Yahoo Japan": "📰 Yahoo",
    "47NEWS": "🗞 47NEWS",
    "Google ニュース": "🔍 Google",
    "WHO DON (サンプルデータ)": "🧪 サンプル",
}
_SOURCE_LABEL_EN: dict[str, str] = {
    "WHO DON": "🌐 WHO",
    "ECDC CDTR": "🇪🇺 ECDC",
    "Yahoo Japan": "📰 Yahoo",
    "47NEWS": "🗞 47NEWS",
    "Google ニュース": "🔍 Google News",
    "WHO DON (サンプルデータ)": "🧪 Sample",
}


def _source_label(source: str, lang: str) -> str:
    """Return the display label for a source key in the given language."""
    tbl = _SOURCE_LABEL_EN if lang == "en" else _SOURCE_LABEL_JA
    return tbl.get(source, source)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch_with_fallback(name: str, fn) -> tuple[list[dict], str | None]:
    """Run fetch fn; on failure load cache. Returns (records, warning_msg | None)."""
    try:
        records = fn()
        cache.save(name, records)
        return records, None
    except Exception as e:
        msg = f"{name} 取得失敗: {e}"
        logging.warning(msg)
        cached, _ = cache.load(name)
        if cached:
            return cached, f"{msg}（キャッシュを使用）"
        return [], msg


def _enrich(a: dict) -> dict:
    """Add iso3_list (and region for no-match) to an article dict in-place."""
    text = (a.get("title", "") + " " + a.get("summary", "")).strip()
    a["iso3_list"] = country_parser.extract_countries(text)
    if not a["iso3_list"]:
        a["region"] = country_parser.detect_region(text)
    return a


def _extraction_stats(articles: list[dict]) -> dict[str, int]:
    total = len(articles)
    success = sum(1 for a in articles if a.get("iso3_list"))
    broad = sum(1 for a in articles if not a.get("iso3_list") and a.get("region"))
    return {"total": total, "success": success, "broad": broad,
            "unknown": total - success - broad}


def _fetch_all() -> tuple[list[dict], list[dict], list[dict], str, list[str]]:
    """Fetch all sources in parallel, apply filters. Returns (who, ecdc, ja_combined, ts, warnings)."""
    warnings: list[str] = []

    def _fetch_who():
        raw = who_don.fetch()
        filtered = disease_filter.filter_articles(raw)
        for a in filtered:
            _enrich(a)
        return filtered

    def _fetch_yahoo():
        raw = yahoo_topics.fetch()
        filtered = disease_filter.filter_yahoo_articles(raw)
        for a in filtered:
            _enrich(a)
        return filtered

    def _fetch_47():
        raw = news_47.fetch()
        filtered = disease_filter.filter_yahoo_articles(raw)
        for a in filtered:
            _enrich(a)
        return filtered

    def _fetch_google():
        raw = google_news.fetch()
        filtered = disease_filter.filter_yahoo_articles(raw)
        for a in filtered:
            _enrich(a)
        return filtered

    tasks = {
        "who_don": _fetch_who,
        "ecdc_cdtr": ecdc_cdtr.fetch,
        "yahoo_topics": _fetch_yahoo,
        "news_47": _fetch_47,
        "google_news": _fetch_google,
    }

    results: dict[str, list[dict]] = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_fetch_with_fallback, name, fn): name for name, fn in tasks.items()}
        for future in as_completed(futures):
            name = futures[future]
            records, warn = future.result()
            results[name] = records
            if warn:
                warnings.append(warn)

    who_articles = results["who_don"]
    ecdc_reports = results["ecdc_cdtr"]
    ja_combined = results["yahoo_topics"] + results["news_47"] + results["google_news"]

    ts = cache.save("who_don", who_articles)
    cache.save("ecdc_cdtr", ecdc_reports)

    return who_articles, ecdc_reports, ja_combined, ts, warnings


_MOCK_DISEASE_MAP: dict[str, str] = {
    "COD": "エボラ出血熱",
    "NGA": "ラッサ熱",
    "CHN": "H5N1型鳥インフルエンザ",
    "BRA": "デング熱",
    "IND": "ニパウイルス感染症",
    "SAU": "MERS-CoV",
    "SSD": "コレラ",
    "BGD": "デング熱",
    "UGA": "マールブルグ病",
}


def _mock_fallback_articles() -> list[dict]:
    """Convert mock ARTICLES to the standard format as a last-resort fallback."""
    result = []
    for iso3, articles in _MOCK_ARTICLES.items():
        disease_ja = _MOCK_DISEASE_MAP.get(iso3)
        if not disease_ja:
            continue
        for a in articles:
            result.append({
                "title": a["title"],
                "url": a["url"],
                "date": a["date"],
                "source": "WHO DON (サンプルデータ)",
                "disease_ja": disease_ja,
                "iso3_list": [iso3],
            })
    return result


def _build_map_df(
    articles: list[dict],
    selected_ja_names: set[str],
    lang: str = "ja",
) -> pd.DataFrame:
    """Aggregate articles to a map-ready DataFrame per ISO3, with lang-aware labels."""
    rows = [
        {"iso3": iso3, "disease": a["disease_ja"]}
        for a in articles
        if a.get("disease_ja") in selected_ja_names
        for iso3 in a.get("iso3_list", [])
    ]
    if not rows:
        return pd.DataFrame(columns=["iso3", "country", "disease", "count"])
    df = pd.DataFrame(rows)
    agg = (
        df.groupby("iso3")
        .agg(
            count=("disease", "count"),
            disease=("disease", lambda x: x.value_counts().index[0]),
        )
        .reset_index()
    )
    agg["country"] = agg["iso3"].map(lambda c: country_parser.get_country_name(c, lang))
    agg["disease"] = agg["disease"].map(lambda ja: disease_ja_to_display(ja, lang))
    return agg


def _tr(title: str, lang: str) -> str:
    """Translate article title if translation is ready, else return original."""
    if not st.session_state.get("translation_ready"):
        return title
    return translator.translate(title, lang)


def _country_cell(a: dict, lang: str) -> str:
    """Return display string for a country cell in the article table."""
    iso3s = a.get("iso3_list", [])
    if iso3s:
        return ", ".join(country_parser.get_country_name(c, lang) for c in iso3s)
    region = a.get("region")
    return f"[{region}]" if region else t("region_unknown", lang)


# ── Session state: language ───────────────────────────────────────────────────

if "lang" not in st.session_state:
    st.session_state["lang"] = "ja"

# ── Session state: translation models ────────────────────────────────────────

if "translation_ready" not in st.session_state:
    if translator.check_models_installed():
        translator._models_ready = True
        st.session_state["translation_ready"] = True
    else:
        with st.spinner(t("translation_preparing", st.session_state["lang"])):
            ok = translator.ensure_models()
        st.session_state["translation_ready"] = ok
        if not ok:
            st.warning(t("translation_unavailable", st.session_state["lang"]))

# ── Session state: articles ───────────────────────────────────────────────────

if "articles_who" not in st.session_state:
    who_cached, who_ts = cache.load("who_don")
    ecdc_cached, _ = cache.load("ecdc_cdtr")
    yahoo_cached, _ = cache.load("yahoo_topics")
    n47_cached, _ = cache.load("news_47")
    gnews_cached, _ = cache.load("google_news")
    if who_cached:
        st.session_state.articles_who = who_cached
        st.session_state.articles_ecdc = ecdc_cached
        st.session_state.articles_ja = (yahoo_cached or []) + (n47_cached or []) + (gnews_cached or [])
        st.session_state.last_updated = who_ts
        st.session_state._using_mock = False
        st.session_state.fetch_warnings = []
    else:
        _placeholder = st.empty()
        with _placeholder.container():
            with st.spinner("初回データ取得中…"):
                try:
                    who_a, ecdc_r, ja_a, ts, warns = _fetch_all()
                    st.session_state.articles_who = who_a
                    st.session_state.articles_ecdc = ecdc_r
                    st.session_state.articles_ja = ja_a
                    st.session_state.last_updated = ts
                    st.session_state._using_mock = False
                    st.session_state.fetch_warnings = warns
                except Exception:
                    st.session_state.articles_who = _mock_fallback_articles()
                    st.session_state.articles_ecdc = []
                    st.session_state.articles_ja = []
                    st.session_state.last_updated = None
                    st.session_state._using_mock = True
                    st.session_state.fetch_warnings = []
        _placeholder.empty()

if "selected_iso3" not in st.session_state:
    st.session_state.selected_iso3 = None

if "disease_ids_selection" not in st.session_state:
    st.session_state.disease_ids_selection = ALL_DISEASE_IDS.copy()


# ── Sidebar ───────────────────────────────────────────────────────────────────

lang = st.session_state["lang"]

with st.sidebar:
    st.header(f"🔬 {t('disease_filter', lang)}")

    # Multiselect uses internal IDs so selection survives language switches.
    # format_func converts each ID to the language-appropriate display name.
    # Note: no key= here; format_func with key= doesn't update chips on re-render.
    # Selection is manually persisted via st.session_state.disease_ids_selection.
    selected_disease_ids: list[str] = st.multiselect(
        t("select_diseases", lang),
        options=ALL_DISEASE_IDS,
        default=st.session_state.disease_ids_selection,
        format_func=lambda did: disease_display_name(did, lang),
    )
    st.session_state.disease_ids_selection = selected_disease_ids
    # Convert IDs to Japanese names for filtering articles (internal data uses ja names)
    selected_ja_names: set[str] = {ja_name_from_id(did) for did in selected_disease_ids}

    st.divider()

    # 配信元一覧
    all_articles_sidebar = (
        st.session_state.get("articles_who", []) + st.session_state.get("articles_ja", [])
    )
    if all_articles_sidebar:
        from collections import Counter

        def _display_label(a: dict, _lang: str) -> str:
            pub = a.get("publisher")
            if pub:
                return localize_label(pub, _lang)
            src = a.get("source", "")
            return _source_label(src, _lang)

        counts = Counter(_display_label(a, lang) for a in all_articles_sidebar)
        total = len(all_articles_sidebar)
        st.header(f"📡 {t('source_list', lang)}")
        caption = f"{'全' if lang == 'ja' else 'Total'} {total} {'件' if lang == 'ja' else 'articles'}"
        st.caption(caption)
        for label, n in counts.most_common():
            st.markdown(f"- {label}: **{n}**")
        st.divider()

    st.header(f"📋 {t('selected_country', lang)}")

    iso3 = st.session_state.selected_iso3
    if iso3 is None:
        st.info(t("no_country_selected", lang))
    else:
        country_name = country_parser.get_country_name(iso3, lang)
        st.subheader(country_name)

        all_articles = st.session_state.articles_who + st.session_state.articles_ja
        country_articles = [
            a for a in all_articles
            if iso3 in a.get("iso3_list", [])
            and a.get("disease_ja") in selected_ja_names
        ]

        if country_articles:
            st.markdown(f"**{t('related_articles', lang)}**")
            for a in sorted(country_articles, key=lambda x: x.get("date", ""), reverse=True):
                label = _display_label(a, lang)
                countries = a.get("iso3_list", [])
                multi_tag = ""
                if len(countries) > 1:
                    names = ", ".join(country_parser.get_country_name(c, lang) for c in countries)
                    multi_tag = f" [{t('multi_country', lang)}: {names}]"
                title_display = _tr(a["title"], lang)
                st.markdown(
                    f'<a href="{a["url"]}" target="_blank">{title_display}</a>'
                    f'<br><small>{a.get("date", t("date_unknown", lang))} {label}{multi_tag}'
                    f' — {disease_ja_to_display(a.get("disease_ja", ""), lang)}</small><br>',
                    unsafe_allow_html=True,
                )
        else:
            st.write(t("no_articles", lang))

        if st.button(t("clear_selection", lang), use_container_width=True):
            st.session_state.selected_iso3 = None
            st.rerun()

    # 広域・地域不明ニュース
    st.divider()
    _all_for_broad = (
        st.session_state.get("articles_who", []) + st.session_state.get("articles_ja", [])
    )
    _broad_articles = [
        a for a in _all_for_broad
        if not a.get("iso3_list") and a.get("disease_ja") in selected_ja_names
    ]
    if _broad_articles:
        count_suffix = f"({len(_broad_articles)}{'件' if lang == 'ja' else ''})"
        st.header(f"🌍 {t('regional_news', lang)} {count_suffix}")
        for a in sorted(_broad_articles, key=lambda x: x.get("date", ""), reverse=True):
            label = _display_label(a, lang)
            region = a.get("region")
            region_tag = f" [{region}]" if region else f" [{t('region_unknown', lang)}]"
            title_display = _tr(a["title"], lang)
            st.markdown(
                f'<a href="{a["url"]}" target="_blank">{title_display}</a>'
                f'<br><small>{a.get("date", t("date_unknown", lang))} {label}{region_tag}'
                f' — {disease_ja_to_display(a.get("disease_ja", ""), lang)}</small><br>',
                unsafe_allow_html=True,
            )


# ── Main area ─────────────────────────────────────────────────────────────────

st.title(f"🦠 {t('app_title', lang)}")
st.caption(t("app_subtitle", lang))

if st.session_state.get("_using_mock"):
    st.warning(t("using_sample", lang))

for w in st.session_state.get("fetch_warnings", []):
    st.warning(f"⚠️ {w}")

col_btn, col_status, col_lang = st.columns([1, 3, 1])
with col_btn:
    fetch_clicked = st.button(t("fetch_data", lang), type="primary", use_container_width=True)
with col_status:
    if st.session_state.last_updated:
        st.info(f"{t('last_updated', lang)}: {st.session_state.last_updated}")
    else:
        st.warning(t("data_not_fetched", lang))
with col_lang:
    new_lang = st.radio(
        t("lang_label", lang),
        options=["ja", "en"],
        format_func=lambda x: "🇯🇵 日本語" if x == "ja" else "🇬🇧 English",
        index=0 if lang == "ja" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    if new_lang != lang:
        st.session_state["lang"] = new_lang
        st.rerun()

_stats = st.session_state.get("extraction_stats")
if _stats and _stats["total"] > 0:
    st.caption(
        f"{t('country_extraction', lang)}: {_stats['total']} {'件中' if lang == 'ja' else 'articles —'} "
        f"{t('success', lang)} {_stats['success']} {'件' if lang == 'ja' else ''} / "
        f"{t('broad', lang)} {_stats['broad']} {'件' if lang == 'ja' else ''} / "
        f"{t('unknown', lang)} {_stats['unknown']} {'件' if lang == 'ja' else ''}"
    )

if fetch_clicked:
    with st.spinner(t("fetching", lang)):
        try:
            who_a, ecdc_r, ja_a, ts, warns = _fetch_all()
            st.session_state.articles_who = who_a
            st.session_state.articles_ecdc = ecdc_r
            st.session_state.articles_ja = ja_a
            st.session_state.last_updated = ts
            st.session_state._using_mock = False
            st.session_state.fetch_warnings = warns
            st.session_state.extraction_stats = _extraction_stats(who_a + ja_a)
            yahoo_count = sum(1 for a in ja_a if a.get("source") == "Yahoo Japan")
            n47_count = sum(1 for a in ja_a if a.get("source") == "47NEWS")
            gnews_count = sum(1 for a in ja_a if a.get("source") == "Google ニュース")
            st.success(
                f"{t('fetch_complete', lang)} — WHO DON: {len(who_a)} / "
                f"ECDC CDTR: {len(ecdc_r)} / "
                f"Yahoo: {yahoo_count} / "
                f"47NEWS: {n47_count} / "
                f"Google: {gnews_count}"
            )
            for w in warns:
                st.warning(f"⚠️ {w}")
        except Exception as e:
            err_label = "データ取得中にエラーが発生しました" if lang == "ja" else "Data fetch error"
            st.error(f"{err_label}: {e}")
            if not st.session_state.articles_who:
                cached_who, who_ts = cache.load("who_don")
                cached_ecdc, _ = cache.load("ecdc_cdtr")
                cached_yahoo, _ = cache.load("yahoo_topics")
                cached_47, _ = cache.load("news_47")
                cached_gnews, _ = cache.load("google_news")
                if cached_who:
                    st.session_state.articles_who = cached_who
                    st.session_state.articles_ecdc = cached_ecdc
                    st.session_state.articles_ja = (
                        (cached_yahoo or []) + (cached_47 or []) + (cached_gnews or [])
                    )
                    st.session_state.last_updated = who_ts
                    cache_msg = (
                        f"キャッシュデータを使用しています（更新: {who_ts}）"
                        if lang == "ja"
                        else f"Using cached data (updated: {who_ts})"
                    )
                    st.warning(cache_msg)
                else:
                    st.session_state.articles_who = _mock_fallback_articles()
                    st.session_state.articles_ecdc = []
                    st.session_state.articles_ja = []
                    st.session_state._using_mock = True
                    fallback_msg = (
                        "実データ取得に失敗しました。サンプルデータを表示しています。"
                        if lang == "ja"
                        else "Failed to fetch real data. Showing sample data."
                    )
                    st.warning(fallback_msg)

# ── Map ───────────────────────────────────────────────────────────────────────

_ja_with_country = [a for a in st.session_state.articles_ja if a.get("iso3_list")]
_all_map_articles = st.session_state.articles_who + _ja_with_country

if _all_map_articles or st.session_state.articles_who:
    map_df = _build_map_df(_all_map_articles, selected_ja_names, lang)

    st.subheader(t("map_title", lang))
    if map_df.empty:
        st.info(t("no_disease_data", lang))
    else:
        selected = st.plotly_chart(build(map_df, lang), use_container_width=True, on_select="rerun")
        if selected and selected.get("selection", {}).get("points"):
            clicked_iso3 = selected["selection"]["points"][0].get("location")
            if clicked_iso3 and clicked_iso3 != st.session_state.selected_iso3:
                st.session_state.selected_iso3 = clicked_iso3
                st.rerun()

    # ── Article table ─────────────────────────────────────────────────────────
    st.divider()
    st.subheader(t("article_table", lang))
    all_articles_for_table = st.session_state.articles_who + st.session_state.articles_ja

    display_articles = [
        {
            t("date_col", lang): a.get("date", ""),
            t("source_col", lang): _display_label(a, lang),
            t("disease_col", lang): disease_ja_to_display(a.get("disease_ja", ""), lang),
            t("country_col", lang): _country_cell(a, lang),
            t("title_col", lang): _tr(a.get("title", ""), lang),
            "URL": a.get("url", ""),
        }
        for a in all_articles_for_table
        if a.get("disease_ja") in selected_ja_names
    ]
    if display_articles:
        st.dataframe(
            pd.DataFrame(display_articles).sort_values(t("date_col", lang), ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={"URL": st.column_config.LinkColumn(t("link", lang), display_text=t("open", lang))},
        )
    else:
        st.info(t("no_articles_filtered", lang))

    # ── ECDC reports ──────────────────────────────────────────────────────────
    if st.session_state.articles_ecdc:
        st.divider()
        st.subheader(t("ecdc_reports", lang))
        ecdc_rows = [
            {
                t("pub_date_col", lang): r.get("date", ""),
                t("title_col", lang): r.get("title", ""),
                "URL": r.get("url", ""),
            }
            for r in st.session_state.articles_ecdc
        ]
        st.dataframe(
            pd.DataFrame(ecdc_rows).sort_values(t("pub_date_col", lang), ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={"URL": st.column_config.LinkColumn(t("link", lang), display_text=t("open", lang))},
        )

else:
    st.subheader(t("map_title", lang))
    no_data_msg = (
        f"「{t('fetch_data', lang)}」ボタンを押すとマップが表示されます。"
        if lang == "ja"
        else f"Click \"{t('fetch_data', lang)}\" to display the map."
    )
    st.info(no_data_msg)
