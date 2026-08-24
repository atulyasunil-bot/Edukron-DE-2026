import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from utils.data_loader import load_application_train
from utils.preprocessing import dtype_summary, duplicate_summary
from utils import charts as ch
from utils.metrics import fmt_number, fmt_pct

st.set_page_config(page_title="Data Quality", page_icon="🏦", layout="wide")
st.title("02 · Data Quality Dashboard")
st.caption("Business Objective: assess the overall quality of the raw application_train table before any cleaning.")

df = load_application_train()
summary = dtype_summary(df)

num_cols = df.select_dtypes(include="number").shape[1]
cat_cols = df.select_dtypes(include="object").shape[1]
missing_cells = df.isnull().sum().sum()
total_cells = df.shape[0] * df.shape[1]
dup = duplicate_summary(df, id_col="SK_ID_CURR")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Number of Rows", fmt_number(df.shape[0]))
c2.metric("Number of Columns", fmt_number(df.shape[1]))
c3.metric("Numerical Columns", fmt_number(num_cols))
c4.metric("Categorical Columns", fmt_number(cat_cols))

c5, c6, c7, c8 = st.columns(4)
c5.metric("Missing Cells", fmt_number(missing_cells))
c6.metric("Duplicate Rows", fmt_number(dup["full_row_duplicates"]))
c7.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1e6:.1f} MB")
c8.metric("Unique Customers (SK_ID_CURR)", fmt_number(dup.get("unique_ids", df.shape[0])))

st.divider()
st.subheader("Column-Level Summary Table")
st.dataframe(summary, use_container_width=True, height=350)

col1, col2 = st.columns(2)
with col1:
    dtc = df.dtypes.astype(str).value_counts().reset_index()
    dtc.columns = ["Data Type", "Count"]
    st.plotly_chart(ch.bar(dtc, "Data Type", "Count", "Column Data Types"), use_container_width=True)
with col2:
    avail = pd.DataFrame({
        "Column": ["Missing", "Available"],
        "Cells": [missing_cells, total_cells - missing_cells],
    })
    st.plotly_chart(ch.donut(avail, "Column", "Cells", "Missing vs Available Data"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    top_unique = summary.sort_values("Unique Values", ascending=False).head(20)
    st.plotly_chart(ch.bar(top_unique, "Column", "Unique Values", "Unique Values by Column (Top 20)", horizontal=True), use_container_width=True)
with col4:
    completeness = round(100 - (missing_cells / total_cells * 100), 2)
    st.plotly_chart(ch.gauge(completeness, "Dataset Completeness %"), use_container_width=True)

st.subheader("Required Analysis")
worst = summary.sort_values("Missing %", ascending=False).head(5)
st.markdown(f"""
- **Columns with quality issues:** {worst.shape[0]} columns exceed noticeable missingness; top offender is
  **{worst.iloc[0]['Column']}** at **{fmt_pct(worst.iloc[0]['Missing %'])}** missing.
- **Extreme missingness:** columns above 60% missing should be flagged for either dropping or converting into a
  "was-reported" indicator flag rather than imputing blindly.
- **Datatype conversion candidates:** `DAYS_BIRTH`, `DAYS_EMPLOYED`, `DAYS_REGISTRATION` are stored as negative day
  counts and should be converted into positive year-based features (done on later pages), not used raw.
- **Duplicate customers:** {dup['duplicate_ids']} duplicate `SK_ID_CURR` values were found — {"none, IDs are unique" if dup['duplicate_ids']==0 else "these need investigation before any customer-level aggregation"}.
- **Categorical inconsistencies:** occupation and organization-type free-text fields contain an "XNA"/unknown
  category that should be treated as missing rather than a genuine category during grouping.
""")

st.subheader("Preprocessing Strategy Recommendation")
st.markdown("""
1. Drop columns with >60% missingness that have no clear business substitute.
2. Median-impute skewed numeric fields (income, credit); mode-impute low-cardinality categoricals.
3. Convert all `DAYS_*` fields to positive year/age features.
4. Create "missing indicator" flags for building/apartment quality fields before dropping them, since missingness
   itself may correlate with property type.
5. Standardise the `XNA` / `Unknown` sentinel values to proper NaN before categorical encoding.
""")
