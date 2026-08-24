import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_application_train
from utils.preprocessing import missing_value_table, missing_bucket
from utils import charts as ch
from utils.metrics import fmt_number, fmt_pct

st.set_page_config(page_title="Missing Value Analysis", page_icon="🏦", layout="wide")
st.title("03 · Missing Value Analysis")
st.caption("Business Objective: understand exactly where data is missing and decide a defensible treatment per column.")

df = load_application_train()
miss = missing_value_table(df)
miss["Bucket"] = miss["Missing %"].apply(missing_bucket)

total_missing = int(df.isnull().sum().sum())
total_cells = df.shape[0] * df.shape[1]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Missing Values", fmt_number(total_missing))
c2.metric("Missing Percentage", fmt_pct(total_missing / total_cells * 100))
c3.metric("Columns with Missing Data", fmt_number(len(miss)))
c4.metric("Columns Above 30% Missing", fmt_number((miss["Missing %"] > 30).sum()))
c5.metric("Columns Above 50% Missing", fmt_number((miss["Missing %"] > 50).sum()))

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ch.bar(miss.head(20), "Column", "Missing %", "Top 20 Columns by Missing %", horizontal=True), use_container_width=True)
with col2:
    st.plotly_chart(ch.histogram(miss, "Missing %", "Missing Percentage Distribution", nbins=20), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    top40 = miss.head(40)["Column"].tolist()
    heat_df = df[top40].isnull().astype(int).sample(min(300, len(df)), random_state=1)
    st.plotly_chart(ch.heatmap(heat_df.values, "Missingness Heatmap (sample of 300 rows x top 40 columns)",
                                x_labels=top40, y_labels=None), use_container_width=True)
with col4:
    dtypes_missing = df[miss["Column"]].dtypes.astype(str).value_counts().reset_index()
    dtypes_missing.columns = ["Data Type", "Column Count"]
    st.plotly_chart(ch.bar(dtypes_missing, "Data Type", "Column Count", "Missing Values by Data Type"), use_container_width=True)

st.subheader("Missingness Buckets")
bucket_counts = miss["Bucket"].value_counts().reindex(
    ["0-5% Missing", "5-20% Missing", "20-40% Missing", "40-60% Missing", "60%+ Missing"]
).fillna(0).reset_index()
bucket_counts.columns = ["Bucket", "Column Count"]
st.plotly_chart(ch.bar(bucket_counts, "Bucket", "Column Count", "Columns per Missingness Bucket"), use_container_width=True)
st.dataframe(miss, use_container_width=True, height=350)

st.subheader("Preprocessing Recommendations by Column Group")
st.markdown("""
| Missingness Group | Example Columns | Recommended Treatment | Reason |
|---|---|---|---|
| 60%+ Missing | `COMMONAREA_*`, `NONLIVINGAPARTMENTS_*` | Drop column, or keep only a binary "reported / not reported" indicator | Too sparse to impute reliably; presence of the value may itself be informative |
| 40–60% Missing | `FONDKAPREMONT_MODE`, `LIVINGAPARTMENTS_*` | Create missing-indicator + median/mode fill | Retains signal while avoiding heavy imputation bias |
| 20–40% Missing | `OCCUPATION_TYPE`, `EXT_SOURCE_1` | Mode fill for categorical, median fill for numeric, or keep as its own "Unknown" category | Moderate gap, business-meaningful category exists |
| 5–20% Missing | `AMT_REQ_CREDIT_BUREAU_*`, `EXT_SOURCE_3` | Median / mode fill | Small gap, standard imputation is safe |
| 0–5% Missing | `AMT_ANNUITY`, `AMT_GOODS_PRICE`, `CNT_FAM_MEMBERS` | Median / mode fill or drop the few rows | Negligible impact either way |
""")
