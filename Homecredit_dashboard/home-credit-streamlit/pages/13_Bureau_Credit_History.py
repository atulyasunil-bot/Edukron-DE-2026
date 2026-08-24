import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.data_loader import load_bureau
from utils import charts as ch
from utils.metrics import fmt_number, fmt_currency
from utils.filters import multiselect_filter

st.set_page_config(page_title="Bureau Credit History", page_icon="🏦", layout="wide")
st.title("13 · Bureau Credit History Analysis")
st.caption("Business Objective: analyse loans previously reported by other financial institutions (bureau.csv).")

bureau = load_bureau()
st.sidebar.markdown("### Filters")
f = multiselect_filter(bureau, "CREDIT_ACTIVE", "Credit Active Status")
f = multiselect_filter(f, "CREDIT_TYPE", "Credit Type")
st.sidebar.markdown(f"**{len(f):,} / {len(bureau):,} rows selected**")

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Bureau Accounts", fmt_number(len(f)))
c2.metric("Customers with Bureau History", fmt_number(f["SK_ID_CURR"].nunique()))
c3.metric("Active Credits", fmt_number((f["CREDIT_ACTIVE"] == "Active").sum()))
c4.metric("Closed Credits", fmt_number((f["CREDIT_ACTIVE"] == "Closed").sum()))
c5.metric("Total Bureau Debt", fmt_currency(f["AMT_CREDIT_SUM_DEBT"].sum()))
c6.metric("Total Overdue Amount", fmt_currency(f["AMT_CREDIT_SUM_OVERDUE"].sum()))

st.divider()
col1, col2 = st.columns(2)
with col1:
    ac = f["CREDIT_ACTIVE"].value_counts().reset_index()
    ac.columns = ["Status", "Count"]
    st.plotly_chart(ch.bar(ac, "Status", "Count", "Active vs Closed Loans"), use_container_width=True)
with col2:
    ctp = f["CREDIT_TYPE"].value_counts().reset_index()
    ctp.columns = ["Credit Type", "Count"]
    st.plotly_chart(ch.bar(ctp, "Credit Type", "Count", "Credit Type Distribution", horizontal=True), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(ch.histogram(f, "AMT_CREDIT_SUM", "Bureau Credit Amount Distribution"), use_container_width=True)
with col4:
    st.plotly_chart(ch.histogram(f.dropna(subset=["AMT_CREDIT_SUM_DEBT"]), "AMT_CREDIT_SUM_DEBT", "Bureau Debt Distribution"), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    overdue = f[f["AMT_CREDIT_SUM_OVERDUE"] > 0]
    st.plotly_chart(ch.histogram(overdue, "AMT_CREDIT_SUM_OVERDUE", "Overdue Amount Distribution (overdue > 0 only)"), use_container_width=True)
with col6:
    debt_by_type = f.groupby("CREDIT_TYPE")["AMT_CREDIT_SUM_DEBT"].sum().sort_values(ascending=False).head(10).reset_index()
    st.plotly_chart(ch.bar(debt_by_type, "CREDIT_TYPE", "AMT_CREDIT_SUM_DEBT", "Credit Type vs Total Debt", horizontal=True), use_container_width=True)

st.subheader("Customer-Level Bureau Aggregates (preview)")
from utils.feature_engineering import aggregate_bureau_features
agg = aggregate_bureau_features(bureau)
st.dataframe(agg.head(200), use_container_width=True)
st.download_button("Download Customer-Level Bureau Aggregates (CSV)", agg.to_csv(index=False).encode(), "bureau_customer_aggregates.csv", "text/csv")

st.subheader("Key Observations")
st.markdown(f"""
- **{fmt_number(f['SK_ID_CURR'].nunique())}** unique customers have external bureau history in this slice.
- Total reported bureau debt across selected records is **{fmt_currency(f['AMT_CREDIT_SUM_DEBT'].sum())}**.
- **{ctp.iloc[0]['Credit Type']}** is the most common credit type reported to the bureau.
""")

st.subheader("Recommendations")
st.markdown("""
1. Merge bureau aggregates (`BUREAU_ACCOUNT_COUNT`, `TOTAL_BUREAU_DEBT`, `MAX_BUREAU_OVERDUE`) onto the customer
   level to enrich the application-level risk view.
2. Flag customers with multiple **Active** bureau accounts for closer manual review of existing obligations.
3. Any non-zero `AMT_CREDIT_SUM_OVERDUE` deserves priority attention regardless of amount, since it indicates an
   existing, unresolved delinquency with another lender.
""")
