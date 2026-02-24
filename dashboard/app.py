import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from config import SCORED_CSV, OUTPUT_DIR
from src.scoring.risk_score import risk_breakdown
from src.utils.logger import get_logger

logger = get_logger("insider_threat.dashboard")

st.set_page_config(
    page_title="Insider Threat Detection SOC",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetric"] label {
        color: #a0aec0 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #e2e8f0 !important;
    }

    .section-header {
        color: #e2e8f0;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #0f3460;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .risk-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .risk-critical { background: #e53e3e22; color: #fc8181; border: 1px solid #e53e3e; }
    .risk-high     { background: #dd6b2022; color: #fbd38d; border: 1px solid #dd6b20; }
    .risk-medium   { background: #d6990022; color: #fefcbf; border: 1px solid #d69e2e; }
    .risk-low      { background: #38a16922; color: #9ae6b4; border: 1px solid #38a169; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h1 {
        color: #58a6ff;
        font-size: 1.1rem;
    }

    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }

    .dashboard-title {
        background: linear-gradient(135deg, #0f3460 0%, #533483 50%, #e94560 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0;
    }
    .dashboard-subtitle {
        color: #718096;
        font-size: 0.95rem;
        margin-top: -8px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    if SCORED_CSV.exists():
        logger.info("Dashboard: loading pre-computed scores from %s", SCORED_CSV)
        return pd.read_csv(SCORED_CSV)
  
    logger.warning(
        "Dashboard: scored CSV not found at %s — running pipeline now.",
        SCORED_CSV,
    )
    from run_pipeline import run
    df = run()
    logger.info("Dashboard: pipeline fallback complete, %d users scored.", len(df))
    return df

df = load_data()

RISK_COLORS = {
    "Critical": "#e53e3e",
    "High":     "#dd6b20",
    "Medium":   "#d69e2e",
    "Low":      "#38a169",
}

def risk_badge(level):
    css = f"risk-{level.lower()}"
    return f'<span class="risk-badge {css}">{level}</span>'


with st.sidebar:
    st.markdown("# SOC Controls")
    st.markdown("---")

    levels = st.multiselect(
        "Risk Levels",
        options=["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"],
    )

    if "role" in df.columns:
        roles = st.multiselect(
            "Roles",
            options=sorted(df["role"].unique()),
            default=sorted(df["role"].unique()),
        )
    else:
        roles = None

    score_range = st.slider(
        "Risk Score Range",
        min_value=0.0,
        max_value=100.0,
        value=(0.0, 100.0),
        step=1.0,
    )

    st.markdown("---")
    st.markdown("##### Export")
    if st.button("Download Alerts CSV", use_container_width=True):
        alerts = df[df["risk_level"].isin(["Critical", "High"])]
        csv = alerts.to_csv(index=False)
        st.download_button("Download", csv, "threat_alerts.csv", "text/csv", use_container_width=True)

    st.markdown("---")
    st.caption("Insider Threat Detection v2.0")
    st.caption("Powered by IF · SVM · Autoencoder")

filtered = df[
    (df["risk_level"].isin(levels)) &
    (df["risk_score"] >= score_range[0]) &
    (df["risk_score"] <= score_range[1])
]
if roles is not None:
    filtered = filtered[filtered["role"].isin(roles)]

st.markdown('<p class="dashboard-title">Insider Threat Detection</p>', unsafe_allow_html=True)
st.markdown('<p class="dashboard-subtitle">Security Operations Center — Real-time Anomaly Monitoring Dashboard</p>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Employees", len(df))
c2.metric("Critical", len(df[df["risk_level"] == "Critical"]))
c3.metric("High Risk", len(df[df["risk_level"] == "High"]))
c4.metric("Avg Score", f"{df['risk_score'].mean():.1f}")
c5.metric("Max Score", f"{df['risk_score'].max():.1f}")

st.markdown("")

st.markdown('<div class="section-header">Risk Overview</div>', unsafe_allow_html=True)
col1, col2 = st.columns([3, 2])

with col1:
    fig_hist = px.histogram(
        filtered,
        x="risk_score",
        nbins=30,
        color="risk_level",
        color_discrete_map=RISK_COLORS,
        title="Risk Score Distribution",
        labels={"risk_score": "Risk Score", "count": "Users"},
    )
    fig_hist.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        bargap=0.05,
        legend=dict(title="", orientation="h", y=-0.15),
        height=380,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    risk_counts = filtered["risk_level"].value_counts().reset_index()
    risk_counts.columns = ["Risk Level", "Count"]
    fig_pie = px.pie(
        risk_counts,
        values="Count",
        names="Risk Level",
        color="Risk Level",
        color_discrete_map=RISK_COLORS,
        title="Risk Level Breakdown",
        hole=0.45,
    )
    fig_pie.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        height=380,
        legend=dict(orientation="h", y=-0.1),
    )
    fig_pie.update_traces(textinfo="percent+label", textfont_size=12)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown('<div class="section-header">Model Analytics</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)

with col3:
    if "if_score" in filtered.columns and "svm_score" in filtered.columns:
        fig_scatter = px.scatter(
            filtered,
            x="if_score",
            y="svm_score",
            color="risk_level",
            color_discrete_map=RISK_COLORS,
            size="risk_score",
            size_max=18,
            hover_data=["user_id", "risk_score"],
            title="Isolation Forest vs One-Class SVM Scores",
            labels={"if_score": "IF Anomaly Score", "svm_score": "SVM Anomaly Score"},
        )
        fig_scatter.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=400,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

with col4:
    if "role" in filtered.columns:
        cross = pd.crosstab(filtered["role"], filtered["risk_level"])
        for lev in ["Critical", "High", "Medium", "Low"]:
            if lev not in cross.columns:
                cross[lev] = 0
        cross = cross[["Critical", "High", "Medium", "Low"]]

        fig_heat = go.Figure(data=go.Heatmap(
            z=cross.values,
            x=cross.columns.tolist(),
            y=cross.index.tolist(),
            colorscale=[[0, "#0d1117"], [0.5, "#0f3460"], [1, "#e94560"]],
            showscale=True,
            text=cross.values,
            texttemplate="%{text}",
            textfont=dict(size=14, color="white"),
        ))
        fig_heat.update_layout(
            title="Risk Levels by Role",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=400,
            xaxis_title="Risk Level",
            yaxis_title="Role",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

st.markdown('<div class="section-header">Threat Alerts</div>', unsafe_allow_html=True)

display_cols = ["user_id", "risk_score", "risk_level"]
if "role" in filtered.columns:
    display_cols.insert(1, "role")
for extra in ["if_score", "svm_score", "ae_score", "sensitive_total", "failed_total"]:
    if extra in filtered.columns:
        display_cols.append(extra)

alerts_df = filtered[display_cols].copy()
alerts_df["risk_score"] = alerts_df["risk_score"].round(1)
for sc in ["if_score", "svm_score", "ae_score"]:
    if sc in alerts_df.columns:
        alerts_df[sc] = alerts_df[sc].round(3)

st.dataframe(
    alerts_df,
    use_container_width=True,
    height=400,
    column_config={
        "user_id": st.column_config.NumberColumn("User ID", format="%d"),
        "risk_score": st.column_config.ProgressColumn(
            "Risk Score",
            min_value=0,
            max_value=100,
            format="%.1f",
        ),
        "risk_level": st.column_config.TextColumn("Risk Level"),
    },
)

st.markdown('<div class="section-header">User Drilldown</div>', unsafe_allow_html=True)

selected_user = st.selectbox(
    "Select a user to inspect",
    options=sorted(filtered["user_id"].unique()),
    format_func=lambda x: f"User {x}",
)

if selected_user is not None:
    user_row = filtered[filtered["user_id"] == selected_user].iloc[0]

    d1, d2, d3 = st.columns(3)
    with d1:
        level = user_row.get("risk_level", "Unknown")
        st.markdown(f"**Risk Level:** {risk_badge(level)}", unsafe_allow_html=True)
        st.metric("Risk Score", f"{user_row['risk_score']:.1f} / 100")
    with d2:
        if "role" in user_row.index:
            st.metric("Role", user_row["role"].title())
        if "sensitive_total" in user_row.index:
            st.metric("Sensitive File Access", f"{user_row['sensitive_total']:.2f}")
    with d3:
        if "failed_total" in user_row.index:
            st.metric("Failed Login Score", f"{user_row['failed_total']:.2f}")
        if "usb_total" in user_row.index:
            st.metric("USB Activity Score", f"{user_row['usb_total']:.2f}")

    st.markdown("**Risk Factor Breakdown:**")
    breakdown = risk_breakdown(user_row)
    bd_df = pd.DataFrame(list(breakdown.items()), columns=["Factor", "Contribution %"])
    bd_df = bd_df.sort_values("Contribution %", ascending=True)

    fig_bar = px.bar(
        bd_df,
        x="Contribution %",
        y="Factor",
        orientation="h",
        color="Contribution %",
        color_continuous_scale=[[0, "#38a169"], [0.5, "#d69e2e"], [1, "#e53e3e"]],
        title=f"Risk Contribution — User {selected_user}",
    )
    fig_bar.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        height=300,
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    feature_cols_radar = ["login_mean", "login_std", "files_mean", "files_max",
                          "sensitive_total", "failed_total", "emails_mean",
                          "after_hours_mean", "usb_total", "vpn_total"]
    available = [c for c in feature_cols_radar if c in user_row.index]
    if available:
        vals = [float(user_row[c]) for c in available]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=available + [available[0]],
            fill="toself",
            fillcolor="rgba(233, 69, 96, 0.2)",
            line=dict(color="#e94560", width=2),
            name=f"User {selected_user}",
        ))
        fig_radar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=400,
            title=f"Behavioural Profile — User {selected_user}",
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(showticklabels=True, gridcolor="#1a1a2e"),
                angularaxis=dict(gridcolor="#1a1a2e"),
            ),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#4a5568; font-size:0.8rem;">'
    'Insider Threat Detection System v2.0 — '
    'Powered by Isolation Forest · One-Class SVM · Autoencoder'
    '</p>',
    unsafe_allow_html=True,
)
