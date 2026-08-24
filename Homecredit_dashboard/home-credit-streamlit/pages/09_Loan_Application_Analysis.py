import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.data_loader import load_application_train
from utils.feature_engineering import engineer_application_features
from utils import charts as ch
from utils.metrics import fmt_currency
from utils.filters import apply_common_filters

st.set_page_config(page_title="Loan Application Analysis", page_icon="🏦", layout="wide")
st.title("09 · Current Loan Application Analysis")
st.caption("Business Objective: understand the structure of current loan applications.")

df = engineer_application_features(load_application_train())
f = apply_common_filters(df)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Applications", f"{len(f):,}")
c2.metric("Average Credit", fmt_currency(f["AMT_CREDIT"].mean()))
c3.metric("Median Credit", fmt_currency(f["AMT_CREDIT"].median()))
c4.metric("Average Annuity", fmt_currency(f["AMT_ANNUITY"].mean()))
c5.metric("Average Goods Price", fmt_currency(f["AMT_GOODS_PRICE"].mean()))
c6.metric("Most Common Contract Type", f["NAME_CONTRACT_TYPE"].mode()[0])

st.divider()
col1, col2 = st.columns(2)
with col1:
    ct = f["NAME_CONTRACT_TYPE"].value_counts().reset_index()
    ct.columns = ["Contract Type", "Count"]
    st.plotly_chart(ch.bar(ct, "Contract Type", "Count", "Applications by Contract Type"), use_container_width=True)
with col2:
    st.plotly_chart(ch.histogram(f, "AMT_CREDIT", "Credit Amount Distribution"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(ch.histogram(f, "AMT_ANNUITY", "Annuity Distribution"), use_container_width=True)
with col4:
    st.plotly_chart(ch.histogram(f, "AMT_GOODS_PRICE", "Goods Price Distribution"), use_container_width=True)

col5, col6 = st.columns(2)
sample = f.sample(min(5000, len(f)), random_state=1)
with col5:
    st.plotly_chart(ch.scatter(sample, "AMT_GOODS_PRICE", "AMT_CREDIT", "Credit vs Goods Price"), use_container_width=True)
with col6:
    st.plotly_chart(ch.scatter(sample, "AMT_ANNUITY", "AMT_CREDIT", "Credit vs Annuity"), use_container_width=True)

col7, col8 = st.columns(2)
with col7:
    wd = f["WEEKDAY_APPR_PROCESS_START"].value_counts().reindex(
        ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    ).reset_index()
    wd.columns = ["Weekday", "Count"]
    st.plotly_chart(ch.bar(wd, "Weekday", "Count", "Applications by Weekday"), use_container_width=True)
with col8:
    hr = f["HOUR_APPR_PROCESS_START"].value_counts().sort_index().reset_index()
    hr.columns = ["Hour", "Count"]
    st.plotly_chart(ch.line(hr, "Hour", "Count", "Applications by Hour"), use_container_width=True)

st.subheader("Detailed Data Table")
st.dataframe(f.head(500), use_container_width=True)
st.download_button("Download Filtered Dataset (CSV)", f.to_csv(index=False).encode(), "loan_application_filtered.csv", "text/csv")

st.subheader("Recommendations")
peak_hour = hr.sort_values("Count", ascending=False).iloc[0]["Hour"]
st.markdown(f"""
1. **{ct.iloc[0]['Contract Type']}** is the dominant loan product — ensure operational capacity matches this
   volume.
2. Typical credit size clusters around **{fmt_currency(f['AMT_CREDIT'].median())}**; use this as a baseline when
   spotting abnormally large requests.
3. Application volume peaks around **hour {int(peak_hour)}** — staff processing/support capacity accordingly.
""")
