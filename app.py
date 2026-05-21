"""新興感染症 世界モニタリングダッシュボード"""

import pandas as pd
import streamlit as st

from src.data.mock_articles import ARTICLES
from src.visualizers.choropleth import build

st.set_page_config(
    page_title="新興感染症モニタリング",
    page_icon="🦠",
    layout="wide",
)

MOCK_DATA = [
    {"iso3": "COD", "country": "コンゴ民主共和国", "disease": "エボラ出血熱", "count": 5},
    {"iso3": "NGA", "country": "ナイジェリア", "disease": "ラッサ熱", "count": 3},
    {"iso3": "CHN", "country": "中国", "disease": "H5N1型鳥インフルエンザ", "count": 2},
    {"iso3": "BRA", "country": "ブラジル", "disease": "デング熱", "count": 8},
    {"iso3": "IND", "country": "インド", "disease": "ニパウイルス感染症", "count": 1},
    {"iso3": "SAU", "country": "サウジアラビア", "disease": "MERS-CoV", "count": 2},
    {"iso3": "SSD", "country": "南スーダン", "disease": "コレラ", "count": 4},
    {"iso3": "BGD", "country": "バングラデシュ", "disease": "デング熱", "count": 6},
    {"iso3": "PER", "country": "ペルー", "disease": "オロポーシュウイルス病", "count": 2},
    {"iso3": "UGA", "country": "ウガンダ", "disease": "マールブルグ病", "count": 1},
]

if "data" not in st.session_state:
    st.session_state.data = None
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None
if "selected_iso3" not in st.session_state:
    st.session_state.selected_iso3 = None

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📋 選択中の国")

    iso3 = st.session_state.selected_iso3

    if iso3 is None:
        st.info("地図上の国をクリックしてください")
    else:
        df_all = pd.DataFrame(MOCK_DATA)
        rows = df_all[df_all["iso3"] == iso3]

        if not rows.empty:
            row = rows.iloc[0]
            st.subheader(row["country"])
            st.caption(f"疾患: {row['disease']}　件数: {row['count']}")
            st.divider()
            articles = ARTICLES.get(iso3, [])
            if articles:
                st.markdown("**関連記事**")
                for article in articles:
                    st.markdown(f"- {article['title']}  \n  `{article['date']}`")
            else:
                st.write("記事データがありません。")
        else:
            st.warning(f"**{iso3}** のデータはありません。")

        if st.button("選択を解除", use_container_width=True):
            st.session_state.selected_iso3 = None
            st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("🦠 新興感染症 世界モニタリングダッシュボード")
st.caption("WHO / ECDC のアウトブレイク情報をリアルタイムで可視化します。")

col_btn, col_status = st.columns([1, 4])
with col_btn:
    fetch_clicked = st.button("🔄 データ取得", type="primary", use_container_width=True)
with col_status:
    if st.session_state.last_updated:
        st.info(f"最終更新: {st.session_state.last_updated}")
    else:
        st.warning("データ未取得 — 「データ取得」ボタンを押してください。")

if fetch_clicked:
    with st.spinner("データを取得中..."):
        import time
        time.sleep(0.8)
        st.session_state.data = MOCK_DATA
        from datetime import datetime
        st.session_state.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.success("取得完了（モックデータ）")

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)

    st.subheader("世界アウトブレイクマップ")
    selected = st.plotly_chart(build(df), use_container_width=True, on_select="rerun")

    if selected and selected.get("selection", {}).get("points"):
        clicked_iso3 = selected["selection"]["points"][0].get("location")
        if clicked_iso3 and clicked_iso3 != st.session_state.selected_iso3:
            st.session_state.selected_iso3 = clicked_iso3
            st.rerun()

    st.divider()
    st.subheader("アウトブレイク一覧")
    st.dataframe(
        df.rename(columns={"iso3": "ISO3", "country": "国名", "disease": "疾患", "count": "件数"}),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.subheader("世界アウトブレイクマップ")
    st.info("「データ取得」ボタンを押すとマップが表示されます。")
