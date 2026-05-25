"""新興感染症 世界モニタリングダッシュボード"""

import logging

import pandas as pd
import streamlit as st

from src import cache
from src.data.mock_articles import ARTICLES as _MOCK_ARTICLES
from src.fetchers import ecdc_cdtr, who_don
from src.parsers import country as country_parser
from src.parsers import disease_filter
from src.visualizers.choropleth import build

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="新興感染症モニタリング",
    page_icon="🦠",
    layout="wide",
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch_all() -> tuple[list[dict], list[dict], str]:
    """Fetch real data, apply disease filter + country extraction, persist to cache."""
    raw_who = who_don.fetch()
    filtered_who = disease_filter.filter_articles(raw_who)
    for article in filtered_who:
        article["iso3_list"] = country_parser.extract_countries_from_title(article["title"])

    raw_ecdc = ecdc_cdtr.fetch()

    ts = cache.save("who_don", filtered_who)
    cache.save("ecdc_cdtr", raw_ecdc)
    return filtered_who, raw_ecdc, ts


# ISO3 → 疾患名(日本語) のモックマッピング
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
    # PER(Oropouche) は対象疾患外のため除外
}


def _mock_fallback_articles() -> list[dict]:
    """Convert mock ARTICLES to the standard article format as a last-resort fallback."""
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


