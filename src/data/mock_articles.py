"""Mock article data keyed by ISO3 country code."""

_DON = "https://www.who.int/emergencies/disease-outbreak-news"
_EBOLA_URL = (
    "https://www.who.int/emergencies/disease-outbreak-news/item/"
    "ebola-virus-disease---democratic-republic-of-the-congo"
)
_H5N1_URL = (
    "https://www.who.int/emergencies/disease-outbreak-news/item/"
    "avian-influenza-a-(h5n1)-china"
)

ARTICLES: dict[str, list[dict[str, str]]] = {
    "COD": [
        {
            "title": "コンゴ民主共和国でのエボラウイルス病アウトブレイク - 2026年5月",
            "date": "2026-05-10",
            "url": _EBOLA_URL,
        },
        {
            "title": "WHO、コンゴ東部のエボラ対応に緊急支援チームを派遣 - 2026年4月",
            "date": "2026-04-28",
            "url": _EBOLA_URL,
        },
        {
            "title": "コンゴ民主共和国エボラ出血熱：感染拡大の現状と対策 - 2026年4月",
            "date": "2026-04-15",
            "url": _EBOLA_URL,
        },
    ],
    "NGA": [
        {
            "title": "ナイジェリア北部でのラッサ熱集団感染報告 - 2026年5月",
            "date": "2026-05-08",
            "url": _DON,
        },
        {
            "title": "ラッサ熱：ナイジェリアCDCが感染予防強化を勧告 - 2026年4月",
            "date": "2026-04-20",
            "url": _DON,
        },
        {
            "title": "ナイジェリアのラッサ熱流行 - 隣国へのリスク評価報告 - 2026年3月",
            "date": "2026-03-30",
            "url": _DON,
        },
    ],
    "CHN": [
        {
            "title": "中国でのA(H5N1)型鳥インフルエンザヒト感染事例 - 2026年5月",
            "date": "2026-05-12",
            "url": _H5N1_URL,
        },
        {
            "title": "WHO、中国のH5N1鳥インフルエンザ対応状況を報告 - 2026年4月",
            "date": "2026-04-25",
            "url": _H5N1_URL,
        },
    ],
    "BRA": [
        {
            "title": "ブラジル南東部でのデング熱急増と非常事態宣言 - 2026年5月",
            "date": "2026-05-15",
            "url": _DON,
        },
        {
            "title": "ブラジル：デング熱ワクチン接種を全土で拡大 - 2026年5月",
            "date": "2026-05-01",
            "url": _DON,
        },
        {
            "title": "リオデジャネイロ州のデング熱感染者数が過去最高を更新 - 2026年4月",
            "date": "2026-04-18",
            "url": _DON,
        },
    ],
    "IND": [
        {
            "title": "インド・ケーララ州でのニパウイルス感染症事例 - 2026年5月",
            "date": "2026-05-09",
            "url": _DON,
        },
        {
            "title": "WHO、インドのニパウイルス感染対応状況を報告 - 2026年4月",
            "date": "2026-04-30",
            "url": _DON,
        },
    ],
    "SAU": [
        {
            "title": "サウジアラビアでのMERS-CoV感染事例報告 - 2026年5月",
            "date": "2026-05-07",
            "url": _DON,
        },
        {
            "title": "MERS-CoV：サウジアラビア医療施設でのクラスター確認 - 2026年4月",
            "date": "2026-04-22",
            "url": _DON,
        },
    ],
    "SSD": [
        {
            "title": "南スーダンでのコレラ感染拡大 - 避難民キャンプで多数の患者 - 2026年5月",
            "date": "2026-05-11",
            "url": _DON,
        },
        {
            "title": "WHO、南スーダンのコレラ対応に緊急物資を供給 - 2026年4月",
            "date": "2026-04-27",
            "url": _DON,
        },
        {
            "title": "南スーダン・ジュバ州のコレラ流行 - 飲料水汚染が原因と判明 - 2026年4月",
            "date": "2026-04-10",
            "url": _DON,
        },
    ],
    "BGD": [
        {
            "title": "バングラデシュでのデング熱感染者急増 - 2026年5月",
            "date": "2026-05-13",
            "url": _DON,
        },
        {
            "title": "ダッカ市内のデング熱ホットスポット - 蚊の駆除作業を強化 - 2026年5月",
            "date": "2026-05-03",
            "url": _DON,
        },
        {
            "title": "バングラデシュのデング熱 - 重症例増加を当局が警告 - 2026年4月",
            "date": "2026-04-21",
            "url": _DON,
        },
    ],
    "PER": [
        {
            "title": "ペルーでのオロポーシュウイルス病感染事例確認 - 2026年5月",
            "date": "2026-05-06",
            "url": _DON,
        },
        {
            "title": "WHO、南米のオロポーシュウイルス感染拡大に注意喚起 - 2026年4月",
            "date": "2026-04-19",
            "url": _DON,
        },
    ],
    "UGA": [
        {
            "title": "ウガンダでのマールブルグ病患者確認 - 接触者追跡を開始 - 2026年5月",
            "date": "2026-05-14",
            "url": _DON,
        },
        {
            "title": "WHO、ウガンダのマールブルグ出血熱に高リスク評価 - 2026年5月",
            "date": "2026-05-02",
            "url": _DON,
        },
    ],
}
