English | [日本語](README.ja.md)

# Emerging Infectious Disease Global Monitoring Dashboard

A Streamlit application that visualizes WHO / ECDC outbreak information and Japanese news in real time on an interactive world choropleth map.

![screenshot](docs/screenshot.png)

## Features

- **6 data sources** integrated in parallel: WHO DON, ECDC CDTR, Yahoo News Japan, 47NEWS, Google News, NHK
- **Interactive world map** — click any country to see related articles in the sidebar
- **Disease filter** — 18 diseases including Ebola, Measles, Dengue, Hantavirus, Mpox and more
- **Source whitelist** — public broadcasters, national newspapers, wire services and government bodies only
- **Country extraction** — alias dictionary (80+ countries), multi-country articles, regional/unspecified fallback
- **Bilingual UI** — Japanese / English toggle; article titles translated locally via argos-translate (no API key needed)

## Data Sources

| Source | Description |
|--------|-------------|
| [WHO Disease Outbreak News (DON)](https://www.who.int/emergencies/disease-outbreak-news) | WHO official outbreak news |
| [ECDC CDTR](https://www.ecdc.europa.eu/en/publications-and-data/monitoring/weekly-threats-reports) | ECDC weekly communicable disease threat reports |
| [Yahoo Japan News](https://news.yahoo.co.jp/) | Major / international topics RSS |
| [47NEWS](https://www.47news.jp/) | Kyodo News regional network RSS |
| [Google News](https://news.google.com/) | Keyword-filtered Google News RSS (whitelisted sources only) |

## Tech Stack

| | |
|---|---|
| **Language** | Python 3.11+ |
| **UI** | [Streamlit](https://streamlit.io/) |
| **Map** | [Plotly](https://plotly.com/python/) choropleth |
| **Package manager** | [uv](https://docs.astral.sh/uv/) |
| **Translation** | [argos-translate](https://github.com/argosopentech/argos-translate) (fully local) |
| **Country lookup** | [pycountry](https://pypi.org/project/pycountry/) |
| **Feed parsing** | [feedparser](https://pypi.org/project/feedparser/) |
| **HTML parsing** | [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/) |

## Setup

### Prerequisites

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd infectious-disease-monitor

# Install dependencies
uv sync
```

### Run

```bash
uv run streamlit run app.py
```

The app opens at `http://localhost:8501`. On first launch, outbreak data is fetched automatically.

> **Note:** The first launch also downloads the Japanese ↔ English translation models (~50 MB each) via argos-translate. An internet connection is required only for this one-time download; subsequent runs work fully offline.

## Directory Structure

```
.
├── app.py                      # Streamlit entry point
├── src/
│   ├── fetchers/               # Data fetchers (WHO, ECDC, Yahoo, 47NEWS, Google)
│   ├── parsers/                # Country extraction, disease filter, source whitelist
│   ├── data/                   # Glossary, UI labels, mock articles
│   ├── visualizers/            # Choropleth map builder
│   ├── translator.py           # argos-translate wrapper + cache
│   └── cache.py                # JSON cache management
└── data/
    └── cache/                  # Runtime cache — excluded from Git
```

## Disclaimer

- This tool is intended for **information aggregation only** and must not be used as the basis for medical or public health decisions.
- Article titles and links are displayed for reference. Copyright of each article belongs to its respective publisher.
- Please respect each website's terms of service and avoid excessive automated access.
- Accuracy and completeness of the data are not guaranteed.

## License

[MIT](LICENSE)

## Changelog

### 2026-05-30
- Split README into English (main) and Japanese (README.ja.md) versions

### 2026-05-30 (patch 2)
- Fixed missing translation in article table title column (now uses same cache as sidebar)
- Localized news source names in sidebar (Yomiuri Shimbun, Nikkei, Jiji Press, etc.)
- Added `PUBLISHER_EN` dict and `localize_label()` to `source_whitelist.py`

### 2026-05-30 (patch 1)
- Extended language toggle to all UI areas: page title, subtitles, headings
- Disease filter options now switch language (Ebola, Measles, …); selection preserved across switches
- Map colorbar and hover tooltip localized
- Article table columns and data (country names, disease names) localized
- Introduced `glossary.py` and `ui_labels.py` for centralized i18n; added `get_country_name(iso3, lang)` to `country.py`

### 2026-05-30 (initial)
- Added Japanese / English language toggle
- Implemented fully local article title translation via argos-translate
- Disease and country name glossary to prevent mistranslations
- Translation result cache (`data/cache/translations.json`)

### 2026-05-25 (5th update)
- Strengthened country extraction (title + summary, alias dictionary expanded to 80+ countries)
- Multi-country articles now mapped to all matching countries
- Added "Regional / Unspecified News" section to sidebar
- Added country extraction accuracy log (`data/cache/country_extraction.log`)

### 2026-05-25 (4th update)
- Introduced source whitelist for Google News RSS (trusted sources only)
- Defined trusted sources: public broadcasters, national newspapers, wire services, government bodies, academia
- Domain-pattern matching for prefectural agencies (`*.lg.jp`) and academia (`*.ac.jp`, `*.edu`)
- Added source breakdown list to sidebar

### 2026-05-25
- Implemented real data fetching for WHO DON / ECDC CDTR (past 3 months, with cache)
- Expanded disease filter to 18 diseases (added Measles, Hantavirus)
- Disease multiselect UI added to sidebar
- Mock data fallback on fetch failure
- Improved choropleth color scale (better visibility at count=1)
- Added Yahoo Japan, 47NEWS, and Google News RSS as data sources (5 sources total)
- Parallel fetching with `ThreadPoolExecutor`; independent per-source error handling
- Japanese country name → ISO3 mapping (70+ countries)
- Source labels in article list (🌐 WHO / 🇪🇺 ECDC / 📰 Yahoo / 🗞 47NEWS / 🔍 Google)

### 2026-05-21
- Article links open in new tab (`target="_blank"`)
- "No data" message on click with no matching articles

### 2026-05-17
- Interactive world map click to select countries
- Selected country articles shown in sidebar
- Initial release (mock data choropleth)
