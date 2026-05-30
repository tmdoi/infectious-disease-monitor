"""World choropleth map builder using Plotly."""

import pandas as pd
import plotly.graph_objects as go

from src.data.ui_labels import t

# UN member states ISO-3 codes — used as a background trace so that
# data-less countries also fire on_select click events.
_WORLD_ISO3: list[str] = [
    "AFG", "ALB", "DZA", "AND", "AGO", "ATG", "ARG", "ARM", "AUS", "AUT",
    "AZE", "BHS", "BHR", "BGD", "BRB", "BLR", "BEL", "BLZ", "BEN", "BTN",
    "BOL", "BIH", "BWA", "BRA", "BRN", "BGR", "BFA", "BDI", "CPV", "KHM",
    "CMR", "CAN", "CAF", "TCD", "CHL", "CHN", "COL", "COM", "COD", "COG",
    "CRI", "CIV", "HRV", "CUB", "CYP", "CZE", "DNK", "DJI", "DOM", "ECU",
    "EGY", "SLV", "GNQ", "ERI", "EST", "SWZ", "ETH", "FJI", "FIN", "FRA",
    "GAB", "GMB", "GEO", "DEU", "GHA", "GRC", "GRD", "GTM", "GIN", "GNB",
    "GUY", "HTI", "HND", "HUN", "ISL", "IND", "IDN", "IRN", "IRQ", "IRL",
    "ISR", "ITA", "JAM", "JPN", "JOR", "KAZ", "KEN", "KIR", "PRK", "KOR",
    "KWT", "KGZ", "LAO", "LVA", "LBN", "LSO", "LBR", "LBY", "LIE", "LTU",
    "LUX", "MDG", "MWI", "MYS", "MDV", "MLI", "MLT", "MHL", "MRT", "MUS",
    "MEX", "FSM", "MDA", "MCO", "MNG", "MNE", "MAR", "MOZ", "MMR", "NAM",
    "NRU", "NPL", "NLD", "NZL", "NIC", "NER", "NGA", "MKD", "NOR", "OMN",
    "PAK", "PLW", "PAN", "PNG", "PRY", "PER", "PHL", "POL", "PRT", "QAT",
    "ROU", "RUS", "RWA", "KNA", "LCA", "VCT", "WSM", "SMR", "STP", "SAU",
    "SEN", "SRB", "SYC", "SLE", "SGP", "SVK", "SVN", "SLB", "SOM", "ZAF",
    "SSD", "ESP", "LKA", "SDN", "SUR", "SWE", "CHE", "SYR", "TJK", "TZA",
    "THA", "TLS", "TGO", "TON", "TTO", "TUN", "TUR", "TKM", "TUV", "UGA",
    "UKR", "ARE", "GBR", "USA", "URY", "UZB", "VUT", "VEN", "VNM", "YEM",
    "ZMB", "ZWE",
]


def build(df: pd.DataFrame, lang: str = "ja") -> go.Figure:
    """Build a choropleth figure from a DataFrame with columns: iso3, country, count, disease."""
    fig = go.Figure()

    # Background trace: nearly transparent fill so all countries register click events
    # without visually overriding the base map land color.
    fig.add_trace(
        go.Choropleth(
            locations=_WORLD_ISO3,
            z=[0] * len(_WORLD_ISO3),
            colorscale=[[0, "rgba(200,200,200,0.05)"], [1, "rgba(200,200,200,0.05)"]],
            showscale=False,
            hoverinfo="none",
            marker_line_color="darkgray",
            marker_line_width=0.3,
            name="",
        )
    )

    # Data trace: countries with outbreak data.
    # zmin=0 anchors the scale; position 0.001 makes a near-step so count=1
    # always lands in the saturated orange zone regardless of the max count.
    _COLORSCALE = [
        [0.000, "#fff5eb"],  # z=0 anchor (never shown; data trace has no 0-count entries)
        [0.001, "#f16913"],  # immediate jump → count=1 always renders as clear orange
        [0.300, "#d94801"],  # count 2-3 → darker orange
        [0.600, "#a63603"],  # count 4-6 → dark reddish-orange
        [1.000, "#7f2704"],  # max count → deepest red
    ]
    hover_count_label = t("hover_count", lang)
    fig.add_trace(
        go.Choropleth(
            locations=df["iso3"],
            z=df["count"],
            zmin=0,
            text=df["country"] + "<br>" + df["disease"],
            colorscale=_COLORSCALE,
            autocolorscale=False,
            reversescale=False,
            marker_line_color="darkgray",
            marker_line_width=0.5,
            colorbar_title=t("colorbar_title", lang),
            hovertemplate=f"%{{text}}<br>{hover_count_label}: %{{z}}<extra></extra>",
            name="",
        )
    )

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
            # Anchor the viewport to valid geographic bounds.
            # Without these, aggressive zoom-out pushes lon/lat beyond ±180/±90,
            # causing Plotly.js to produce NaN coordinates and freeze the map.
            lataxis=dict(range=[-90, 90]),
            lonaxis=dict(range=[-180, 180]),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=520,
        # Preserve the user's zoom/pan state across Streamlit reruns.
        # on_select="rerun" triggers a Python rerun on every country click;
        # without uirevision the map would reset to the default view each time.
        uirevision="world-map",
        # Pan mode: drag scrolls the map, scroll-wheel zooms.
        # Single-click still fires on_select normally.
        # Avoids the drag-to-zoom-box mode that can push the viewport out of bounds.
        dragmode="pan",
    )
    return fig
