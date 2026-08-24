import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.data_loader import load_application_train
from utils.feature_engineering import engineer_application_features
from utils import charts as ch
from utils.metrics import fmt_number
from utils.filters import apply_common_filters

st.set_page_config(page_title="Employment Analysis", page_icon="🏦", layout="wide")
st.title("07 · Employment Analysis")
st.caption("Business Objective: understand employment stability and its relationship to credit behaviour.")

df = engineer_application_features(load_application_train())
f = apply_common_filters(df)

emp_valid = f.dropna(subset=["EMPLOYMENT_YEARS"])

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Average Employment Years", f"{emp_valid['EMPLOYMENT_YEARS'].mean():.1f}")
c2.metric("Median Employment Years", f"{emp_valid['EMPLOYMENT_YEARS'].median():.1f}")
c3.metric("Most Common Occupation", f["OCCUPATION_TYPE"].mode()[0] if f["OCCUPATION_TYPE"].notna().any() else "N/A")
c4.metric("Most Common Organization", f["ORGANIZATION_TYPE"].mode()[0])
emp_dr = (f.groupby("EMPLOYMENT_GROUP")["TARGET"].mean() * 100).sort_values(ascending=False)
c5.metric("Highest-Risk Employment Group", emp_dr.index[0])

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ch.histogram(emp_valid, "EMPLOYMENT_YEARS", "Employment Years Distribution"), use_container_width=True)
with col2:
    eg = f["EMPLOYMENT_GROUP"].value_counts().reset_index()
    eg.columns = ["Employment Group", "Count"]
    st.plotly_chart(ch.bar(eg, "Employment Group", "Count", "Employment Group Distribution"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    egdr = emp_dr.reset_index()
    egdr.columns = ["Employment Group", "Default Rate %"]
    st.plotly_chart(ch.bar(egdr, "Employment Group", "Default Rate %", "Default Rate by Employment Group"), use_container_width=True)
with col4:
    occ_dr = (f.groupby("OCCUPATION_TYPE")["TARGET"].mean() * 100).sort_values(ascending=False).reset_index()
    occ_dr.columns = ["Occupation", "Default Rate %"]
    st.plotly_chart(ch.bar(occ_dr, "Occupation", "Default Rate %", "Occupation vs Default Rate", horizontal=True), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    org_dr = (f.groupby("ORGANIZATION_TYPE")["TARGET"].mean() * 100).sort_values(ascending=False).head(20).reset_index()
    org_dr.columns = ["Organization Type", "Default Rate %"]
    st.plotly_chart(ch.bar(org_dr, "Organization Type", "Default Rate %", "Organization Type vs Default (Top 20)", horizontal=True), use_container_width=True)
with col6:
    sample = emp_valid.sample(min(5000, len(emp_valid)), random_state=1)
    st.plotly_chart(ch.scatter(sample, "EMPLOYMENT_YEARS", "AMT_INCOME_TOTAL", "Employment Years vs Income"), use_container_width=True)

sample2 = emp_valid.sample(min(5000, len(emp_valid)), random_state=1)
st.plotly_chart(ch.scatter(sample2, "EMPLOYMENT_YEARS", "AMT_CREDIT", "Employment Years vs Credit"), use_container_width=True)

st.subheader("Required Preprocessing Note")
sentinel_count = int((df["DAYS_EMPLOYED"] == 365243).sum())
st.markdown(f"""
`DAYS_EMPLOYED` contains **{sentinel_count:,}** records using the sentinel value `365243`
(Home Credit's convention for pensioners / not-currently-employed applicants). These were recoded to `NaN` and
bucketed into an **"Unemployed / Special"** employment group rather than being treated as a 1000-year outlier.
""")

st.subheader("Detailed Data Table")
st.dataframe(f.head(500), use_container_width=True)
st.download_button("Download Filtered Dataset (CSV)", f.to_csv(index=False).encode(), "employment_filtered.csv", "text/csv")

st.subheader("Recommendations")
st.markdown(f"""
1. The **{emp_dr.index[0]}** employment group shows the highest observed default rate — factor employment
   tenure into manual review triggers.
2. Occupation-level default-rate spread suggests occupation should be a monitored dimension, not just income.
3. Track the "Unemployed / Special" segment separately since it mixes pensioners (typically lower risk) with
   genuinely unemployed applicants (typically higher risk).
""")
