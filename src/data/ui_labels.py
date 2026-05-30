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
        "translation_disabled_note": "※ この環境では記事タイトルの自動翻訳は無効です(UI表示の言語切替は利用できます)",
        # About / How to Use
        "about_header": "ℹ️ About",
        "about_body": """\
**新興感染症 世界モニタリングダッシュボード**は、WHO・ECDCおよび主要報道機関の感染症アウトブレイク情報を世界地図上にリアルタイム集約・可視化するツールです。

**データソース**
- 🌐 WHO Disease Outbreak News (DON)
- 🇪🇺 ECDC 週次感染症脅威レポート (CDTR)
- 📰 Yahoo Japan / 🗞 47NEWS / 🔍 Google ニュース
- 公共放送・全国紙・通信社・公的機関のみ配信

**対象疾患** (18疾患)
エボラ出血熱、マールブルグ病、鳥インフルエンザ、MERS-CoV、ラッサ熱、デング熱、ジカ熱、ハンタウイルス、ニパウイルス、エムポックス、コレラ、黄熱、チクングニア熱、クリミア・コンゴ出血熱、麻疹 など

**免責事項**
- 本ツールは情報集約が目的であり、医学的・公衆衛生上の判断の根拠とすべきではありません
- 各記事の著作権は配信元に帰属します。タイトルとリンクのみ表示しています
- データの正確性・完全性は保証されません

**ライセンス:** MIT
""",
        "howto_header": "📖 使い方",
        "howto_body": """\
1. **「🔄 データ取得」**ボタンを押して最新情報を取得します
2. **地図上の色付きの国をクリック**すると、その国の関連記事がサイドバーに表示されます
   - 色が濃いほどアウトブレイク件数が多い国です
3. **記事タイトルをクリック**すると新しいタブで元記事が開きます
4. **「疾患フィルタ」**で表示する感染症を絞り込めます
5. **言語トグル(🇯🇵 日本語 / 🇬🇧 English)**で表示言語を切り替えます。記事タイトルも自動翻訳されます
6. **「広域・地域不明ニュース」**セクションには、特定の国に紐付けられなかった記事が表示されます

> 地図右のカラーバーがアウトブレイク件数のスケールを示します。
""",
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
        "translation_disabled_note": "Note: Automatic article title translation is disabled in this environment (UI language switching is still available).",
        # About / How to Use
        "about_header": "ℹ️ About",
        "about_body": """\
**Emerging Infectious Disease Global Monitoring Dashboard** aggregates and visualizes outbreak information from WHO, ECDC, and major news outlets on an interactive world map in real time.

**Data Sources**
- 🌐 WHO Disease Outbreak News (DON)
- 🇪🇺 ECDC Weekly Communicable Disease Threats Report (CDTR)
- 📰 Yahoo Japan / 🗞 47NEWS / 🔍 Google News
- Trusted sources only: public broadcasters, national newspapers, wire services, government bodies

**Diseases Monitored** (18 diseases)
Ebola, Marburg, Avian Influenza, MERS-CoV, Lassa Fever, Dengue, Zika, Hantavirus, Nipah, Mpox, Cholera, Yellow Fever, Chikungunya, Crimean-Congo Hemorrhagic Fever, Measles, and more

**Disclaimer**
- This tool is for **information aggregation only** and must not be used as a basis for medical or public health decisions
- Article copyright belongs to each publisher. Only titles and links are displayed
- Accuracy and completeness of data are not guaranteed

**License:** MIT
""",
        "howto_header": "📖 How to Use",
        "howto_body": """\
1. Click **"🔄 Fetch Data"** to load the latest outbreak information
2. **Click a colored country on the map** to see related articles in the sidebar
   - Darker color = more outbreak reports for that country
3. **Click an article title** to open the original article in a new tab
4. Use the **Disease Filter** to narrow down which diseases are shown
5. Use the **language toggle (🇯🇵 日本語 / 🇬🇧 English)** to switch the display language. Article titles are translated automatically
6. Articles that cannot be linked to a specific country appear in the **"Regional / Unspecified News"** section

> The color bar on the right of the map shows the outbreak count scale.
""",
    },
}


def t(key: str, lang: str = "ja") -> str:
    """Return UI label for key in the given language, falling back to Japanese."""
    return _LABELS.get(lang, _LABELS["ja"]).get(key, _LABELS["ja"].get(key, key))
