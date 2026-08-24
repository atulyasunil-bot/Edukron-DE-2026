import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.data_loader import load_application_train
from utils.feature_engineering import engineer_application_features
from utils import charts as ch
from utils.metrics import fmt_pct, fmt_number
from utils.filters import apply_common_filters

st.set_page_config(page_title="Default Risk EDA", page_icon="🏦", layout="wide")
st.title("11 · Default Risk EDA")
st.caption("Business Objective: explore the TARGET variable in depth. This is EDA only — no predictive model is built.")

df = engineer_application_features(load_application_train())
f = apply_common_filters(df)

def top_group(col):
    return (f.groupby(col, observed=True)["TARGET"].mean() * 100).sort_values(ascending=False).index[0]

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Default Customers", fmt_number((f["TARGET"] == 1).sum()))
c2.metric("Non-Default Customers", fmt_number((f["TARGET"] == 0).sum()))
c3.metric("Default Rate", fmt_pct(f["TARGET"].mean() * 100))
c4.metric("Highest-Risk Age Group", top_group("AGE_GROUP"))
c5.metric("Highest-Risk Income Group", top_group("INCOME_GROUP"))
c6.metric("Highest-Risk Employment Group", top_group("EMPLOYMENT_GROUP"))

st.divider()
col1, col2 = st.columns(2)
with col1:
    tvc = f["TARGET"].value_counts().rename({0: "Non-Default", 1: "Default"}).reset_index()
    tvc.columns = ["Status", "Count"]
    st.plotly_chart(ch.bar(tvc, "Status", "Count", "TARGET Distribution"), use_container_width=True)
with col2:
    st.plotly_chart(ch.donut(tvc, "Status", "Count", "Default Percentage"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    age_dr = (f.groupby("AGE_GROUP", observed=True)["TARGET"].mean() * 100).reset_index()
    age_dr.columns = ["Age Group", "Default Rate %"]
    st.plotly_chart(ch.bar(age_dr, "Age Group", "Default Rate %", "Default Rate by Age Group"), use_container_width=True)
with col4:
    inc_dr = (f.groupby("INCOME_GROUP", observed=True)["TARGET"].mean() * 100).reset_index()
    inc_dr.columns = ["Income Group", "Default Rate %"]
    st.plotly_chart(ch.bar(inc_dr, "Income Group", "Default Rate %", "Default Rate by Income Group"), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    emp_dr = (f.groupby("EMPLOYMENT_GROUP")["TARGET"].mean() * 100).reset_index()
    emp_dr.columns = ["Employment Group", "Default Rate %"]
    st.plotly_chart(ch.bar(emp_dr, "Employment Group", "Default Rate %", "Default Rate by Employment Group"), use_container_width=True)
with col6:
    edu_dr = (f.groupby("NAME_EDUCATION_TYPE")["TARGET"].mean() * 100).sort_values(ascending=False).reset_index()
    edu_dr.columns = ["Education", "Default Rate %"]
    st.plotly_chart(ch.bar(edu_dr, "Education", "Default Rate %", "Default Rate by Education", horizontal=True), use_container_width=True)

col7, col8 = st.columns(2)
with col7:
    occ_dr = (f.groupby("OCCUPATION_TYPE")["TARGET"].mean() * 100).sort_values(ascending=False).reset_index()
    occ_dr.columns = ["Occupation", "Default Rate %"]
    st.plotly_chart(ch.bar(occ_dr, "Occupation", "Default Rate %", "Default Rate by Occupation", horizontal=True), use_container_width=True)
with col8:
    ct_dr = f.groupby(["NAME_CONTRACT_TYPE", "TARGET"]).size().reset_index(name="Count")
    ct_dr["TARGET"] = ct_dr["TARGET"].map({0: "Non-Default", 1: "Default"})
    st.plotly_chart(ch.grouped_bar(ct_dr, "NAME_CONTRACT_TYPE", "Count", "TARGET", "Default by Contract Type"), use_container_width=True)

st.subheader("Detailed Data Table")
st.dataframe(f.head(500), use_container_width=True)
st.download_button("Download Filtered Dataset (CSV)", f.to_csv(index=False).encode(), "default_risk_filtered.csv", "text/csv")

st.subheader("Required Insight: Count vs Rate")
biggest_age_group = f["AGE_GROUP"].value_counts().idxmax()
st.markdown(f"""
A large group can contain many raw defaults simply because it contains many customers overall. For example,
**{biggest_age_group}** is the single largest age group by customer count, so it may show a high *absolute* number
of defaults — but that does not necessarily mean it has the highest *default rate*. The charts above therefore
report **default rate (%)** by group, not raw default counts, to avoid this size bias.
""")
