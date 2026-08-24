import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.data_loader import load_application_train
from utils.feature_engineering import engineer_application_features
from utils import charts as ch
from utils.metrics import fmt_number, value_counts_df
from utils.filters import apply_common_filters

st.set_page_config(page_title="Customer Demographics", page_icon="🏦", layout="wide")
st.title("05 · Customer Demographic Analysis")
st.caption("Business Objective: understand who the Home Credit customers actually are.")

df = engineer_application_features(load_application_train())
f = apply_common_filters(df)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Average Age", f"{f['AGE_YEARS'].mean():.1f} yrs")
c2.metric("Median Age", f"{f['AGE_YEARS'].median():.1f} yrs")
c3.metric("Most Common Gender", f["CODE_GENDER"].mode()[0])
c4.metric("Most Common Education", f["NAME_EDUCATION_TYPE"].mode()[0].split(" ")[0])
c5.metric("Most Common Income Type", f["NAME_INCOME_TYPE"].mode()[0])
c6.metric("Most Common Family Status", f["NAME_FAMILY_STATUS"].mode()[0])

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ch.histogram(f, "AGE_YEARS", "Age Distribution"), use_container_width=True)
with col2:
    gvc = value_counts_df(f, "CODE_GENDER")
    st.plotly_chart(ch.donut(gvc, "CODE_GENDER", "Count", "Gender Distribution"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    edu = value_counts_df(f, "NAME_EDUCATION_TYPE")
    st.plotly_chart(ch.bar(edu, "NAME_EDUCATION_TYPE", "Count", "Education Distribution", horizontal=True), use_container_width=True)
with col4:
    fam = value_counts_df(f, "NAME_FAMILY_STATUS")
    st.plotly_chart(ch.bar(fam, "NAME_FAMILY_STATUS", "Count", "Family Status Distribution"), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    inc = value_counts_df(f, "NAME_INCOME_TYPE")
    st.plotly_chart(ch.bar(inc, "NAME_INCOME_TYPE", "Count", "Income Type Distribution", horizontal=True), use_container_width=True)
with col6:
    age_gender = f.groupby(["AGE_GROUP", "CODE_GENDER"], observed=True).size().reset_index(name="Count")
    st.plotly_chart(ch.grouped_bar(age_gender, "AGE_GROUP", "Count", "CODE_GENDER", "Age Group by Gender"), use_container_width=True)

sample = f.sample(min(5000, len(f)), random_state=1)
st.plotly_chart(ch.scatter(sample, "AGE_YEARS", "AMT_INCOME_TOTAL", "Age vs Income"), use_container_width=True)

st.subheader("Detailed Data Table")
st.dataframe(f.head(500), use_container_width=True)
st.download_button("Download Filtered Dataset (CSV)", f.to_csv(index=False).encode(), "demographics_filtered.csv", "text/csv")

st.subheader("Key Observations")
st.markdown(f"""
- The typical Home Credit customer is around **{f['AGE_YEARS'].median():.0f} years old**, working, with
  **{f['NAME_EDUCATION_TYPE'].mode()[0]}** education.
- **{f['NAME_FAMILY_STATUS'].mode()[0]}** is the most common family status in the portfolio.
- Gender split: {value_counts_df(f, 'CODE_GENDER').to_dict('records')}.
""")

st.subheader("Business Recommendations")
st.markdown("""
1. Tailor communication/marketing content to the dominant education and income-type segments identified above.
2. Track whether age or family-status segments are under-represented relative to the addressable market.
3. Use demographic segments as a cross-cut lens on later risk pages rather than analysing risk in isolation.
""")
