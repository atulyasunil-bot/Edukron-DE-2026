import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from utils.data_loader import load_application_train
from utils.feature_engineering import engineer_application_features
from utils import charts as ch
from utils.metrics import fmt_currency, fmt_pct, fmt_number
from utils.filters import apply_common_filters

st.set_page_config(page_title="Executive Overview", page_icon="🏦", layout="wide")
st.title("01 · Executive Portfolio Overview")
st.caption("Business Objective: give management a one-glance view of the whole loan portfolio.")

df = engineer_application_features(load_application_train())
f = apply_common_filters(df)

# ---- KPI cards ----
total = len(f)
default_rate = f["TARGET"].mean() * 100 if total else 0
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Customers", fmt_number(total))
c2.metric("Default Customers", fmt_number((f["TARGET"] == 1).sum()))
c3.metric("Non-Default Customers", fmt_number((f["TARGET"] == 0).sum()))
c4.metric("Default Rate", fmt_pct(default_rate))
c5.metric("Total Credit Exposure", fmt_currency(f["AMT_CREDIT"].sum()))
c6.metric("Average Credit Amount", fmt_currency(f["AMT_CREDIT"].mean()))

c7, c8, c9, c10, c11, c12 = st.columns(6)
c7.metric("Average Income", fmt_currency(f["AMT_INCOME_TOTAL"].mean()))
c8.metric("Average Annuity", fmt_currency(f["AMT_ANNUITY"].mean()))
c9.metric("Average Goods Price", fmt_currency(f["AMT_GOODS_PRICE"].mean()))
c10.metric("Median Income", fmt_currency(f["AMT_INCOME_TOTAL"].median()))
c11.metric("Median Credit Amount", fmt_currency(f["AMT_CREDIT"].median()))
c12.metric("Contract Types", fmt_number(f["NAME_CONTRACT_TYPE"].nunique()))

st.divider()

col1, col2 = st.columns(2)
with col1:
    tvc = f["TARGET"].value_counts().rename({0: "Non-Default", 1: "Default"}).reset_index()
    tvc.columns = ["Status", "Count"]
    st.plotly_chart(ch.bar(tvc, "Status", "Count", "Default vs Non-Default"), use_container_width=True)
with col2:
    st.plotly_chart(ch.donut(tvc, "Status", "Count", "Default Percentage"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    ct = f["NAME_CONTRACT_TYPE"].value_counts().reset_index()
    ct.columns = ["Contract Type", "Count"]
    st.plotly_chart(ch.bar(ct, "Contract Type", "Count", "Applications by Contract Type"), use_container_width=True)
with col4:
    st.plotly_chart(ch.histogram(f, "AMT_CREDIT", "Credit Amount Distribution"), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    st.plotly_chart(ch.histogram(f, "AMT_INCOME_TOTAL", "Income Distribution"), use_container_width=True)
with col6:
    inc_tree = f.groupby("NAME_INCOME_TYPE")["AMT_CREDIT"].sum().reset_index()
    inc_tree["ALL"] = "Portfolio"
    st.plotly_chart(ch.treemap(inc_tree, ["ALL", "NAME_INCOME_TYPE"], "AMT_CREDIT", "Credit by Income Type"), use_container_width=True)

col7, col8 = st.columns(2)
with col7:
    dr = (f.groupby("NAME_INCOME_TYPE")["TARGET"].mean() * 100).round(2).sort_values(ascending=False).reset_index()
    dr.columns = ["Income Type", "Default Rate %"]
    st.plotly_chart(ch.bar(dr, "Income Type", "Default Rate %", "Default Rate by Income Type", horizontal=True), use_container_width=True)
with col8:
    sample = f.sample(min(5000, len(f)), random_state=1)
    st.plotly_chart(ch.scatter(sample, "AMT_INCOME_TOTAL", "AMT_CREDIT", "Income vs Credit"), use_container_width=True)

st.divider()
st.subheader("Detailed Data Table")
st.dataframe(f.head(500), use_container_width=True)
st.download_button("Download Filtered Dataset (CSV)", f.to_csv(index=False).encode(), "filtered_portfolio.csv", "text/csv")

st.subheader("Key Observations")
top_income_seg = f["NAME_INCOME_TYPE"].value_counts().idxmax()
highest_risk_income = dr.iloc[0]["Income Type"] if len(dr) else "N/A"
st.markdown(f"""
- Overall observed default rate in the selected slice is **{fmt_pct(default_rate)}**.
- Total credit exposure across the selected customers is **{fmt_currency(f['AMT_CREDIT'].sum())}**.
- The largest customer segment by income type is **{top_income_seg}**.
- The income type with the highest observed default rate is **{highest_risk_income}**.
- Typical (median) credit amount is **{fmt_currency(f['AMT_CREDIT'].median())}** against a median income of **{fmt_currency(f['AMT_INCOME_TOTAL'].median())}**.
""")

st.subheader("Business Recommendations")
st.markdown("""
1. Prioritise manual review for income segments showing above-average default rates rather than treating all applicants uniformly.
2. Track total credit exposure by income type monthly to catch concentration risk building up in any single segment.
3. Use the income-vs-credit scatter pattern to sanity-check whether credit sizing keeps pace with income growth across the portfolio.
""")
