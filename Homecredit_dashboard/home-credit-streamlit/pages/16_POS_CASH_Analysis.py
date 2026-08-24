import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.data_loader import load_pos_cash
from utils.feature_engineering import aggregate_pos_cash_features
from utils import charts as ch
from utils.metrics import fmt_number
from utils.filters import multiselect_filter

st.set_page_config(page_title="POS/CASH Loan Analysis", page_icon="🏦", layout="wide")
st.title("16 · POS / CASH Loan Analysis")
st.caption("Business Objective: analyse point-of-sale and cash loan balances (POS_CASH_balance.csv).")

pos = load_pos_cash()
st.sidebar.markdown("### Filters")
f = multiselect_filter(pos, "NAME_CONTRACT_STATUS", "Contract Status")
st.sidebar.markdown(f"**{len(f):,} / {len(pos):,} rows selected**")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("POS/CASH Records", fmt_number(len(f)))
c2.metric("Active Contracts", fmt_number((f["NAME_CONTRACT_STATUS"] == "Active").sum()))
c3.metric("Completed Contracts", fmt_number((f["NAME_CONTRACT_STATUS"] == "Completed").sum()))
c4.metric("Avg Installments Remaining", f"{f['CNT_INSTALMENT_FUTURE'].mean():.1f}")
c5.metric("Customers with DPD > 0", fmt_number(f.loc[f['SK_DPD'] > 0, 'SK_ID_CURR'].nunique()))

st.divider()
col1, col2 = st.columns(2)
with col1:
    cs = f["NAME_CONTRACT_STATUS"].value_counts().reset_index()
    cs.columns = ["Status", "Count"]
    st.plotly_chart(ch.bar(cs, "Status", "Count", "Contract Status Distribution"), use_container_width=True)
with col2:
    st.plotly_chart(ch.histogram(f.dropna(subset=["CNT_INSTALMENT_FUTURE"]), "CNT_INSTALMENT_FUTURE", "Installments Remaining Distribution"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    dpd_pos = f[f["SK_DPD"] > 0]
    st.plotly_chart(ch.histogram(dpd_pos, "SK_DPD", "Days Past Due Distribution (DPD > 0)"), use_container_width=True)
with col4:
    st.plotly_chart(ch.box(f, x="NAME_CONTRACT_STATUS", y="SK_DPD", title="DPD by Contract Status"), use_container_width=True)

sample = f.sample(min(20000, len(f)), random_state=1)
monthly = sample.groupby("MONTHS_BALANCE")["CNT_INSTALMENT_FUTURE"].mean().reset_index()
st.plotly_chart(ch.line(monthly, "MONTHS_BALANCE", "CNT_INSTALMENT_FUTURE", "Monthly Balance Trend (avg installments remaining, sampled)"), use_container_width=True)

st.subheader("Customer-Level Feature Engineering (preview)")
agg = aggregate_pos_cash_features(pos)
st.dataframe(agg.head(200), use_container_width=True)
st.download_button("Download Customer-Level POS/CASH Aggregates (CSV)", agg.to_csv(index=False).encode(), "pos_cash_customer_aggregates.csv", "text/csv")

st.subheader("Recommendations")
st.markdown("""
1. Merge `AVG_DPD`, `MAX_DPD` and `TOTAL_DPD_EVENTS` onto the application-level customer profile as repayment
   stability signals from POS/cash products.
2. Prioritise manual review for customers whose `MAX_DPD` is high even if their most recent status is "Active" —
   past delinquency is informative regardless of current standing.
3. Track completed-vs-active contract mix over time as a portfolio health indicator.
""")
