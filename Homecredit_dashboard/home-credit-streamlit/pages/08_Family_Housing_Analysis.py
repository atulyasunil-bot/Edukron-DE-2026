import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.data_loader import load_application_train
from utils.feature_engineering import engineer_application_features
from utils import charts as ch
from utils.metrics import fmt_pct, fmt_currency
from utils.filters import apply_common_filters

st.set_page_config(page_title="Family & Housing Analysis", page_icon="🏦", layout="wide")
st.title("08 · Family & Housing Analysis")
st.caption("Business Objective: study household composition and living situation as affordability context.")

df = engineer_application_features(load_application_train())
f = apply_common_filters(df)

home_own_pct = (f["NAME_HOUSING_TYPE"] == "House / apartment").mean() * 100
car_own_pct = (f["FLAG_OWN_CAR"] == "Y").mean() * 100

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Average Family Size", f"{f['CNT_FAM_MEMBERS'].mean():.2f}")
c2.metric("Average Number of Children", f"{f['CNT_CHILDREN'].mean():.2f}")
c3.metric("Home Ownership %", fmt_pct(home_own_pct))
c4.metric("Car Ownership %", fmt_pct(car_own_pct))
c5.metric("Most Common Housing Type", f["NAME_HOUSING_TYPE"].mode()[0])

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ch.histogram(f, "CNT_FAM_MEMBERS", "Family Size Distribution", nbins=15), use_container_width=True)
with col2:
    ch_vc = f["CNT_CHILDREN"].value_counts().reset_index()
    ch_vc.columns = ["Children", "Count"]
    st.plotly_chart(ch.bar(ch_vc.head(10), "Children", "Count", "Children Distribution"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    ht = f["NAME_HOUSING_TYPE"].value_counts().reset_index()
    ht.columns = ["Housing Type", "Count"]
    st.plotly_chart(ch.bar(ht, "Housing Type", "Count", "Housing Type Distribution"), use_container_width=True)
with col4:
    realty = f["FLAG_OWN_REALTY"].value_counts().reset_index()
    realty.columns = ["Owns Realty", "Count"]
    st.plotly_chart(ch.donut(realty, "Owns Realty", "Count", "Property Ownership"), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    car = f["FLAG_OWN_CAR"].value_counts().reset_index()
    car.columns = ["Owns Car", "Count"]
    st.plotly_chart(ch.donut(car, "Owns Car", "Count", "Car Ownership"), use_container_width=True)
with col6:
    st.plotly_chart(ch.box(f, x="CNT_FAM_MEMBERS", y="AMT_INCOME_TOTAL", title="Family Size vs Income"), use_container_width=True)

fam_dr = (f.groupby("CNT_FAM_MEMBERS")["TARGET"].mean() * 100).reset_index()
fam_dr.columns = ["Family Size", "Default Rate %"]
fam_dr = fam_dr[fam_dr["Family Size"] <= 10]
st.plotly_chart(ch.line(fam_dr, "Family Size", "Default Rate %", "Family Size vs Default Rate"), use_container_width=True)

st.subheader("Detailed Data Table")
st.dataframe(f.head(500), use_container_width=True)
st.download_button("Download Filtered Dataset (CSV)", f.to_csv(index=False).encode(), "family_housing_filtered.csv", "text/csv")

st.subheader("Key Observations")
st.markdown(f"""
- Average household has **{f['CNT_FAM_MEMBERS'].mean():.1f}** members and **{f['CNT_CHILDREN'].mean():.1f}**
  children.
- **{fmt_pct(home_own_pct)}** of applicants live in a "House / apartment" housing type; **{fmt_pct(car_own_pct)}**
  own a car.
- Median **income per family member** is **{fmt_currency(f['INCOME_PER_FAMILY_MEMBER'].median())}**, a useful
  affordability lens beyond raw household income.
""")

st.subheader("Recommendations")
st.markdown("""
1. Use income-per-family-member (not raw income) when assessing affordability for larger households.
2. Track whether housing type correlates with repayment stress in the risk-segmentation page (19).
3. Consider separate underwriting guidance for renters vs. homeowners given differing fixed-cost burdens.
""")
