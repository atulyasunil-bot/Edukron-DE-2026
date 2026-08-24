import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from utils.data_loader import load_bureau_balance
from utils import charts as ch
from utils.metrics import fmt_number

st.set_page_config(page_title="Bureau Balance Analysis", page_icon="🏦", layout="wide")
st.title("14 · Bureau Balance Analysis")
st.caption("Business Objective: analyse historical monthly bureau account status (bureau_balance.csv).")

bb = load_bureau_balance()

st.sidebar.markdown("### Filters")
month_range = st.sidebar.slider("Months Balance Range", int(bb["MONTHS_BALANCE"].min()), int(bb["MONTHS_BALANCE"].max()),
                                 (int(bb["MONTHS_BALANCE"].min()), int(bb["MONTHS_BALANCE"].max())))
f = bb[(bb["MONTHS_BALANCE"] >= month_range[0]) & (bb["MONTHS_BALANCE"] <= month_range[1])]
st.sidebar.markdown(f"**{len(f):,} / {len(bb):,} rows selected**")

DELINQUENT_STATUSES = ["1", "2", "3", "4", "5"]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Monthly Records", fmt_number(len(f)))
c2.metric("Unique Bureau Accounts", fmt_number(f["SK_ID_BUREAU"].nunique()))
c3.metric("Most Common Status", f["STATUS"].mode()[0])
c4.metric("Delinquency Records", fmt_number(f["STATUS"].isin(DELINQUENT_STATUSES).sum()))
c5.metric("Closed Records ('C')", fmt_number((f["STATUS"] == "C").sum()))

st.divider()
col1, col2 = st.columns(2)
with col1:
    sv = f["STATUS"].value_counts().reset_index()
    sv.columns = ["Status", "Count"]
    st.plotly_chart(ch.bar(sv, "Status", "Count", "Status Distribution"), use_container_width=True)
with col2:
    st.plotly_chart(ch.donut(sv, "Status", "Count", "Status Percentage"), use_container_width=True)

col3, col4 = st.columns(2)
sample = f.sample(min(200000, len(f)), random_state=1)
monthly = sample.groupby(["MONTHS_BALANCE", "STATUS"]).size().reset_index(name="Count")
with col3:
    st.plotly_chart(ch.stacked_bar(monthly, "MONTHS_BALANCE", "Count", "STATUS", "Account Status by Month (sampled)"), use_container_width=True)
with col4:
    delinq_trend = sample.assign(is_delinq=sample["STATUS"].isin(DELINQUENT_STATUSES).astype(int)) \
                          .groupby("MONTHS_BALANCE")["is_delinq"].mean().mul(100).reset_index()
    delinq_trend.columns = ["Months Balance", "Delinquency Rate %"]
    st.plotly_chart(ch.line(delinq_trend, "Months Balance", "Delinquency Rate %", "Monthly Delinquency Trend (sampled)"), use_container_width=True)

st.subheader("Status Heatmap (Months x Status, sampled)")
pivot = pd.crosstab(sample["MONTHS_BALANCE"], sample["STATUS"])
pivot = pivot.sort_index()
st.plotly_chart(ch.heatmap(pivot.values.T, "Status Heatmap", x_labels=pivot.index.tolist(), y_labels=pivot.columns.tolist()), use_container_width=True)

st.subheader("Customer/Account-Level Feature Engineering (preview)")
acc_features = bb.groupby("SK_ID_BUREAU").agg(
    MONTHS_WITH_DELINQUENCY=("STATUS", lambda x: x.isin(DELINQUENT_STATUSES).sum()),
    MAX_DELINQUENCY_LEVEL=("STATUS", lambda x: max([int(s) for s in x if s.isdigit()], default=0)),
    CLOSED_MONTHS=("STATUS", lambda x: (x == "C").sum()),
    ACTIVE_MONTHS=("STATUS", lambda x: (x == "0").sum()),
).reset_index()
st.dataframe(acc_features.head(200), use_container_width=True)
st.download_button("Download Bureau-Account Aggregates (CSV)", acc_features.to_csv(index=False).encode(), "bureau_balance_account_aggregates.csv", "text/csv")

st.subheader("Recommendations")
st.markdown("""
1. Join `MONTHS_WITH_DELINQUENCY` and `MAX_DELINQUENCY_LEVEL` onto `bureau.csv` (via `SK_ID_BUREAU`) and then onto
   the customer level (via `SK_ID_CURR`) to enrich risk views with external repayment history.
2. Accounts with a non-zero `MAX_DELINQUENCY_LEVEL` warrant closer manual review regardless of how long ago it
   occurred.
3. Monitor month-over-month delinquency-rate trend as an early-warning macro signal, not just a per-account flag.
""")
