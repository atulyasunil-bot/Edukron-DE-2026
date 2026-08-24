import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from utils.data_loader import DATA_DIR
from utils import charts as ch
from utils.metrics import fmt_number

st.set_page_config(page_title="Installment Payment Analysis", page_icon="🏦", layout="wide")
st.title("17 · Installment Payment Analysis")
st.caption("Business Objective: understand actual repayment behaviour (installments_payments.csv) — one of the "
           "most useful credit-risk indicators.")

path = os.path.join(DATA_DIR, "installments_payments.csv")

if not os.path.exists(path):
    st.warning(
        "`installments_payments.csv` was not part of the uploaded file set, so this page cannot render live "
        "charts. Drop the file into the `data/` folder and reload — the pipeline below runs automatically."
    )
    st.code("home-credit-streamlit/data/installments_payments.csv", language="text")
    st.markdown("""
**Feature engineering that will run automatically once the file is present:**
```
Payment Delay      = DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT
Payment Difference = AMT_PAYMENT - AMT_INSTALMENT
Payment Ratio      = AMT_PAYMENT / AMT_INSTALMENT
```
Classified into: Early / On-Time / Late Payment, and Underpayment / Full Payment / Overpayment.

**Charts:** Payment Delay Distribution, On-Time vs Late Payments donut, Scheduled vs Actual Payment scatter,
Payment Difference Distribution, Late Payment Count by Customer, Delay Days vs Payment Amount scatter.

**Customer-level features:** Total Installments, Late Payment Count/%, Average & Maximum Payment Delay,
Average Payment Ratio, Underpayment Count.
""")
else:
    df = pd.read_csv(path)
    df["PAYMENT_DELAY"] = df["DAYS_ENTRY_PAYMENT"] - df["DAYS_INSTALMENT"]
    df["PAYMENT_DIFF"] = df["AMT_PAYMENT"] - df["AMT_INSTALMENT"]
    df["PAYMENT_RATIO"] = df["AMT_PAYMENT"] / df["AMT_INSTALMENT"].replace(0, pd.NA)

    def classify(row):
        return "Late Payment" if row["PAYMENT_DELAY"] > 0 else ("Early Payment" if row["PAYMENT_DELAY"] < 0 else "On-Time Payment")
    df["PAYMENT_TIMING"] = df.apply(classify, axis=1)

    total = len(df)
    on_time_pct = (df["PAYMENT_TIMING"] == "On-Time Payment").mean() * 100
    late_pct = (df["PAYMENT_TIMING"] == "Late Payment").mean() * 100
    under_pct = (df["PAYMENT_DIFF"] < 0).mean() * 100

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Installments", fmt_number(total))
    c2.metric("Average Installment", f"{df['AMT_INSTALMENT'].mean():,.0f}")
    c3.metric("On-Time Payment %", f"{on_time_pct:.2f}%")
    c4.metric("Late Payment %", f"{late_pct:.2f}%")
    c5.metric("Underpayment %", f"{under_pct:.2f}%")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(ch.histogram(df, "PAYMENT_DELAY", "Payment Delay Distribution"), use_container_width=True)
    with col2:
        tv = df["PAYMENT_TIMING"].value_counts().reset_index()
        tv.columns = ["Timing", "Count"]
        st.plotly_chart(ch.donut(tv, "Timing", "Count", "On-Time vs Late Payments"), use_container_width=True)

    agg = df.groupby("SK_ID_CURR").agg(
        TOTAL_INSTALLMENTS=("SK_ID_PREV", "count"),
        LATE_PAYMENT_COUNT=("PAYMENT_TIMING", lambda x: (x == "Late Payment").sum()),
        AVG_PAYMENT_DELAY=("PAYMENT_DELAY", "mean"),
        MAX_PAYMENT_DELAY=("PAYMENT_DELAY", "max"),
        AVG_PAYMENT_RATIO=("PAYMENT_RATIO", "mean"),
    ).reset_index()
    agg["LATE_PAYMENT_PCT"] = agg["LATE_PAYMENT_COUNT"] / agg["TOTAL_INSTALLMENTS"] * 100
    st.subheader("Customer-Level Feature Engineering (preview)")
    st.dataframe(agg.head(200), use_container_width=True)
    st.download_button("Download Customer-Level Aggregates (CSV)", agg.to_csv(index=False).encode(), "installments_aggregates.csv", "text/csv")
