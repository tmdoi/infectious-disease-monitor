# 新興感染症 世界モニタリングダッシュボード

WHO / ECDC / Yahoo Japan / 47NEWS / Google ニュース のアウトブレイク情報を世界地図（コロプレスマップ）でリアルタイム可視化する Streamlit アプリです。

## 機能

- 世界全190カ国を対象とした感染症アウトブレイクの地図表示
- 16疾患(エボラ・麻疹・デング熱など)の疾患フィルタ
- 国クリックで詳細情報と WHO DON 記事リンクを表示
- 手動ボタンでデータを最新状態に更新(過去3ヶ月分、キャッシュ付き)
- 5データソースを並列取得、ソース別エラーハンドリング付き

## データソース

| ソース | 内容 |
|--------|------|
| [WHO Disease Outbreak News (DON)](https://www.who.int/emergencies/disease-outbreak-news) | WHO が公表する感染症アウトブレイク速報 |
| [ECDC CDTR](https://www.ecdc.europa.eu/en/publications-and-data/monitoring/weekly-threats-reports) | 欧州疾病予防管理センターの週次レポート |
| [Yahoo Japan トピックス](https://news.yahoo.co.jp/) | Yahoo Japan 主要・国際トピックス RSS |
| [47NEWS](https://www.47news.jp/) | 共同通信系地方紙連合ニュース RSS |
| [Google ニュース](https://news.google.com/) | 疾患キーワードによる Google News RSS 検索 |

## セットアップ

### 前提条件

- Python 3.11 以上
- [uv](https://docs.astral.sh/uv/) （パッケージマネージャ）

### 手順

```bash
# リポジトリのクローン
git clone <repository-url>
cd infectious-disease-monitor

# 依存パッケージのインストール
uv sync
```

## 実行方法

```bash
uv run streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。初回起動時はデータを自動取得します。

## ディレクトリ構造

```
.
├── app.py                  # Streamlit エントリーポイント
├── src/
│   ├── fetchers/           # 外部データ取得モジュール
│   ├── parsers/            # データ変換モジュール（国名→ISO3、疾患フィルタ）
│   ├── cache.py            # JSON キャッシュ管理
│   └── visualizers/        # 地図描画モジュール
└── data/
    └── cache/              # 取得データのキャッシュ（Git 管理外）
```

## 技術スタック

- **Python 3.11**
- **[Streamlit](https://streamlit.io/)** — Web UI フレームワーク
- **[Plotly](https://plotly.com/python/)** — インタラクティブ地図描画
- **[uv](https://docs.astral.sh/uv/)** — パッケージ管理

## 更新履歴

### 2026-05-30(2回目)
- 下部の記事一覧テーブルのタイトル列を日英翻訳に対応(サイドバーと同じキャッシュを共用)
- サイドバーのソース名(読売新聞→Yomiuri Shimbun、時事通信→Jiji Press など)を日英対訳に対応
- source_whitelist.py に PUBLISHER_EN 辞書と localize_label() を追加

### 2026-05-30
- 言語トグルの対応範囲を全画面に拡大: ページタイトル・サブタイトル・各見出しを日英切替
- 疾患フィルタの選択肢を日英対応(Ebola, Measles など)、言語切替時も選択状態を維持
- 地図の凡例(アウトブレイク数 / Number of Outbreaks)・ホバーツールチップを言語連動
- 下部テーブルの列ヘッダーとデータ(国名・疾患名)を日英切替
- UIラベル辞書(ui_labels.py)と疾患用語集(glossary.py)を整備し全コンポーネントで共通化
- country.py に get_country_name(iso3, lang) を追加(英語国名は pycountry から取得)

### 2026-05-30(初版)
- 日英言語トグルを追加(画面上部)
- argos-translate による完全ローカル翻訳機能を実装(記事タイトルの日英相互翻訳)
- 疾患名・国名の確定訳用語集で誤訳を防止
- 翻訳結果のキャッシュ機構を追加(data/cache/translations.json)

### 2026-05-25(5回目)
- 国名抽出を強化(タイトル+概要から検出、表記揺れ辞書を80カ国以上に拡充)
- 複数国記事は該当するすべての国に反映するよう変更
- サイドバーに「広域・地域不明ニュース」セクションを新設
- 国判定の精度ログ出力機能を追加(data/cache/country_extraction.log)

### 2026-05-25(4回目)
- Google ニュース RSS にホワイトリストフィルタを導入(公共性の高いソースのみ通す)
- 信頼ソースとして公共放送・全国紙・通信社・公的機関・アカデミアを定義
- 都道府県(*.lg.jp など)とアカデミア(*.ac.jp, *.edu)はドメインパターンで判定
- サイドバーに「配信元一覧」(件数の多い順)を追加

### 2026-05-25
- WHO DON / ECDC CDTR の実データ取得を実装(過去3ヶ月、キャッシュ機構付き)
- 疾患フィルタを16疾患に拡張(麻疹を新規追加、ハンタウイルス含む)
- 疾患マルチセレクト UI をサイドバーに追加
- 実データ取得失敗時のモックデータフォールバックを実装
- コロプレスマップの色スケールを改善(度数1の視認性向上、離散的近似ステップ関数)
- Yahoo Japan トピックスRSS(主要・国際)をデータソースに追加
- 47NEWS RSS と Google ニュース RSS をデータソースに追加(計5ソース)
- 5ソースの並列フェッチ(ThreadPoolExecutor)とソース別独立エラーハンドリング
- 日本語国名→ISO3 変換マッピングを追加(主要70カ国)
- 記事一覧にソースラベル(🌐 WHO / 🇪🇺 ECDC / 📰 Yahoo / 🗞 47NEWS / 🔍 Google)を表示

### 2026-05-21
- 記事リンクの新規タブ表示(target="_blank")対応
- データなし国クリック時の「データなし」表示

### 2026-05-17
- 世界地図クリックインタラクションを実装
- 選択中の国の記事をサイドバーに表示
- 初版リリース(モックデータによる世界アウトブレイクマップ)
