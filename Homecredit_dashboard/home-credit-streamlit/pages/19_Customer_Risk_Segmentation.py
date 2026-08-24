import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from utils.data_loader import load_application_train, load_bureau
from utils.feature_engineering import engineer_application_features, aggregate_bureau_features
from utils import charts as ch
from utils.metrics import fmt_number, fmt_currency

st.set_page_config(page_title="Customer Risk Segmentation", page_icon="🏦", layout="wide")
st.title("19 · Customer Risk Segmentation Using EDA Rules")
st.caption("Business Objective: build descriptive, rule-based EDA segments. These are NOT model predictions.")

df = engineer_application_features(load_application_train())
bureau_agg = aggregate_bureau_features(load_bureau())
df = df.merge(bureau_agg, on="SK_ID_CURR", how="left")
df["TOTAL_BUREAU_DEBT"] = df["TOTAL_BUREAU_DEBT"].fillna(0)

# --- Rule-based scoring (transparent, documented) ---
score = pd.Series(0, index=df.index)
score += (df["CREDIT_TO_INCOME"] > df["CREDIT_TO_INCOME"].quantile(0.75)).astype(int)
score += (df["ANNUITY_TO_INCOME"] > df["ANNUITY_TO_INCOME"].quantile(0.75)).astype(int)
score += (df["TOTAL_BUREAU_DEBT"] > df["TOTAL_BUREAU_DEBT"].quantile(0.75)).astype(int)
score += (df["EMPLOYMENT_GROUP"].isin(["<1 Year", "Unemployed / Special"])).astype(int)

df["RISK_SCORE"] = score
df["RISK_SEGMENT"] = pd.cut(score, bins=[-1, 0, 1, 2, 4],
                             labels=["Low Observed Risk", "Moderate Observed Risk",
                                     "Elevated Observed Risk", "High Observed Risk"])

st.info("""
**How segments were built (fully rule-based, no model training):** one point is added for each of the following
that is true for a customer — (1) Credit-to-Income ratio above the portfolio's 75th percentile, (2) Annuity-to-
Income ratio above the 75th percentile, (3) Total bureau debt above the 75th percentile, (4) Employment group is
"<1 Year" or "Unemployed / Special". Total points (0-4) map to: 0 → Low, 1 → Moderate, 2 → Elevated, 3-4 → High
Observed Risk.
""")

seg_counts = df["RISK_SEGMENT"].value_counts().reindex(
    ["Low Observed Risk", "Moderate Observed Risk", "Elevated Observed Risk", "High Observed Risk"]
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Low-Risk Customers", fmt_number(seg_counts.get("Low Observed Risk", 0)))
c2.metric("Moderate-Risk Customers", fmt_number(seg_counts.get("Moderate Observed Risk", 0)))
c3.metric("Elevated-Risk Customers", fmt_number(seg_counts.get("Elevated Observed Risk", 0)))
c4.metric("High-Risk Customers", fmt_number(seg_counts.get("High Observed Risk", 0)))
high_exposure = df.loc[df["RISK_SEGMENT"] == "High Observed Risk", "AMT_CREDIT"].sum()
c5.metric("Credit Exposure — High-Risk Segment", fmt_currency(high_exposure))

st.divider()
col1, col2 = st.columns(2)
with col1:
    sc = seg_counts.reset_index()
    sc.columns = ["Segment", "Count"]
    st.plotly_chart(ch.bar(sc, "Segment", "Count", "Customer Count by Risk Segment"), use_container_width=True)
with col2:
    exposure = df.groupby("RISK_SEGMENT", observed=True)["AMT_CREDIT"].sum().reset_index()
    st.plotly_chart(ch.donut(exposure, "RISK_SEGMENT", "AMT_CREDIT", "Portfolio Exposure by Segment"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    avg_income = df.groupby("RISK_SEGMENT", observed=True)["AMT_INCOME_TOTAL"].mean().reset_index()
    st.plotly_chart(ch.bar(avg_income, "RISK_SEGMENT", "AMT_INCOME_TOTAL", "Average Income by Segment"), use_container_width=True)
with col4:
    avg_credit = df.groupby("RISK_SEGMENT", observed=True)["AMT_CREDIT"].mean().reset_index()
    st.plotly_chart(ch.bar(avg_credit, "RISK_SEGMENT", "AMT_CREDIT", "Average Credit by Segment"), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    st.plotly_chart(ch.box(df, x="RISK_SEGMENT", y="CREDIT_TO_INCOME", title="Credit-to-Income by Segment"), use_container_width=True)
with col6:
    bureau_debt_seg = df.groupby("RISK_SEGMENT", observed=True)["TOTAL_BUREAU_DEBT"].mean().reset_index()
    st.plotly_chart(ch.bar(bureau_debt_seg, "RISK_SEGMENT", "TOTAL_BUREAU_DEBT", "Avg Bureau Debt by Segment"), use_container_width=True)

# Sanity check against observed TARGET (descriptive validation only, not model output)
seg_default = (df.groupby("RISK_SEGMENT", observed=True)["TARGET"].mean() * 100).round(2).reset_index()
seg_default.columns = ["Segment", "Observed Default Rate %"]
st.subheader("Descriptive Validation: Observed Default Rate by EDA Segment")
st.plotly_chart(ch.bar(seg_default, "Segment", "Observed Default Rate %", "Observed Default Rate by Risk Segment"), use_container_width=True)
st.caption("This chart is shown only to sanity-check that the rule-based segments align directionally with "
           "observed outcomes — it is descriptive validation, not a predictive model.")

st.subheader("Detailed Data Table")
st.dataframe(df[["SK_ID_CURR", "RISK_SEGMENT", "RISK_SCORE", "CREDIT_TO_INCOME", "ANNUITY_TO_INCOME",
                  "TOTAL_BUREAU_DEBT", "EMPLOYMENT_GROUP", "AMT_CREDIT", "TARGET"]].head(500), use_container_width=True)
st.download_button("Download Segmented Dataset (CSV)", df.to_csv(index=False).encode(), "risk_segmented_customers.csv", "text/csv")
