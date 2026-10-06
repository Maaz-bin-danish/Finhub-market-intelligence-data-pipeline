# ============================================================
# FINHUB — MARKET INTELLIGENCE
# Executive Business Intelligence Dashboard
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from snowflake_connection import run_query
from queries import (
    OVERVIEW_KPIS,
    MARKET_MOVERS,
    STOCK_LIST,
    STOCK_DETAIL,
    STOCK_PRICE_HISTORY,
    STOCK_NEWS,
    STOCK_EARNINGS,
    STOCK_PEERS,
    EARNINGS_CALENDAR,
    IPO_CALENDAR,
    LATEST_NEWS,
    NEWS_BY_SYMBOL,
    CRYPTO_OVERVIEW,
    CRYPTO_ASSETS,
    CRYPTO_EXCHANGES,
    FOREX_PAIRS,
    MARKET_STATUS,
    MARKET_HOLIDAYS,
)
from styles import load_styles
load_styles()


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FINHUB — Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# st.markdown(
#     """
#     <div class="finhub-main-title">FINHUB</div>
#     <div class="finhub-main-subtitle">Market Intelligence & Business Analytics</div>
#     """,
#     unsafe_allow_html=True,
# )
# ============================================================
# THEME / NATIVE CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       FINHUB — PROFESSIONAL BI THEME
       Streamlit light + dark theme compatible
       ======================================================== */

    /* ---------- Main application ---------- */

    .stApp {
        background: var(--background-color);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        padding-left: 2.2rem;
        padding-right: 2.2rem;
    }

    /* ---------- Sidebar ---------- */

    section[data-testid="stSidebar"] {
        border-right: 1px solid var(--secondary-background-color);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.2rem;
    }

    section[data-testid="stSidebar"] .stRadio label {
        font-weight: 500;
    }

    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stTextInput label,
    section[data-testid="stSidebar"] .stMultiSelect label {
        font-weight: 600;
        font-size: 0.82rem;
    }

    /* ---------- Typography ---------- */

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color);
        letter-spacing: -0.02em;
    }

    .finhub-main-title {
        margin-top: 0;
        margin-bottom: 0.15rem;
        color: var(--text-color);
        font-size: 2.6rem;
        line-height: 1.05;
        font-weight: 850;
        letter-spacing: -0.05em;
    }

    .finhub-main-subtitle {
        color: var(--secondary-text-color);
        font-size: 0.92rem;
        font-weight: 500;
        margin-bottom: 1.4rem;
    }

    h2 {
        margin-top: 1.8rem;
        margin-bottom: 0.3rem;
        font-weight: 700;
    }

    h3 {
        margin-top: 1.4rem;
        margin-bottom: 0.2rem;
        font-weight: 700;
    }

    p {
        color: var(--text-color);
    }

    /* ---------- Metrics ---------- */

    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        min-height: 105px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.72rem;
        font-weight: 650;
        letter-spacing: 0.04em;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.65rem;
        font-weight: 750;
        letter-spacing: -0.03em;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 0.78rem;
        font-weight: 650;
    }

    /* ---------- Inputs ---------- */

    div[data-baseweb="select"] > div {
        border-radius: 8px;
    }

    .stTextInput input {
        border-radius: 8px;
    }

    .stNumberInput input {
        border-radius: 8px;
    }

    .stDateInput input {
        border-radius: 8px;
    }

    /* ---------- Buttons ---------- */

    .stButton > button {
        border-radius: 8px;
        font-weight: 650;
        min-height: 38px;
    }

    .stDownloadButton > button {
        border-radius: 8px;
        font-weight: 650;
    }

    /* ---------- DataFrames ---------- */

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 10px;
        overflow: hidden;
    }

    /* ---------- Expanders ---------- */

    div[data-testid="stExpander"] {
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 10px;
    }

    /* ---------- Tabs ---------- */

    button[data-baseweb="tab"] {
        font-weight: 600;
    }

    /* ---------- Horizontal divider ---------- */

    hr {
        border: none;
        border-top: 1px solid rgba(128, 128, 128, 0.18);
        margin: 1.2rem 0;
    }

    /* ---------- Alerts ---------- */

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* ---------- Charts ---------- */

    div[data-testid="stPlotlyChart"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ---------- Columns ---------- */

    div[data-testid="column"] {
        min-width: 0;
    }

    /* ---------- Sidebar buttons / refresh ---------- */

    section[data-testid="stSidebar"] button {
        border-radius: 8px;
    }

    /* ---------- Hide Streamlit branding ---------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* Keep header space small without destroying layout */

    header[data-testid="stHeader"] {
        background: transparent;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def cached_query(query, params=None):
    """
    Cached Snowflake query with native parameter binding.
    """

    return run_query(query, params=params)


def clean_number(value, decimals=2):
    if value is None:
        return "—"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"

    return f"{value:,.{decimals}f}"


def clean_percent(value):
    if value is None:
        return "—"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"

    if value > 0:
        return f"+{value:.2f}%"

    return f"{value:.2f}%"


def compact_number(value):
    if value is None:
        return "—"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"

    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"

    if value >= 1_000:
        return f"{value / 1_000:.1f}K"

    return f"{int(value):,}"


def section(title, caption=None):
    st.markdown(
        f"### {title}"
    )

    if caption:
        st.caption(caption)

def style_market_table(df, percent_columns=None):
    """
    Green positive / red negative formatting.
    No raw HTML.
    """

    if df.empty:
        return df

    percent_columns = percent_columns or []

    def color_value(value):
        try:
            number = float(value)

            if number > 0:
                return "color: #15803d; font-weight: 700;"

            if number < 0:
                return "color: #dc2626; font-weight: 700;"

        except (TypeError, ValueError):
            pass

        return ""

    styler = df.style

    for column in percent_columns:
        if column in df.columns:
            styler = styler.map(color_value, subset=[column])

    return styler


def latest_per_symbol(df):
    if df.empty:
        return df

    required = {"SYMBOL", "QUOTE_TIMESTAMP"}

    if not required.issubset(df.columns):
        return df

    result = df.copy()

    result["QUOTE_TIMESTAMP"] = pd.to_datetime(
        result["QUOTE_TIMESTAMP"],
        errors="coerce",
    )

    result = (
        result.sort_values("QUOTE_TIMESTAMP")
        .drop_duplicates("SYMBOL", keep="last")
    )

    return result


def create_price_chart(df, symbol):
    if df.empty:
        return None

    chart_df = df.copy()

    chart_df["QUOTE_TIMESTAMP"] = pd.to_datetime(
        chart_df["QUOTE_TIMESTAMP"],
        errors="coerce",
    )

    chart_df["CURRENT_PRICE"] = pd.to_numeric(
        chart_df["CURRENT_PRICE"],
        errors="coerce",
    )

    chart_df = chart_df.dropna(
        subset=["QUOTE_TIMESTAMP", "CURRENT_PRICE"]
    )

    if chart_df.empty:
        return None

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_df["QUOTE_TIMESTAMP"],
            y=chart_df["CURRENT_PRICE"],
            mode="lines",
            name=str(symbol),
            line=dict(
                color="#2563eb",
                width=2.5,
            ),
            hovertemplate=(
                "<b>%{y:.2f}</b>"
                "<br>%{x}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=None,
        height=390,
        margin=dict(l=10, r=10, t=20, b=10),

        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",

        hovermode="x unified",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#111827",
        ),

        xaxis=dict(
            title=dict(
                text="",
            ),
            showgrid=False,
            showticklabels=True,
            tickfont=dict(
                family="Inter, Arial, sans-serif",
                color="#111827",
                size=12,
            ),
            linecolor="#d1d5db",
            tickcolor="#9ca3af",
        ),

        yaxis=dict(
            title=dict(
                text="Price",
                font=dict(
                    family="Inter, Arial, sans-serif",
                    color="#111827",
                    size=13,
                ),
            ),
            showgrid=True,
            gridcolor="#eef2f7",
            tickfont=dict(
                family="Inter, Arial, sans-serif",
                color="#111827",
                size=12,
            ),
            linecolor="#d1d5db",
            tickcolor="#9ca3af",
        ),

        legend=dict(
            visible=True,
            font=dict(
                family="Inter, Arial, sans-serif",
                color="#111827",
                size=12,
            ),
            bgcolor="#ffffff",
            bordercolor="#e5e7eb",
            borderwidth=1,
        ),
    )

    return fig


def create_movement_chart(df):
    if df.empty:
        return None

    chart_df = df.copy()

    chart_df["PRICE_CHANGE_PCT"] = pd.to_numeric(
        chart_df["PRICE_CHANGE_PCT"],
        errors="coerce",
    )

    chart_df = chart_df.dropna(
        subset=["PRICE_CHANGE_PCT"]
    )

    if chart_df.empty:
        return None

    chart_df = chart_df.sort_values(
        "PRICE_CHANGE_PCT"
    )

    colors = [
        "#dc2626" if value < 0 else "#16a34a"
        for value in chart_df["PRICE_CHANGE_PCT"]
    ]

    fig = go.Figure(
        go.Bar(
            x=chart_df["PRICE_CHANGE_PCT"],
            y=chart_df["SYMBOL"],
            orientation="h",
            marker_color=colors,
            text=[
                f"{value:+.2f}%"
                for value in chart_df["PRICE_CHANGE_PCT"]
            ],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b>"
                "<br>Change: %{x:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=450,
        margin=dict(
            l=70,
            r=70,
            t=15,
            b=10,
        ),

        # Let Streamlit/Plotly follow the selected theme
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        xaxis=dict(
            title="Price change %",
            zeroline=True,
            zerolinecolor="#9ca3af",
            gridcolor="#e5e7eb",
        ),

        yaxis=dict(
            title=None,
            categoryorder="array",
            categoryarray=chart_df["SYMBOL"].tolist(),
        ),

        font=dict(
            family="Inter, Arial, sans-serif",
        ),

        showlegend=False,
    )

    return fig

def get_market_status():
    try:
        return cached_query(MARKET_STATUS)
    except Exception:
        return pd.DataFrame()


def status_text(df):
    """
    FACT_MARKET_STATUS schema is allowed to evolve.
    We detect likely status columns instead of inventing values.
    """

    if df.empty:
        return "Unavailable"

    possible_columns = [
        "STATUS",
        "MARKET_STATUS",
        "SESSION_STATUS",
        "STATE",
        "MARKET_STATE",
    ]

    for column in possible_columns:
        if column in df.columns:
            value = df.iloc[0][column]

            if pd.notna(value):
                return str(value).upper()

    return "Available"


# ============================================================
# DATA LOAD
# ============================================================

try:
    overview = cached_query(OVERVIEW_KPIS)
    market = cached_query(MARKET_MOVERS)
    stocks = cached_query(STOCK_LIST)
    market_status = get_market_status()

    connection_ok = True

except Exception as error:
    connection_ok = False

    st.error(
        "Snowflake connection/query error. "
        "Check the dashboard connection and Gold tables."
    )

    st.exception(error)
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-top">
            <div class="sidebar-logo">F</div>
            <div>
                <div class="sidebar-brand">FINHUB</div>
                <div class="sidebar-subtitle">MARKET INTELLIGENCE</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section-title">OVERVIEW</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Stocks",
            "Earnings & Events",
            "News Intelligence",
            "Crypto",
            "Forex",
        ],
        format_func=lambda x: {
            "Executive Overview": "◈  Executive Overview",
            "Stocks": "◉  Stocks",
            "Earnings & Events": "▣  Earnings & Events",
            "News Intelligence": "◌  News Intelligence",
            "Crypto": "₿  Crypto",
            "Forex": "↔  Forex",
        }[x],
        label_visibility="collapsed",
    )

    st.markdown(
        "<div class='sidebar-spacer'></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section-title">SYSTEM</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "↻  Refresh Dashboard",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.markdown(
        """
        <div class="sidebar-footer">
            <div class="sidebar-footer-title">FINHUB</div>
            <div class="sidebar-footer-text">
                Market intelligence workspace
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns(
    [5, 1],
    vertical_alignment="center",
)

with header_left:
    st.markdown(
        '<div class="dashboard-title">FINHUB</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        "Market Intelligence & Business Analytics"
        "</div>",
        unsafe_allow_html=True,
    )

with header_right:
    if connection_ok:
        st.markdown(
            '<div class="connected-box">● DATA CONNECTED</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# KPI STRIP
# ============================================================

if not overview.empty:

    stocks_covered = int(
        overview.iloc[0]["STOCKS_COVERED"]
    )

    market_points = int(
        overview.iloc[0]["MARKET_DATA_POINTS"]
    )

    news_articles = int(
        overview.iloc[0]["NEWS_ARTICLES"]
    )

    crypto_assets = int(
        overview.iloc[0]["CRYPTO_ASSETS"]
    )

    forex_pairs = int(
        overview.iloc[0]["FOREX_PAIRS"]
    )

else:
    stocks_covered = 0
    market_points = 0
    news_articles = 0
    crypto_assets = 0
    forex_pairs = 0


st.markdown("")

st.markdown("")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric(
        "STOCKS COVERED",
        compact_number(stocks_covered),
    )

with k2:
    st.metric(
        "MARKET QUOTES",
        compact_number(market_points),
    )

with k3:
    st.metric(
        "NEWS ARTICLES",
        compact_number(news_articles),
    )

with k4:
    st.metric(
        "CRYPTO ASSETS",
        compact_number(crypto_assets),
    )

with k5:
    st.metric(
        "FOREX PAIRS",
        compact_number(forex_pairs),
    )

# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    # --------------------------------------------------------
    # MARKET STATUS
    # --------------------------------------------------------

    section(
        "Market Status",
        "Current market session information available from the Gold layer.",
    )

    status_col, summary_col, timestamp_col = st.columns(3)

    current_status = status_text(market_status)

    with status_col:
        st.metric(
            "US MARKET",
            current_status,
        )

    with summary_col:
        if not market.empty:
            positive = int(
                (
                    pd.to_numeric(
                        market["PRICE_CHANGE_PCT"],
                        errors="coerce",
                    )
                    > 0
                ).sum()
            )

            negative = int(
                (
                    pd.to_numeric(
                        market["PRICE_CHANGE_PCT"],
                        errors="coerce",
                    )
                    < 0
                ).sum()
            )

            flat = int(
                (
                    pd.to_numeric(
                        market["PRICE_CHANGE_PCT"],
                        errors="coerce",
                    )
                    == 0
                ).sum()
            )

            st.markdown(
                f"""
                <div class="market-direction-kpi">
                    <div class="kpi-label">MARKET DIRECTION</div>
                    <div class="kpi-value">
                        <span class="market-up">{positive} ↑</span>
                        <span class="market-separator"> / </span>
                        <span class="market-down">{negative} ↓</span>
                    </div>
                    <div class="kpi-description">{flat} flat</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.metric(
                "MARKET DIRECTION",
                "—",
            )

    with timestamp_col:

        if (
            not market.empty
            and "QUOTE_TIMESTAMP" in market.columns
        ):

            latest_timestamp = pd.to_datetime(
                market["QUOTE_TIMESTAMP"],
                errors="coerce",
            ).max()

            if pd.notna(latest_timestamp):
                timestamp_value = latest_timestamp.strftime(
                    "%d %b %Y, %H:%M"
                )
            else:
                timestamp_value = "—"
        else:
            timestamp_value = "—"

        st.metric(
            "LATEST MARKET DATA",
            timestamp_value,
        )

    # --------------------------------------------------------
    # MARKET PULSE
    # --------------------------------------------------------

    section(
        "Market Pulse",
        "Latest available quote per symbol, separated into positive and negative movers.",
    )

    pulse_df = latest_per_symbol(market)

    if not pulse_df.empty:

        pulse_df["PRICE_CHANGE_PCT"] = pd.to_numeric(
            pulse_df["PRICE_CHANGE_PCT"],
            errors="coerce",
        )

        pulse_df["CURRENT_PRICE"] = pd.to_numeric(
            pulse_df["CURRENT_PRICE"],
            errors="coerce",
        )

        pulse_df = pulse_df.dropna(
            subset=["PRICE_CHANGE_PCT"]
        )

        gainers = (
            pulse_df
            .sort_values(
                "PRICE_CHANGE_PCT",
                ascending=False,
            )
            .head(5)
            .copy()
        )

        losers = (
            pulse_df
            .sort_values(
                "PRICE_CHANGE_PCT",
                ascending=True,
            )
            .head(5)
            .copy()
        )

        gainers = gainers[
            [
                "SYMBOL",
                "CURRENT_PRICE",
                "PRICE_CHANGE_PCT",
            ]
        ]

        losers = losers[
            [
                "SYMBOL",
                "CURRENT_PRICE",
                "PRICE_CHANGE_PCT",
            ]
        ]

        gainers.columns = [
            "Symbol",
            "Price",
            "Change %",
        ]

        losers.columns = [
            "Symbol",
            "Price",
            "Change %",
        ]

        gain_col, loss_col = st.columns(2)

        with gain_col:

            st.markdown("**TOP GAINERS**")

            styled_gainers = (
                gainers.style
                .format(
                    {
                        "Price": "${:,.2f}",
                        "Change %": "{:+.2f}%",
                    }
                )
                .map(
                    lambda value:
                    "color: #15803d; font-weight: 700;"
                    if isinstance(value, (int, float))
                    and value > 0
                    else "",
                    subset=["Change %"],
                )
            )

            st.dataframe(
                styled_gainers,
                use_container_width=True,
                hide_index=True,
                height=225,
            )

        with loss_col:

            st.markdown("**TOP LOSERS**")

            styled_losers = (
                losers.style
                .format(
                    {
                        "Price": "${:,.2f}",
                        "Change %": "{:+.2f}%",
                    }
                )
                .map(
                    lambda value:
                    "color: #dc2626; font-weight: 700;"
                    if isinstance(value, (int, float))
                    and value < 0
                    else "",
                    subset=["Change %"],
                )
            )

            st.dataframe(
                styled_losers,
                use_container_width=True,
                hide_index=True,
                height=225,
            )

    else:
        st.info("No market movement data available.")

    # --------------------------------------------------------
    # UNUSUAL PRICE ACTIVITY
    # --------------------------------------------------------

    section(
        "Unusual Price Activity",
        "Symbols showing the largest absolute price movement and intraday range in the available market data.",
    )

    if not pulse_df.empty:

        activity = pulse_df.copy()

        activity["PRICE_CHANGE_PCT"] = pd.to_numeric(
            activity["PRICE_CHANGE_PCT"],
            errors="coerce",
        )

        activity["INTRADAY_RANGE"] = pd.to_numeric(
            activity["INTRADAY_RANGE"],
            errors="coerce",
        )

        activity["ABS_MOVE"] = (
            activity["PRICE_CHANGE_PCT"].abs()
        )

        activity = (
            activity
            .sort_values(
                "ABS_MOVE",
                ascending=False,
            )
            .head(10)
        )

        activity_display = activity[
            [
                "SYMBOL",
                "CURRENT_PRICE",
                "PRICE_CHANGE_PCT",
                "INTRADAY_RANGE",
            ]
        ].copy()

        activity_display.columns = [
            "Symbol",
            "Price",
            "Change %",
            "Intraday Range",
        ]

        styled_activity = (
            activity_display.style
            .format(
                {
                    "Price": "${:,.2f}",
                    "Change %": "{:+.2f}%",
                    "Intraday Range": "${:,.2f}",
                }
            )
            .map(
                lambda value:
                "color: #15803d; font-weight: 700;"
                if isinstance(value, (int, float))
                and value > 0
                else (
                    "color: #dc2626; font-weight: 700;"
                    if isinstance(value, (int, float))
                    and value < 0
                    else ""
                ),
                subset=["Change %"],
            )
        )

        st.dataframe(
            styled_activity,
            use_container_width=True,
            hide_index=True,
            height=350,
        )

    else:
        st.info("No price activity data available.")

    # --------------------------------------------------------
    # PRICE MOVEMENT
    # --------------------------------------------------------

    section(
        "Price Movement",
        "Latest price movement across the available stock universe.",
    )

    if not pulse_df.empty:

        chart_data = (
            pulse_df
            .sort_values(
                "PRICE_CHANGE_PCT",
                key=lambda x: x.abs(),
                ascending=False,
            )
            .head(15)
        )

        movement_chart = create_movement_chart(
            chart_data
        )

        if movement_chart:
            st.plotly_chart(
                movement_chart,
                use_container_width=True,
            )

    # --------------------------------------------------------
    # MARKET SUMMARY
    # --------------------------------------------------------

    section(
        "Market Summary",
        "Snapshot of the current direction of the latest available quotes.",
    )

    if not pulse_df.empty:

        changes = pd.to_numeric(
            pulse_df["PRICE_CHANGE_PCT"],
            errors="coerce",
        ).dropna()

        positive_count = int(
            (changes > 0).sum()
        )

        negative_count = int(
            (changes < 0).sum()
        )

        flat_count = int(
            (changes == 0).sum()
        )

        largest_move = (
            changes.abs().max()
            if not changes.empty
            else None
        )

        s1, s2, s3, s4 = st.columns(4)

        with s1:
            st.metric(
                "POSITIVE",
                positive_count,
            )

        with s2:
            st.metric(
                "NEGATIVE",
                negative_count,
            )

        with s3:
            st.metric(
                "FLAT",
                flat_count,
            )

        with s4:
            st.metric(
                "LARGEST MOVE",
                clean_percent(largest_move),
            )

    # --------------------------------------------------------
    # MARKET DATA TABLE
    # --------------------------------------------------------

    with st.expander(
        "View latest market data",
        expanded=False,
    ):

        if not pulse_df.empty:

            table = pulse_df[
                [
                    "SYMBOL",
                    "CURRENT_PRICE",
                    "PRICE_CHANGE",
                    "PRICE_CHANGE_PCT",
                    "HIGH_PRICE",
                    "LOW_PRICE",
                    "OPEN_PRICE",
                    "PREVIOUS_CLOSE",
                    "INTRADAY_RANGE",
                    "QUOTE_TIMESTAMP",
                ]
            ].copy()

            table.columns = [
                "Symbol",
                "Price",
                "Change",
                "Change %",
                "High",
                "Low",
                "Open",
                "Previous Close",
                "Intraday Range",
                "Quote Timestamp",
            ]

            styled_table = (
                table.style
                .format(
                    {
                        "Price": "${:,.2f}",
                        "Change": "${:+,.2f}",
                        "Change %": "{:+.2f}%",
                        "High": "${:,.2f}",
                        "Low": "${:,.2f}",
                        "Open": "${:,.2f}",
                        "Previous Close": "${:,.2f}",
                        "Intraday Range": "${:,.2f}",
                    },
                    na_rep="—",
                )
                .map(
                    lambda value:
                    "color: #15803d; font-weight: 700;"
                    if isinstance(value, (int, float))
                    and value > 0
                    else (
                        "color: #dc2626; font-weight: 700;"
                        if isinstance(value, (int, float))
                        and value < 0
                        else ""
                    ),
                    subset=[
                        "Change",
                        "Change %",
                    ],
                )
            )

            st.dataframe(
                styled_table,
                use_container_width=True,
                hide_index=True,
                height=450,
            )


# ============================================================
# STOCKS
# ============================================================

elif page == "Stocks":

    section(
        "Stock Intelligence",
        "Detailed company, market, historical price, peer and earnings intelligence.",
    )

    if stocks.empty:
        st.warning("No stock universe available.")
        st.stop()

    stock_symbols = stocks["SYMBOL"].dropna().tolist()

    selected_symbol = st.selectbox(
        "Select security",
        stock_symbols,
        index=0,
    )

    detail = cached_query(
        STOCK_DETAIL,
        [selected_symbol],
    )

    if detail.empty:
        st.warning(
            f"No detailed market information available for {selected_symbol}."
        )
        st.stop()

    row = detail.iloc[0]

    st.markdown("")

    st.subheader(
        str(row.get("COMPANY_NAME", selected_symbol))
    )

    st.caption(
        f"{selected_symbol} · "
        f"{row.get('EXCHANGE', '—')} · "
        f"{row.get('INDUSTRY', '—')}"
    )

    current_price = row.get("CURRENT_PRICE")
    price_change = row.get("PRICE_CHANGE")
    price_change_pct = row.get("PRICE_CHANGE_PCT")

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric(
            "CURRENT PRICE",
            (
                f"${float(current_price):,.2f}"
                if pd.notna(current_price)
                else "—"
            ),
        )

    with m2:
        st.metric(
            "CHANGE",
            (
                f"${float(price_change):+,.2f}"
                if pd.notna(price_change)
                else "—"
            ),
        )

    with m3:
        st.metric(
            "CHANGE %",
            (
                f"{float(price_change_pct):+.2f}%"
                if pd.notna(price_change_pct)
                else "—"
            ),
        )

    with m4:
        st.metric(
            "DAY HIGH",
            (
                f"${float(row['HIGH_PRICE']):,.2f}"
                if pd.notna(row["HIGH_PRICE"])
                else "—"
            ),
        )

    with m5:
        st.metric(
            "DAY LOW",
            (
                f"${float(row['LOW_PRICE']):,.2f}"
                if pd.notna(row["LOW_PRICE"])
                else "—"
            ),
        )

    tabs = st.tabs(
        [
            "Price History",
            "Company",
            "Peers",
            "News",
            "Earnings",
        ]
    )

    # --------------------------------------------------------
    # PRICE HISTORY
    # --------------------------------------------------------

    with tabs[0]:

        history = cached_query(
            STOCK_PRICE_HISTORY,
            [selected_symbol],
        )

        if history.empty:
            st.info(
                "No historical market data available."
            )
        else:

            chart = create_price_chart(
                history,
                selected_symbol,
            )

            if chart:
                chart.update_layout(
                    template="plotly_white",
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    font=dict(
                        family="Inter, Arial, sans-serif",
                        color="#111827",
                    ),
                    xaxis=dict(
                        tickfont=dict(
                            color="#111827",
                        ),
                    ),
                    yaxis=dict(
                        tickfont=dict(
                            color="#111827",
                        ),
                    ),
                    legend=dict(
                        font=dict(
                            color="#111827",
                        ),
                    ),
                )

                st.plotly_chart(
                    chart,
                    use_container_width=True,
                )

            display_history = history.copy()

            display_history["QUOTE_TIMESTAMP"] = pd.to_datetime(
                display_history["QUOTE_TIMESTAMP"],
                errors="coerce",
            )

            display_history = display_history.sort_values(
                "QUOTE_TIMESTAMP",
                ascending=False,
            )

            display_history = display_history[
                [
                    "QUOTE_DATE",
                    "CURRENT_PRICE",
                    "PRICE_CHANGE",
                    "PRICE_CHANGE_PCT",
                    "OPEN_PRICE",
                    "HIGH_PRICE",
                    "LOW_PRICE",
                    "PREVIOUS_CLOSE",
                    "INTRADAY_RANGE",
                ]
            ]

            display_history.columns = [
                "Date",
                "Price",
                "Change",
                "Change %",
                "Open",
                "High",
                "Low",
                "Previous Close",
                "Intraday Range",
            ]

            styled_history = (
                display_history.style
                .format(
                    {
                        "Price": "${:,.2f}",
                        "Change": "${:+,.2f}",
                        "Change %": "{:+.2f}%",
                        "Open": "${:,.2f}",
                        "High": "${:,.2f}",
                        "Low": "${:,.2f}",
                        "Previous Close": "${:,.2f}",
                        "Intraday Range": "${:,.2f}",
                    },
                    na_rep="—",
                )
                .map(
                    lambda value:
                    "color: #15803d; font-weight: 700;"
                    if isinstance(value, (int, float))
                    and value > 0
                    else (
                        "color: #dc2626; font-weight: 700;"
                        if isinstance(value, (int, float))
                        and value < 0
                        else ""
                    ),
                    subset=[
                        "Change",
                        "Change %",
                    ],
                )
            )

            st.dataframe(
                styled_history,
                use_container_width=True,
                hide_index=True,
                height=400,
            )

    # --------------------------------------------------------
    # COMPANY
    # --------------------------------------------------------

    with tabs[1]:

        c1, c2 = st.columns(2)

        with c1:
            st.write("**Company**")
            st.write(
                row.get("COMPANY_NAME", "—")
            )

            st.write("**Industry**")
            st.write(
                row.get("INDUSTRY", "—")
            )

            st.write("**Country**")
            st.write(
                row.get("COUNTRY", "—")
            )

        with c2:
            st.write("**Exchange**")
            st.write(
                row.get("EXCHANGE", "—")
            )

            st.write("**Currency**")
            st.write(
                row.get("CURRENCY", "—")
            )

            st.write("**Previous Close**")
            previous_close = row.get(
                "PREVIOUS_CLOSE"
            )

            if pd.notna(previous_close):
                st.write(
                    f"${float(previous_close):,.2f}"
                )
            else:
                st.write("—")

    # --------------------------------------------------------
    # PEERS
    # --------------------------------------------------------

    with tabs[2]:

        peers = cached_query(
            STOCK_PEERS,
            [selected_symbol],
        )

        if peers.empty:
            st.info(
                "No peer market data available."
            )
        else:

            peers = peers.copy()

            peers["CURRENT_PRICE"] = pd.to_numeric(
                peers["CURRENT_PRICE"],
                errors="coerce",
            )

            peers["PRICE_CHANGE_PCT"] = pd.to_numeric(
                peers["PRICE_CHANGE_PCT"],
                errors="coerce",
            )

            peer_display = peers[
                [
                    "STOCK_SYMBOL",
                    "PEER_SYMBOL",
                    "CURRENT_PRICE",
                    "PRICE_CHANGE_PCT",
                ]
            ].copy()

            peer_display.columns = [
                "Selected Stock",
                "Peer",
                "Price",
                "Change %",
            ]

            styled_peers = (
                peer_display.style
                .format(
                    {
                        "Price": "${:,.2f}",
                        "Change %": "{:+.2f}%",
                    },
                    na_rep="—",
                )
                .map(
                    lambda value:
                    "color: #15803d; font-weight: 700;"
                    if isinstance(value, (int, float))
                    and value > 0
                    else (
                        "color: #dc2626; font-weight: 700;"
                        if isinstance(value, (int, float))
                        and value < 0
                        else ""
                    ),
                    subset=["Change %"],
                )
            )

            st.dataframe(
                styled_peers,
                use_container_width=True,
                hide_index=True,
                height=400,
            )

    # --------------------------------------------------------
    # STOCK NEWS
    # --------------------------------------------------------

    with tabs[3]:

        news = cached_query(
            STOCK_NEWS,
            [selected_symbol],
        )

        if news.empty:
            st.info(
                "No recent news available."
            )
        else:

            for _, news_row in news.iterrows():

                headline = news_row.get(
                    "HEADLINE",
                    "Untitled",
                )

                source = news_row.get(
                    "SOURCE",
                    "Unknown source",
                )

                timestamp = news_row.get(
                    "NEWS_TIMESTAMP",
                    "",
                )

                left, right = st.columns([5, 1])

                with left:
                    st.markdown(f"**{headline}**")
                    st.caption(f"{source} · {timestamp}")

                with right:
                    news_url = news_row.get("NEWS_URL", None)

                    if pd.notna(news_url) and news_url:
                        st.link_button(
                            "Read Article",
                            str(news_url),
                            use_container_width=True,
                        )

                st.divider()
                
                

                

    # --------------------------------------------------------
    # EARNINGS
    # --------------------------------------------------------

    with tabs[4]:

        earnings = cached_query(
            STOCK_EARNINGS,
            [selected_symbol],
        )

        if earnings.empty:
            st.info(
                "No earnings history available."
            )
        else:

            earnings_display = earnings.copy()

            earnings_display.columns = [
                column.replace(
                    "_",
                    " "
                ).title()
                for column in earnings_display.columns
            ]

            st.dataframe(
                earnings_display,
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# EARNINGS & EVENTS
# ============================================================

elif page == "Earnings & Events":

    st.title("Earnings & Events")

    st.caption(
        "Corporate earnings and upcoming market events from the Gold layer."
    )

    earnings_tab, ipo_tab, holiday_tab = st.tabs(
        [
            "Earnings Calendar",
            "IPO Calendar",
            "Market Holidays",
        ]
    )

    with earnings_tab:

        earnings = cached_query(
            EARNINGS_CALENDAR
        )

        if earnings.empty:
            st.info(
                "No earnings calendar data available."
            )
        else:

            st.dataframe(
                earnings,
                use_container_width=True,
                hide_index=True,
                height=600,
            )

    with ipo_tab:

        ipo = cached_query(
            IPO_CALENDAR
        )

        if ipo.empty:
            st.info(
                "No IPO calendar data available."
            )
        else:

            st.dataframe(
                ipo,
                use_container_width=True,
                hide_index=True,
                height=600,
            )

    with holiday_tab:

        holidays = cached_query(
            MARKET_HOLIDAYS
        )

        if holidays.empty:
            st.info(
                "No market holiday data available."
            )
        else:

            st.dataframe(
                holidays,
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# NEWS INTELLIGENCE
# ============================================================

elif page == "News Intelligence":

    st.title("News Intelligence")

    st.caption(
        "Latest market news captured by the FINHUB pipeline."
    )

    news_filter = st.text_input(
        "Filter by symbol",
        placeholder="e.g. AAPL, MSFT, NVDA",
    ).strip().upper()

    if news_filter:

        news = cached_query(
            NEWS_BY_SYMBOL,
            [news_filter],
        )

    else:

        news = cached_query(
            LATEST_NEWS
        )

    if news.empty:

        st.info(
            "No news available for the selected filter."
        )

    else:

        news = news.copy()

        for _, row in news.iterrows():

            symbol = row.get(
                "SYMBOL",
                "",
            )

            headline = row.get(
                "HEADLINE",
                "Untitled",
            )

            source = row.get(
                "SOURCE",
                "Unknown source",
            )

            timestamp = row.get(
                "NEWS_TIMESTAMP",
                "",
            )

            url = row.get(
                "NEWS_URL",
                None,
            )

            left, right = st.columns(
                [5, 1]
            )

            with left:

                st.markdown(
                    f"**{headline}**"
                )

                st.caption(
                    f"{symbol} · {source} · {timestamp}"
                )

            with right:

                if pd.notna(url) and url:

                    st.link_button(
                        "Read",
                        str(url),
                        use_container_width=True,
                    )

            st.divider()


# ============================================================
# CRYPTO
# ============================================================

elif page == "Crypto":

    st.title("Crypto Intelligence")

    st.caption(
        "Crypto asset and exchange coverage available in the Gold layer."
    )

    crypto_overview = cached_query(
        CRYPTO_OVERVIEW
    )

    exchanges = cached_query(
        CRYPTO_EXCHANGES
    )

    crypto_assets = cached_query(
        CRYPTO_ASSETS
    )

    total_crypto = 0

    if not crypto_overview.empty:

        total_crypto = int(
            crypto_overview.iloc[0][
                "TOTAL_CRYPTO_ASSETS"
            ]
        )

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "CRYPTO ASSETS",
            compact_number(total_crypto),
        )

    with c2:
        st.metric(
            "EXCHANGES",
            len(exchanges),
        )

    assets_tab, exchange_tab = st.tabs(
        [
            "Assets",
            "Exchanges",
        ]
    )

    with assets_tab:

        if crypto_assets.empty:
            st.info(
                "No crypto assets available."
            )
        else:

            st.dataframe(
                crypto_assets,
                use_container_width=True,
                hide_index=True,
                height=600,
            )

    with exchange_tab:

        if exchanges.empty:
            st.info(
                "No crypto exchanges available."
            )
        else:

            st.dataframe(
                exchanges,
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# FOREX
# ============================================================

elif page == "Forex":

    st.title("Forex Intelligence")

    st.caption(
        "Foreign exchange coverage available in the Gold layer."
    )

    forex = cached_query(
        FOREX_PAIRS
    )

    if forex.empty:

        st.warning(
            "No forex pairs are currently available in the Gold layer."
        )

    else:

        st.metric(
            "FOREX PAIRS",
            len(forex),
        )

        st.dataframe(
            forex,
            use_container_width=True,
            hide_index=True,
            height=650,
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

footer_left, footer_right = st.columns(
    [4, 1]
)

with footer_left:
    st.caption(
        "FINHUB Market Intelligence · Snowflake Gold Layer · Finnhub Data Pipeline"
    )

with footer_right:
    st.caption(
        "Management BI Dashboard"
    )