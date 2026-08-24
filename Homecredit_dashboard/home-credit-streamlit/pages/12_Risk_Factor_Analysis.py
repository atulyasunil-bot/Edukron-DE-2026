import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import numpy as np
from utils.data_loader import load_application_train
from utils.feature_engineering import engineer_application_features
from utils import charts as ch
from utils.filters import apply_common_filters

st.set_page_config(page_title="Risk Factor Analysis", page_icon="🏦", layout="wide")
st.title("12 · Risk Factor Exploration")
st.caption("Business Objective: study which variables show a meaningful observed relationship with default. Correlation ≠ causation.")

df = engineer_application_features(load_application_train())
f = apply_common_filters(df)

col1, col2 = st.columns(2)
with col1:
    age_dr = (f.groupby("AGE_GROUP", observed=True)["TARGET"].mean() * 100).reset_index()
    age_dr.columns = ["Age Group", "Default Rate %"]
    st.plotly_chart(ch.bar(age_dr, "Age Group", "Default Rate %", "Age Group vs Default Rate"), use_container_width=True)
with col2:
    import pandas as pd
    f["CREDIT_BAND"] = pd.qcut(f["AMT_CREDIT"], 5, duplicates="drop")
    cr_dr = (f.groupby("CREDIT_BAND", observed=True)["TARGET"].mean() * 100).reset_index()
    cr_dr.columns = ["Credit Band", "Default Rate %"]
    cr_dr["Credit Band"] = cr_dr["Credit Band"].astype(str)
    st.plotly_chart(ch.bar(cr_dr, "Credit Band", "Default Rate %", "Credit Band vs Default Rate"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    inc_dr = (f.groupby("INCOME_GROUP", observed=True)["TARGET"].mean() * 100).reset_index()
    inc_dr.columns = ["Income Band", "Default Rate %"]
    st.plotly_chart(ch.bar(inc_dr, "Income Band", "Default Rate %", "Income Band vs Default Rate"), use_container_width=True)
with col4:
    emp_dr = (f.groupby("EMPLOYMENT_GROUP")["TARGET"].mean() * 100).reset_index()
    emp_dr.columns = ["Employment Band", "Default Rate %"]
    st.plotly_chart(ch.bar(emp_dr, "Employment Band", "Default Rate %", "Employment Band vs Default Rate"), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    f["CTI_BAND"] = pd.qcut(f["CREDIT_TO_INCOME"].clip(upper=f["CREDIT_TO_INCOME"].quantile(0.99)), 5, duplicates="drop")
    cti_dr = (f.groupby("CTI_BAND", observed=True)["TARGET"].mean() * 100).reset_index()
    cti_dr.columns = ["Credit-to-Income Band", "Default Rate %"]
    cti_dr["Credit-to-Income Band"] = cti_dr["Credit-to-Income Band"].astype(str)
    st.plotly_chart(ch.bar(cti_dr, "Credit-to-Income Band", "Default Rate %", "Credit-to-Income Band vs Default"), use_container_width=True)
with col6:
    f["ATI_BAND"] = pd.qcut(f["ANNUITY_TO_INCOME"].clip(upper=f["ANNUITY_TO_INCOME"].quantile(0.99)), 5, duplicates="drop")
    ati_dr = (f.groupby("ATI_BAND", observed=True)["TARGET"].mean() * 100).reset_index()
    ati_dr.columns = ["Annuity-to-Income Band", "Default Rate %"]
    ati_dr["Annuity-to-Income Band"] = ati_dr["Annuity-to-Income Band"].astype(str)
    st.plotly_chart(ch.bar(ati_dr, "Annuity-to-Income Band", "Default Rate %", "Annuity-to-Income Band vs Default"), use_container_width=True)

st.subheader("Correlation Heatmap (Numerical Variables)")
num_cols = ["TARGET", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AGE_YEARS",
            "EMPLOYMENT_YEARS", "CNT_FAM_MEMBERS", "CREDIT_TO_INCOME", "ANNUITY_TO_INCOME"]
num_cols = [c for c in num_cols if c in f.columns]
corr = f[num_cols].corr(numeric_only=True)
st.plotly_chart(ch.heatmap(corr.values, "Correlation Heatmap", x_labels=corr.columns.tolist(), y_labels=corr.columns.tolist()), use_container_width=True)
st.dataframe(corr.round(3), use_container_width=True)

st.subheader("Important Rule")
top_corr = corr["TARGET"].drop("TARGET").abs().sort_values(ascending=False)
st.markdown(f"""
**Correlation does not prove causation.** The variable with the strongest linear association with `TARGET` in this
slice is **{top_corr.index[0]}** (|r| = {top_corr.iloc[0]:.3f}). This is reported here strictly as an
**observed relationship**, not a causal claim — e.g. we say "customers with lower `{top_corr.index[0]}` are
associated with higher observed default rates," never "`{top_corr.index[0]}` causes default."
""")

st.subheader("Detailed Data Table")
st.dataframe(f.head(500), use_container_width=True)
st.download_button("Download Filtered Dataset (CSV)", f.to_csv(index=False).encode(), "risk_factors_filtered.csv", "text/csv")
