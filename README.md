# 新興感染症 世界モニタリングダッシュボード

WHO / ECDC のアウトブレイク情報を世界地図（コロプレスマップ）でリアルタイム可視化する Streamlit アプリです。

## 機能

- 世界全190カ国を対象とした感染症アウトブレイクの地図表示
- 国クリックで詳細情報を表示
- 手動ボタンでデータを最新状態に更新

## データソース

| ソース | 内容 |
|--------|------|
| [WHO Disease Outbreak News (DON)](https://www.who.int/emergencies/disease-outbreak-news) | WHO が公表する感染症アウトブレイク速報 |
| [ECDC CDTR](https://www.ecdc.europa.eu/en/publications-data/communicable-disease-threats-report) | 欧州疾病予防管理センターの週次レポート |

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

ブラウザで `http://localhost:8501` が自動的に開きます。

## ディレクトリ構造

```
.
├── app.py                  # Streamlit エントリーポイント
├── src/
│   ├── fetchers/           # 外部データ取得モジュール
│   ├── parsers/            # データ変換モジュール（国名→ISO3など）
│   └── visualizers/        # 地図描画モジュール
└── data/
    └── cache/              # 取得データのキャッシュ（Git 管理外）
```

## 技術スタック

- **Python 3.11**
- **[Streamlit](https://streamlit.io/)** — Web UI フレームワーク
- **[Plotly](https://plotly.com/python/)** — インタラクティブ地図描画
- **[uv](https://docs.astral.sh/uv/)** — パッケージ管理
