import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.data_loader import load_application_train
from utils.feature_engineering import engineer_application_features
from utils import charts as ch
from utils.metrics import fmt_currency, fmt_number
from utils.filters import apply_common_filters

st.set_page_config(page_title="Income Analysis", page_icon="🏦", layout="wide")
st.title("06 · Income Analysis")
st.caption("Business Objective: understand income distribution and how it relates to lending decisions.")

df = engineer_application_features(load_application_train())
f = apply_common_filters(df)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Average Income", fmt_currency(f["AMT_INCOME_TOTAL"].mean()))
c2.metric("Median Income", fmt_currency(f["AMT_INCOME_TOTAL"].median()))
c3.metric("Maximum Income", fmt_currency(f["AMT_INCOME_TOTAL"].max()))
c4.metric("Avg Income / Family Member", fmt_currency(f["INCOME_PER_FAMILY_MEMBER"].mean()))
c5.metric("Largest Income Group", f["INCOME_GROUP"].value_counts().idxmax())

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ch.histogram(f, "AMT_INCOME_TOTAL", "Income Histogram"), use_container_width=True)
with col2:
    ig = f["INCOME_GROUP"].value_counts().reset_index()
    ig.columns = ["Income Group", "Count"]
    st.plotly_chart(ch.bar(ig, "Income Group", "Count", "Income Group Distribution"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(ch.box(f, x="NAME_EDUCATION_TYPE", y="AMT_INCOME_TOTAL", title="Income by Education"), use_container_width=True)
with col4:
    occ_income = f.groupby("OCCUPATION_TYPE")["AMT_INCOME_TOTAL"].median().sort_values(ascending=False).reset_index()
    st.plotly_chart(ch.bar(occ_income, "OCCUPATION_TYPE", "AMT_INCOME_TOTAL", "Median Income by Occupation", horizontal=True), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    st.plotly_chart(ch.box(f, x="NAME_INCOME_TYPE", y="AMT_INCOME_TOTAL", title="Income by Income Type"), use_container_width=True)
with col6:
    sample = f.sample(min(5000, len(f)), random_state=1)
    st.plotly_chart(ch.scatter(sample, "AMT_INCOME_TOTAL", "AMT_CREDIT", "Income vs Credit"), use_container_width=True)

igdr = (f.groupby("INCOME_GROUP", observed=True)["TARGET"].mean() * 100).round(2).reset_index()
igdr.columns = ["Income Group", "Default Rate %"]
st.plotly_chart(ch.bar(igdr, "Income Group", "Default Rate %", "Income Group vs Default Rate"), use_container_width=True)

st.subheader("Detailed Data Table")
st.dataframe(f.head(500), use_container_width=True)
st.download_button("Download Filtered Dataset (CSV)", f.to_csv(index=False).encode(), "income_filtered.csv", "text/csv")

st.subheader("Recommendations")
top_borrow = f.groupby("INCOME_GROUP", observed=True)["AMT_CREDIT"].sum().idxmax()
worst_risk = igdr.sort_values("Default Rate %", ascending=False).iloc[0]["Income Group"]
st.markdown(f"""
- **{top_borrow}** income segment carries the largest total credit exposure and should be monitored for
  concentration risk.
- **{worst_risk}** shows the highest observed default rate among income groups — a candidate for tighter
  affordability checks.
- Income-per-family-member is a more informative affordability signal than raw income alone; consider using it
  in manual underwriting checklists.
""")
