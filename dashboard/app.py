import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import streamlit as st
from run_pipeline import run

st.set_page_config(layout="wide")
st.title("Insider Threat Detection – SOC Dashboard")

df = run()

c1, c2, c3 = st.columns(3)
c1.metric("Employees", len(df))
c2.metric("High Risk", len(df[df["risk_score"] > 1.2]))
c3.metric("Max Risk", round(df["risk_score"].max(), 2))

st.subheader("Alerts")
st.dataframe(
    df[df["risk_score"] > 1.2][
        ["user_id", "risk_score", "if_score", "svm_score"]
    ]
)

st.subheader("Risk Distribution")
st.bar_chart(df.set_index("user_id")["risk_score"])
