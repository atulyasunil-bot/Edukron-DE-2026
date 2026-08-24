import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from utils.data_loader import DATA_DIR
from utils import charts as ch
from utils.metrics import fmt_number

st.set_page_config(page_title="Previous Applications", page_icon="🏦", layout="wide")
st.title("15 · Previous Application Analysis")
st.caption("Business Objective: study customers' previous Home Credit loan applications (previous_application.csv).")

path = os.path.join(DATA_DIR, "previous_application.csv")

if not os.path.exists(path):
    st.warning(
        "`previous_application.csv` was not part of the uploaded file set, so this page cannot render live "
        "charts. Drop the file into the `data/` folder and reload this page — the code below will pick it up "
        "automatically without any changes."
    )
    st.code("home-credit-streamlit/data/previous_application.csv", language="text")
    st.markdown("""
**What this page will show once the file is present:**
- KPIs: Previous Applications, Approved / Refused / Cancelled counts, Approval Rate, Rejection Rate
- Application Status bar chart + Approval donut chart
- Application vs Credit Amount scatter plot
- Previous Contract Type, Client Type, and Product Type distributions
- Rejection reasons (where available) as a horizontal bar chart
- Customer-level feature engineering: number of previous applications, number approved/refused,
  approval rate per customer, average and maximum previous credit
""")
else:
    df = pd.read_csv(path)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    total = len(df)
    approved = (df["NAME_CONTRACT_STATUS"] == "Approved").sum()
    refused = (df["NAME_CONTRACT_STATUS"] == "Refused").sum()
    cancelled = (df["NAME_CONTRACT_STATUS"] == "Canceled").sum()
    c1.metric("Previous Applications", fmt_number(total))
    c2.metric("Approved", fmt_number(approved))
    c3.metric("Refused", fmt_number(refused))
    c4.metric("Cancelled", fmt_number(cancelled))
    c5.metric("Approval Rate", f"{approved/total*100:.2f}%")
    c6.metric("Rejection Rate", f"{refused/total*100:.2f}%")

    col1, col2 = st.columns(2)
    with col1:
        sv = df["NAME_CONTRACT_STATUS"].value_counts().reset_index()
        sv.columns = ["Status", "Count"]
        st.plotly_chart(ch.bar(sv, "Status", "Count", "Application Status"), use_container_width=True)
    with col2:
        st.plotly_chart(ch.donut(sv, "Status", "Count", "Approval Percentage"), use_container_width=True)

    sample = df.sample(min(5000, len(df)), random_state=1)
    st.plotly_chart(ch.scatter(sample, "AMT_APPLICATION", "AMT_CREDIT", "Application vs Credit Amount"), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        ctp = df["NAME_CONTRACT_TYPE"].value_counts().reset_index()
        ctp.columns = ["Contract Type", "Count"]
        st.plotly_chart(ch.bar(ctp, "Contract Type", "Count", "Previous Contract Types"), use_container_width=True)
    with col4:
        clt = df["NAME_CLIENT_TYPE"].value_counts().reset_index()
        clt.columns = ["Client Type", "Count"]
        st.plotly_chart(ch.bar(clt, "Client Type", "Count", "Client Type Distribution"), use_container_width=True)

    agg = df.groupby("SK_ID_CURR").agg(
        PREVIOUS_APPLICATION_COUNT=("SK_ID_PREV", "count"),
        NUMBER_APPROVED=("NAME_CONTRACT_STATUS", lambda x: (x == "Approved").sum()),
        NUMBER_REFUSED=("NAME_CONTRACT_STATUS", lambda x: (x == "Refused").sum()),
        AVG_PREVIOUS_CREDIT=("AMT_CREDIT", "mean"),
        MAX_PREVIOUS_CREDIT=("AMT_CREDIT", "max"),
    ).reset_index()
    agg["PREVIOUS_APPROVAL_RATE"] = agg["NUMBER_APPROVED"] / agg["PREVIOUS_APPLICATION_COUNT"]
    st.subheader("Customer-Level Feature Engineering (preview)")
    st.dataframe(agg.head(200), use_container_width=True)
    st.download_button("Download Customer-Level Aggregates (CSV)", agg.to_csv(index=False).encode(), "previous_application_aggregates.csv", "text/csv")
