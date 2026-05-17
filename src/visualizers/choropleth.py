"""World choropleth map builder using Plotly."""

import pandas as pd
import plotly.graph_objects as go


def build(df: pd.DataFrame) -> go.Figure:
    """Build a choropleth figure from a DataFrame with columns: iso3, country, count, disease."""
    fig = go.Figure(
        go.Choropleth(
            locations=df["iso3"],
            z=df["count"],
            text=df["country"] + "<br>" + df["disease"],
            colorscale="Reds",
            autocolorscale=False,
            reversescale=False,
            marker_line_color="darkgray",
            marker_line_width=0.5,
            colorbar_title="アウトブレイク数",
            hovertemplate="%{text}<br>件数: %{z}<extra></extra>",
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
