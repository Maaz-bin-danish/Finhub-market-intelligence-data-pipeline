import streamlit as st


def load_styles():
    st.markdown(
        """
        <style>

        .dashboard-title {
            margin-top: 0;
            margin-bottom: 0.1rem;
            color: var(--text-color);
            font-size: 2.2rem;
            line-height: 1.05;
            font-weight: 800;
            letter-spacing: -0.045em;
        }

        .dashboard-subtitle {
            color: #6b7280;
            font-size: 0.88rem;
            font-weight: 500;
            margin-bottom: 1.6rem;
            letter-spacing: 0.01em;
        }

        /* =====================================================
           GLOBAL
        ===================================================== */

        .stApp {
            background: #f5f7fa;
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }


        /* =====================================================
           HEADER
           ===================================================== */

        .finhub-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .finhub-main-title {
            margin-top: 0;
            margin-bottom: 0.1rem;
            color: var(--text-color);
            font-size: 2.2rem;
            line-height: 1.05;
            font-weight: 800;
            letter-spacing: -0.045em;
        }

        .finhub-main-subtitle {
            color: var(--secondary-text-color);
            font-size: 0.88rem;
            font-weight: 500;
            margin-bottom: 1.6rem;
            letter-spacing: 0.01em;
        }

        .finhub-status {
            text-align: right;
            color: #6b7280;
            font-size: 0.78rem;
            line-height: 1.5;
        }

        /* =====================================================
           KPI CARDS
           ===================================================== */

        .kpi-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.1rem 1.2rem;
            min-height: 115px;
            box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
        }

        .kpi-label {
            color: #6b7280;
            font-size: 0.72rem;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: 0.45px;
        }

        .kpi-value {
            color: #111827;
            font-size: 1.8rem;
            font-weight: 750;
            margin-top: 7px;
            line-height: 1;
        }

        .kpi-description {
            color: #9ca3af;
            font-size: 0.72rem;
            margin-top: 7px;
        }

        /* =====================================================
           SECTION
           ===================================================== */

        .section-title {
            color: #111827;
            font-size: 1.15rem;
            font-weight: 700;
            margin-top: 1.4rem;
            margin-bottom: 2px;
        }

        .section-description {
            color: #6b7280;
            font-size: 0.82rem;
            margin-bottom: 0.75rem;
        }

        /* =====================================================
           SIGNALS
           ===================================================== */

        .signal-up {
            color: #16a34a;
            font-weight: 700;
        }

        .signal-down {
            color: #dc2626;
            font-weight: 700;
        }

        .signal-neutral {
            color: #6b7280;
            font-weight: 700;
        }

        /* =====================================================
           INFO CARD
           ===================================================== */

        .info-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem 1.15rem;
            box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
        }

        /* =====================================================
           TABLE
           ===================================================== */

        div[data-testid="stDataFrame"] {
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
        }

        /* =====================================================
           INPUTS
           ===================================================== */

        div[data-baseweb="select"] > div {
            border-radius: 8px;
        }

        .stTextInput input {
            border-radius: 8px;
        }

        /* =====================================================
           BUTTON
           ===================================================== */

        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
        }

        /* =====================================================
           HIDE STREAMLIT DEFAULT UI
           ===================================================== */

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }


        /* ============================================================
        SIDEBAR — FINHUB
        ============================================================ */

        [data-testid="stSidebar"] {
            background-color: #111827 !important;
        }

        [data-testid="stSidebar"] > div {
            background-color: #111827 !important;
        }

        [data-testid="stSidebar"] > div > div {
            background-color: #111827 !important;
        }

        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background-color: #111827 !important;
        }

        [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            background-color: #111827 !important;
            padding: 1.4rem 1rem 1rem 1rem;
        }


        /* ---------- BRAND ---------- */

        .sidebar-top {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.2rem 0.3rem 1.8rem 0.3rem;
        }

        .sidebar-logo {
            width: 40px;
            height: 40px;
            min-width: 40px;
            border-radius: 11px;
            background: #ffffff;
            color: #111827;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            font-weight: 800;
        }

        .sidebar-brand {
            color: #ffffff !important;
            font-size: 1.3rem;
            font-weight: 800;
            line-height: 1;
            letter-spacing: -0.04em;
        }

        .sidebar-subtitle {
            color: #7c8797 !important;
            font-size: 0.56rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            margin-top: 4px;
        }


        /* ---------- SECTION LABEL ---------- */

        .sidebar-section-title {
            color: #647184 !important;
            font-size: 0.6rem;
            font-weight: 750;
            letter-spacing: 0.15em;
            margin: 0 0 0.55rem 0.3rem;
        }


        /* ---------- NAVIGATION ---------- */

        [data-testid="stSidebar"] [data-testid="stRadio"] > label {
            display: none !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
            width: 100%;
            box-sizing: border-box;
            background: transparent !important;
            border: 1px solid transparent !important;
            border-radius: 9px !important;
            padding: 0.7rem 0.8rem !important;
            margin: 0 !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background: #1b2532 !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p {
            color: #aeb8c6 !important;
            font-size: 0.83rem !important;
            font-weight: 550 !important;
            margin: 0 !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
            background: #ffffff !important;
            border-color: #ffffff !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {
            color: #111827 !important;
            font-weight: 700 !important;
        }


        /* ---------- SPACING ---------- */

        .sidebar-spacer {
            height: 1.6rem;
        }


        /* ---------- REFRESH ---------- */

        [data-testid="stSidebar"] .stButton {
            width: 100%;
        }

        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            background: #182230 !important;
            color: #cbd5e1 !important;
            border: 1px solid #2a3747 !important;
            border-radius: 9px !important;
            padding: 0.6rem 0.75rem !important;
            font-size: 0.78rem !important;
            font-weight: 650 !important;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: #202c3a !important;
            color: #ffffff !important;
            border-color: #3a4859 !important;
        }


        /* ---------- FOOTER ---------- */

        .sidebar-footer {
            margin-top: 1.5rem;
            padding: 0.85rem 0.9rem;
            background: #151e29;
            border: 1px solid #263342;
            border-radius: 9px;
        }

        .sidebar-footer-title {
            color: #dbe3ec !important;
            font-size: 0.7rem;
            font-weight: 700;
        }

        .sidebar-footer-text {
            color: #697789 !important;
            font-size: 0.61rem;
            margin-top: 3px;
        }

        .market-up {
            color: #16a34a;
            font-weight: 750;
        }

        .market-down {
            color: #dc2626;
            font-weight: 750;
        }

        .market-separator {
            color: #9ca3af;
            font-weight: 500;
        }

        </style>
                """,
        unsafe_allow_html=True,
    )


def render_kpi(label, value, description=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(title, description=""):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-description">{description}</div>
        """,
        unsafe_allow_html=True,
    )


def render_signal(value):
    """
    Return a visual market movement signal.
    """

    if value is None:
        return '<span class="signal-neutral">—</span>'

    try:
        value = float(value)
    except (TypeError, ValueError):
        return '<span class="signal-neutral">—</span>'

    if value > 0:
        return (
            f'<span class="signal-up">'
            f'↑ {value:.2f}%'
            f'</span>'
        )

    if value < 0:
        return (
            f'<span class="signal-down">'
            f'↓ {abs(value):.2f}%'
            f'</span>'
        )

    return '<span class="signal-neutral">→ 0.00%</span>'

