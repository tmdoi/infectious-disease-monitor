[English](README.md) | 日本語

# 新興感染症 世界モニタリングダッシュボード

WHO / ECDC のアウトブレイク情報と日本語ニュースを、インタラクティブな世界コロプレスマップでリアルタイム可視化する Streamlit アプリです。

![screenshot](docs/screenshot.png)

## 主な機能

- **6データソース**を並列取得: WHO DON、ECDC CDTR、Yahoo ニュース Japan、47NEWS、Google ニュース、NHK
- **インタラクティブ世界地図** — 国をクリックするとサイドバーに関連記事を表示
- **疾患フィルタ** — エボラ、麻疹、デング熱、ハンタウイルス、エムポックスなど18疾患
- **配信元ホワイトリスト** — 公共放送・全国紙・通信社・公的機関のみ
- **国名抽出** — 表記揺れ辞書(80カ国以上)、複数国対応、広域・不明セクション
- **日英相互翻訳** — argos-translate による完全ローカル翻訳(APIキー不要)

## データソース

| ソース | 内容 |
|--------|------|
| [WHO Disease Outbreak News (DON)](https://www.who.int/emergencies/disease-outbreak-news) | WHO が公表する感染症アウトブレイク速報 |
| [ECDC CDTR](https://www.ecdc.europa.eu/en/publications-and-data/monitoring/weekly-threats-reports) | 欧州疾病予防管理センターの週次レポート |
| [Yahoo Japan トピックス](https://news.yahoo.co.jp/) | Yahoo Japan 主要・国際トピックス RSS |
| [47NEWS](https://www.47news.jp/) | 共同通信系地方紙連合ニュース RSS |
| [Google ニュース](https://news.google.com/) | 疾患キーワードによる Google News RSS(ホワイトリスト済み) |

## 技術スタック

| | |
|---|---|
| **言語** | Python 3.11+ |
| **UI** | [Streamlit](https://streamlit.io/) |
| **地図** | [Plotly](https://plotly.com/python/) コロプレスマップ |
| **パッケージ管理** | [uv](https://docs.astral.sh/uv/) |
| **翻訳** | [argos-translate](https://github.com/argosopentech/argos-translate)(完全ローカル) |
| **国名解決** | [pycountry](https://pypi.org/project/pycountry/) |
| **フィード解析** | [feedparser](https://pypi.org/project/feedparser/) |
| **HTML解析** | [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/) |

## セットアップ

### 前提条件

- Python 3.11 以上
- [uv](https://docs.astral.sh/uv/)（パッケージマネージャ）

### インストール

```bash
# リポジトリのクローン
git clone <repository-url>
cd infectious-disease-monitor

# 依存パッケージのインストール
uv sync
```

### 実行

```bash
uv run streamlit run app.py
```

ブラウザで `http://localhost:8501` が開きます。初回起動時はアウトブレイクデータを自動取得します。

> **注意:** 初回起動時には argos-translate の日英翻訳モデル(各 ~50 MB)もダウンロードされます。ネット接続が必要なのはこの1回のみで、以降は完全オフラインで動作します。

## ディレクトリ構造

```
.
├── app.py                      # Streamlit エントリーポイント
├── src/
│   ├── fetchers/               # データ取得(WHO / ECDC / Yahoo / 47NEWS / Google)
│   ├── parsers/                # 国名抽出・疾患フィルタ・配信元ホワイトリスト
│   ├── data/                   # 用語集・UIラベル・モックデータ
│   ├── visualizers/            # コロプレスマップ描画
│   ├── translator.py           # argos-translate ラッパー + キャッシュ
│   └── cache.py                # JSON キャッシュ管理
└── data/
    └── cache/                  # 実行時キャッシュ(Git 管理外)
```

## 免責事項

- 本ツールは**情報集約を目的**としており、医学的・公衆衛生上の判断の根拠として使用してはなりません。
- 各記事のタイトルとリンクのみを表示します。著作権は各配信元に帰属します。
- 各サイトの利用規約を尊重し、過度なアクセスを行わないでください。
- データの正確性・完全性は保証されません。

## 開発について

このプロジェクトは [Claude Code](https://claude.ai/code)(Anthropic の AI コーディング支援ツール)を活用して開発しました。設計方針の検討から実装、デバッグまで、AI ペアプログラミングの形で進めています。

## ライセンス

[MIT](LICENSE)

## 更新履歴

### 2026-05-30(4回目)
- 開発体制(Claude Code 活用)についての記載を追加
- サイドバーに About と使い方メニューを追加(日英対応、st.expander で折りたたみ式)

### 2026-05-30
- README を日英2ファイル構成に整備(英語をメイン、日本語版を README.ja.md に分離)

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
- 疾患フィルタを18疾患に拡張(麻疹を新規追加、ハンタウイルス含む)
- 疾患マルチセレクト UI をサイドバーに追加
- 実データ取得失敗時のモックデータフォールバックを実装
- コロプレスマップの色スケールを改善(度数1の視認性向上、離散的近似ステップ関数)
- Yahoo Japan トピックスRSS(主要・国際)をデータソースに追加
- 47NEWS RSS と Google ニュース RSS をデータソースに追加(計6ソース)
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
