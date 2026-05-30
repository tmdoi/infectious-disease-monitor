"""Bilingual UI label dictionary for Japanese/English toggle."""

from __future__ import annotations

_LABELS: dict[str, dict[str, str]] = {
    "ja": {
        # App header
        "app_title": "新興感染症 世界モニタリングダッシュボード",
        "app_subtitle": "WHO / ECDC / Yahoo Japan / 47NEWS / Google ニュース のアウトブレイク情報をリアルタイムで可視化します。",
        # Sidebar
        "disease_filter": "疾患フィルタ",
        "select_diseases": "表示する疾患を選択",
        "selected_country": "選択中の国",
        "source_list": "配信元一覧",
        "related_articles": "関連記事",
        "regional_news": "広域・地域不明ニュース",
        "no_country_selected": "地図上の国をクリックしてください",
        "no_articles": "この国の記事データがありません（フィルタを確認してください）。",
        "clear_selection": "選択を解除",
        # Main area
        "fetch_data": "🔄 データ取得",
        "last_updated": "最終更新",
        "data_not_fetched": "データ未取得 — 「データ取得」ボタンを押してください。",
        "using_sample": "⚠️ サンプルデータ表示中 — 「データ取得」ボタンで実データに切り替えできます。",
        "fetching": "WHO DON / ECDC CDTR / Yahoo Japan / 47NEWS / Google ニュース からデータを取得中…",
        "fetch_complete": "取得完了",
        # Map
        "map_title": "世界アウトブレイクマップ",
        "colorbar_title": "アウトブレイク数",
        "hover_count": "件数",
        "no_disease_data": "選択された疾患に該当する国データがありません。",
        # Article table
        "article_table": "アウトブレイク記事一覧",
        "no_articles_filtered": "選択された疾患の記事がありません。",
        "date_col": "日付",
        "source_col": "ソース",
        "disease_col": "疾患",
        "country_col": "国",
        "title_col": "タイトル",
        "link": "リンク",
        "open": "開く",
        # ECDC table
        "ecdc_reports": "最新 ECDC CDTR レポート",
        "pub_date_col": "発行日",
        # Misc
        "date_unknown": "日付不明",
        "region_unknown": "地域不明",
        "multi_country": "複数国",
        "country_extraction": "国判定",
        "success": "成功",
        "broad": "広域",
        "unknown": "不明",
        # Language toggle
        "lang_label": "言語 / Language",
        # Translation
        "translation_preparing": "翻訳モデルを準備中...",
        "translation_unavailable": "⚠️ 翻訳モデルが利用できません。初回のみネット接続が必要です。",
    },
    "en": {
        # App header
        "app_title": "Emerging Infectious Disease Global Monitoring Dashboard",
        "app_subtitle": "Real-time visualization of outbreak information from WHO / ECDC / Yahoo Japan / 47NEWS / Google News.",
        # Sidebar
        "disease_filter": "Disease Filter",
        "select_diseases": "Select diseases to display",
        "selected_country": "Selected Country",
        "source_list": "Sources",
        "related_articles": "Related Articles",
        "regional_news": "Regional / Unspecified News",
        "no_country_selected": "Click a country on the map",
        "no_articles": "No articles for this country (check filters).",
        "clear_selection": "Clear Selection",
        # Main area
        "fetch_data": "🔄 Fetch Data",
        "last_updated": "Last updated",
        "data_not_fetched": "No data yet — click \"Fetch Data\".",
        "using_sample": "⚠️ Showing sample data — click \"Fetch Data\" to load real data.",
        "fetching": "Fetching from WHO DON / ECDC CDTR / Yahoo Japan / 47NEWS / Google News…",
        "fetch_complete": "Fetch complete",
        # Map
        "map_title": "Global Outbreak Map",
        "colorbar_title": "Number of Outbreaks",
        "hover_count": "Count",
        "no_disease_data": "No country data for the selected diseases.",
        # Article table
        "article_table": "Outbreak Article List",
        "no_articles_filtered": "No articles for the selected diseases.",
        "date_col": "Date",
        "source_col": "Source",
        "disease_col": "Disease",
        "country_col": "Country",
        "title_col": "Title",
        "link": "Link",
        "open": "Open",
        # ECDC table
        "ecdc_reports": "Latest ECDC CDTR Reports",
        "pub_date_col": "Published",
        # Misc
        "date_unknown": "Unknown date",
        "region_unknown": "Region unknown",
        "multi_country": "Multi-country",
        "country_extraction": "Country detection",
        "success": "success",
        "broad": "broad",
        "unknown": "unknown",
        # Language toggle
        "lang_label": "言語 / Language",
        # Translation
        "translation_preparing": "Preparing translation models...",
        "translation_unavailable": "⚠️ Translation models unavailable. Internet required on first run.",
    },
}


def t(key: str, lang: str = "ja") -> str:
    """Return UI label for key in the given language, falling back to Japanese."""
    return _LABELS.get(lang, _LABELS["ja"]).get(key, _LABELS["ja"].get(key, key))
