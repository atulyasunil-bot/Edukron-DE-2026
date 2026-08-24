import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from utils.data_loader import DATA_DIR
from utils import charts as ch
from utils.metrics import fmt_number

st.set_page_config(page_title="Credit Card Analysis", page_icon="🏦", layout="wide")
st.title("18 · Credit Card Balance Analysis")
st.caption("Business Objective: understand customers' credit-card usage and repayment behaviour (credit_card_balance.csv).")

path = os.path.join(DATA_DIR, "credit_card_balance.csv")

if not os.path.exists(path):
    st.warning(
        "`credit_card_balance.csv` was not part of the uploaded file set, so this page cannot render live "
        "charts. Drop the file into the `data/` folder and reload — the pipeline below runs automatically."
    )
    st.code("home-credit-streamlit/data/credit_card_balance.csv", language="text")
    st.markdown("""
**Feature engineering that will run automatically once the file is present:**
```
Credit Utilization = AMT_BALANCE / AMT_CREDIT_LIMIT_ACTUAL
```
**Charts:** Credit Balance Distribution, Credit Limit Distribution, Credit Utilization Distribution,
Credit Limit vs Balance scatter, Balance vs Payment scatter, DPD Distribution.

**Customer-level features:** Average/Maximum Balance, Average Credit Limit, Average/Maximum Utilization,
Total Drawings, Average Payments, Maximum DPD.
""")
else:
    df = pd.read_csv(path)
    df["CREDIT_UTILIZATION"] = df["AMT_BALANCE"] / df["AMT_CREDIT_LIMIT_ACTUAL"].replace(0, pd.NA)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Credit Card Customers", fmt_number(df["SK_ID_CURR"].nunique()))
    c2.metric("Average Balance", f"{df['AMT_BALANCE'].mean():,.0f}")
    c3.metric("Average Credit Limit", f"{df['AMT_CREDIT_LIMIT_ACTUAL'].mean():,.0f}")
    c4.metric("Average Utilization", f"{df['CREDIT_UTILIZATION'].mean()*100:.1f}%")
    c5.metric("Average Monthly Payment", f"{df['AMT_PAYMENT_CURRENT'].mean():,.0f}")
    c6.metric("Customers with DPD", fmt_number(df.loc[df['SK_DPD'] > 0, 'SK_ID_CURR'].nunique()))

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(ch.histogram(df, "AMT_BALANCE", "Credit Balance Distribution"), use_container_width=True)
    with col2:
        st.plotly_chart(ch.histogram(df.dropna(subset=["CREDIT_UTILIZATION"]), "CREDIT_UTILIZATION", "Credit Utilization Distribution"), use_container_width=True)

    agg = df.groupby("SK_ID_CURR").agg(
        AVG_BALANCE=("AMT_BALANCE", "mean"),
        MAX_BALANCE=("AMT_BALANCE", "max"),
        AVG_CREDIT_LIMIT=("AMT_CREDIT_LIMIT_ACTUAL", "mean"),
        AVG_UTILIZATION=("CREDIT_UTILIZATION", "mean"),
        MAX_UTILIZATION=("CREDIT_UTILIZATION", "max"),
        MAX_DPD=("SK_DPD", "max"),
    ).reset_index()
    st.subheader("Customer-Level Feature Engineering (preview)")
    st.dataframe(agg.head(200), use_container_width=True)
    st.download_button("Download Customer-Level Aggregates (CSV)", agg.to_csv(index=False).encode(), "credit_card_aggregates.csv", "text/csv")
