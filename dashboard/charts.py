import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# FINHUB DASHBOARD — CHARTS
# ============================================================

CHART_TEMPLATE = "plotly_white"


def market_movers_chart(df):
    """Horizontal bar chart for biggest stock movements."""

    if df.empty:
        return go.Figure()

    data = df.copy()

    data["PRICE_CHANGE_PERCENT"] = data["PRICE_CHANGE_PERCENT"].astype(float)

    data = data.sort_values("PRICE_CHANGE_PERCENT")

    fig = px.bar(
        data,
        x="PRICE_CHANGE_PERCENT",
        y="SYMBOL",
        orientation="h",
        text="PRICE_CHANGE_PERCENT",
        template=CHART_TEMPLATE,
        title="Market Movers",
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Change: %{x:.2f}%"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        height=430,
        margin=dict(l=20, r=60, t=60, b=30),
        xaxis_title="Price Change (%)",
        yaxis_title=None,
        showlegend=False,
    )

    return fig


def volume_chart(df):
    """Top stocks by trading volume."""

    if df.empty:
        return go.Figure()

    data = df.copy()

    data["VOLUME"] = data["VOLUME"].astype(float)

    data = data.sort_values("VOLUME")

    fig = px.bar(
        data,
        x="VOLUME",
        y="SYMBOL",
        orientation="h",
        template=CHART_TEMPLATE,
        title="Highest Trading Volume",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Volume: %{x:,}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=430,
        margin=dict(l=20, r=30, t=60, b=30),
        xaxis_title="Volume",
        yaxis_title=None,
        showlegend=False,
    )

    return fig


def stock_price_chart(df, symbol):
    """Stock price history chart."""

    if df.empty:
        return go.Figure()

    data = df.copy()

    data["QUOTE_TIMESTAMP"] = data["QUOTE_TIMESTAMP"].astype(str)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["QUOTE_TIMESTAMP"],
            y=data["CURRENT_PRICE"],
            mode="lines+markers",
            name="Price",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Price: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=f"{symbol} Price Movement",
        template=CHART_TEMPLATE,
        height=420,
        margin=dict(l=20, r=30, t=60, b=40),
        xaxis_title=None,
        yaxis_title="Price",
        showlegend=False,
        hovermode="x unified",
    )

    return fig


def stock_volume_chart(df, symbol):
    """Stock trading volume chart."""

    if df.empty:
        return go.Figure()

    data = df.copy()

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=data["QUOTE_TIMESTAMP"],
            y=data["VOLUME"],
            name="Volume",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Volume: %{y:,}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=f"{symbol} Trading Volume",
        template=CHART_TEMPLATE,
        height=350,
        margin=dict(l=20, r=30, t=60, b=40),
        xaxis_title=None,
        yaxis_title="Volume",
        showlegend=False,
    )

    return fig


def earnings_surprise_chart(df, symbol):
    """Actual vs estimated earnings."""

    if df.empty:
        return go.Figure()

    data = df.copy()

    data = data.sort_values("PERIOD")

    fig = go.Figure()

    if "ESTIMATE" in data.columns:
        fig.add_trace(
            go.Bar(
                x=data["PERIOD"],
                y=data["ESTIMATE"],
                name="Estimate",
            )
        )

    if "ACTUAL" in data.columns:
        fig.add_trace(
            go.Bar(
                x=data["PERIOD"],
                y=data["ACTUAL"],
                name="Actual",
            )
        )

    fig.update_layout(
        title=f"{symbol} Earnings — Actual vs Estimate",
        template=CHART_TEMPLATE,
        height=380,
        barmode="group",
        margin=dict(l=20, r=30, t=60, b=40),
        xaxis_title=None,
        yaxis_title="EPS",
    )

    return fig