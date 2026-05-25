"""World choropleth map builder using Plotly."""

import pandas as pd
import plotly.graph_objects as go

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


def build(df: pd.DataFrame) -> go.Figure:
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
    # Custom colorscale ensures count=1 renders as visible orange rather than near-white.
    # zmin=0 anchors the scale so z=1 maps to ~10% position (clear "#fc8d59").
    _COLORSCALE = [
        [0.00, "#fff5f0"],
        [0.10, "#fc8d59"],
        [0.40, "#de2d26"],
        [1.00, "#67000d"],
    ]
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
            colorbar_title="アウトブレイク数",
            hovertemplate="%{text}<br>件数: %{z}<extra></extra>",
            name="",
        )
    )

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=520,
    )
    return fig
