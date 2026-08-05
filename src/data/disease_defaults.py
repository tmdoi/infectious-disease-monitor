"""疾患ごとの既定国（推定用）の設定。

タイトルに国名・地名・州名・広域マーカーのいずれも含まれず地域不明になる記事に
対してのみ、疾患から流行国を推定するために使う。

⚠️ 暫定設定（流行状況依存）
    ここに書かれた対応は「その年の流行がどこで起きているか」に依存する暫定的な
    ものであり、流行地が移れば誤った推定になる。定期的に見直し、流行が収束したら
    エントリを削除すること。値を変更・削除する箇所はこの辞書 1 か所だけでよい。

現在の設定:
    サイクロスポラ症 → USA  （2026年夏のレタス由来アウトブレイクが米国中心のため）
"""

from __future__ import annotations

# 日本語疾患名（disease_filter の表示名）→ ISO3
DISEASE_DEFAULT_COUNTRY: dict[str, str] = {
    "サイクロスポラ症": "USA",
}


def default_country(disease_ja: str) -> str | None:
    """Return the provisional default ISO3 for a disease name, or None if unset."""
    return DISEASE_DEFAULT_COUNTRY.get(disease_ja)