def _build_map_df(articles: list[dict], selected_diseases: list[str]) -> pd.DataFrame:
    """Expand articles to (iso3, disease) rows, then aggregate per country."""
    rows = [
        {"iso3": iso3, "disease": a["disease_ja"]}
        for a in articles
        if a.get("disease_ja") in selected_diseases
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
    agg["country"] = agg["iso3"].map(country_parser.iso3_to_display_name)
    return agg


# ── Session state bootstrap ───────────────────────────────────────────────────

if "articles_who" not in st.session_state:
    who_cached, who_ts = cache.load("who_don")
    ecdc_cached, _ = cache.load("ecdc_cdtr")
    if who_cached:
        st.session_state.articles_who = who_cached
        st.session_state.articles_ecdc = ecdc_cached
        st.session_state.last_updated = who_ts
        st.session_state._using_mock = False
    else:
        # キャッシュなし → 自動取得を試みる
        _placeholder = st.empty()
        with _placeholder.container():
            with st.spinner("初回データ取得中…"):
                try:
                    who_articles, ecdc_reports, ts = _fetch_all()
                    st.session_state.articles_who = who_articles
                    st.session_state.articles_ecdc = ecdc_reports
                    st.session_state.last_updated = ts
                    st.session_state._using_mock = False
                except Exception:
                    st.session_state.articles_who = _mock_fallback_articles()
                    st.session_state.articles_ecdc = []
                    st.session_state.last_updated = None
                    st.session_state._using_mock = True
        _placeholder.empty()

if "selected_iso3" not in st.session_state:
    st.session_state.selected_iso3 = None


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("🔬 疾患フィルタ")
    all_diseases = disease_filter.ALL_DISEASES_JA
    selected_diseases = st.multiselect(
        "表示する疾患を選択",
        options=all_diseases,
        default=all_diseases,
    )

    st.divider()
    st.header("📋 選択中の国")

    iso3 = st.session_state.selected_iso3
    if iso3 is None:
        st.info("地図上の国をクリックしてください")
    else:
        country_name = country_parser.iso3_to_display_name(iso3)
        st.subheader(country_name)

        country_articles = [
            a for a in st.session_state.articles_who
            if iso3 in a.get("iso3_list", [])
            and a.get("disease_ja") in selected_diseases
        ]

        if country_articles:
            st.markdown("**関連 WHO DON 記事**")
            for a in sorted(country_articles, key=lambda x: x.get("date", ""), reverse=True):
                st.markdown(
                    f'<a href="{a["url"]}" target="_blank">{a["title"]}</a>'
                    f'<br><small>{a.get("date", "日付不明")} — {a.get("disease_ja", "")}</small><br>',
                    unsafe_allow_html=True,
                )
        else:
            st.write("この国の記事データがありません（フィルタを確認してください）。")

        if st.button("選択を解除", use_container_width=True):
            st.session_state.selected_iso3 = None
            st.rerun()


# ── Main area ─────────────────────────────────────────────────────────────────

st.title("🦠 新興感染症 世界モニタリングダッシュボード")
st.caption("WHO / ECDC のアウトブレイク情報をリアルタイムで可視化します。")

if st.session_state.get("_using_mock"):
    st.warning("⚠️ サンプルデータ表示中 — 「データ取得」ボタンで実データに切り替えできます。")

col_btn, col_status = st.columns([1, 4])
with col_btn:
    fetch_clicked = st.button("🔄 データ取得", type="primary", use_container_width=True)
with col_status:
    if st.session_state.last_updated:
        st.info(f"最終更新: {st.session_state.last_updated}")
    else:
        st.warning("データ未取得 — 「データ取得」ボタンを押してください。")

if fetch_clicked:
    with st.spinner("WHO DON / ECDC CDTR からデータを取得中…"):
        try:
            who_articles, ecdc_reports, ts = _fetch_all()
            st.session_state.articles_who = who_articles
            st.session_state.articles_ecdc = ecdc_reports
            st.session_state.last_updated = ts
            st.session_state._using_mock = False
            st.success(
                f"取得完了 — WHO DON: {len(who_articles)} 件 / ECDC CDTR: {len(ecdc_reports)} 件"
            )
        except Exception as e:
            st.error(f"データ取得中にエラーが発生しました: {e}")
            # キャッシュフォールバック
            if not st.session_state.articles_who:
                cached_who, who_ts = cache.load("who_don")
                cached_ecdc, _ = cache.load("ecdc_cdtr")
                if cached_who:
                    st.session_state.articles_who = cached_who
                    st.session_state.articles_ecdc = cached_ecdc
                    st.session_state.last_updated = who_ts
                    st.warning(f"キャッシュデータを使用しています（更新: {who_ts}）")
                else:
                    # キャッシュもなければモックを使用
                    st.session_state.articles_who = _mock_fallback_articles()
                    st.session_state.articles_ecdc = []
                    st.session_state._using_mock = True
                    st.warning("実データ取得に失敗しました。サンプルデータを表示しています。")

# ── Map ───────────────────────────────────────────────────────────────────────

if st.session_state.articles_who:
    map_df = _build_map_df(st.session_state.articles_who, selected_diseases)

    st.subheader("世界アウトブレイクマップ")
    if map_df.empty:
        st.info("選択された疾患に該当する国データがありません。")
    else:
        selected = st.plotly_chart(build(map_df), use_container_width=True, on_select="rerun")
        if selected and selected.get("selection", {}).get("points"):
            clicked_iso3 = selected["selection"]["points"][0].get("location")
            if clicked_iso3 and clicked_iso3 != st.session_state.selected_iso3:
                st.session_state.selected_iso3 = clicked_iso3
                st.rerun()

    # Outbreak table
    st.divider()
    st.subheader("アウトブレイク一覧（WHO DON 記事ベース）")
    display_articles = [
        {
            "日付": a.get("date", ""),
            "疾患": a.get("disease_ja", ""),
            "国": ", ".join(
                country_parser.iso3_to_display_name(c) for c in a.get("iso3_list", [])
            ) or "複数国/不明",
            "タイトル": a.get("title", ""),
            "URL": a.get("url", ""),
        }
        for a in st.session_state.articles_who
        if a.get("disease_ja") in selected_diseases
    ]
    if display_articles:
        st.dataframe(
            pd.DataFrame(display_articles).sort_values("日付", ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={"URL": st.column_config.LinkColumn("リンク", display_text="開く")},
        )
    else:
        st.info("選択された疾患の記事がありません。")

    # ECDC reports
    if st.session_state.articles_ecdc:
        st.divider()
        st.subheader("最新 ECDC CDTR レポート")
        ecdc_rows = [
            {
                "発行日": r.get("date", ""),
                "タイトル": r.get("title", ""),
                "URL": r.get("url", ""),
            }
            for r in st.session_state.articles_ecdc
        ]
        st.dataframe(
            pd.DataFrame(ecdc_rows).sort_values("発行日", ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={"URL": st.column_config.LinkColumn("リンク", display_text="開く")},
        )

else:
    st.subheader("世界アウトブレイクマップ")
    st.info("「データ取得」ボタンを押すとマップが表示されます。")
