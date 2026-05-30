# 新興感染症 世界モニタリングダッシュボード

## プロジェクト概要

WHO / ECDC のアウトブレイク情報を世界地図（コロプレスマップ）でリアルタイム可視化する Streamlit アプリ。

- 対象: 全世界 WHO 加盟国 約190カ国
- 対象疾患: 新興・新種ウイルスのアウトブレイク
- 更新方式: 手動（UI ボタンでデータ取得）

## 実行コマンド

```bash
uv run streamlit run app.py
```

## ディレクトリ構造

```
.
├── app.py                  # Streamlit エントリーポイント
├── src/
│   ├── fetchers/           # 外部データ取得
│   │   ├── who_don.py      # WHO Disease Outbreak News
│   │   └── ecdc_cdtr.py    # ECDC Communicable Disease Threats Report
│   ├── parsers/            # データ変換
│   │   └── country.py      # 国名 → ISO3 変換
│   └── visualizers/        # 描画
│       └── choropleth.py   # Plotly コロプレスマップ
└── data/
    └── cache/              # 取得データのキャッシュ（Git 管理外）
```

## データソース

| ソース | URL | 形式 |
|--------|-----|------|
| WHO DON | https://www.who.int/emergencies/disease-outbreak-news | RSS / HTML |
| ECDC CDTR | https://www.ecdc.europa.eu/en/publications-data/communicable-disease-threats-report | PDF / HTML |

## コーディング規約

- Python 3.11+ の型ヒントを使用する（`str | None` など union 構文）
- 各モジュールのパブリック関数には docstring を書く（1行で十分）
- コメントは「なぜ」が自明でない場合のみ記載
- フォーマッタ: `ruff format`、リンタ: `ruff check`
- テストは `pytest` を使用（`uv run pytest`）

## 依存関係

パッケージ管理は `uv` を使用。依存追加は `uv add <package>`。

## 更新ルール

このプロジェクトに変更を加えた際は、**README.md(英語版)と README.ja.md(日本語版)の両方**の「更新履歴 / Changelog」セクションに追記すること。

- README.md(英語版): 英語で記載
- README.ja.md(日本語版): 日本語で記載
- 新しい変更は上(新しい日付が上)に追記する
- 日付は実装日

フォーマット:

**README.md (English)**
```
### YYYY-MM-DD
- Brief description in English (1–3 lines)
```

**README.ja.md (日本語)**
```
### YYYY-MM-DD
- 変更内容を簡潔に1-3行で記載
```
