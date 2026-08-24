import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.data_loader import load_application_train
from utils.feature_engineering import engineer_application_features
from utils import charts as ch
from utils.metrics import fmt_number, fmt_pct
from utils.filters import apply_common_filters

st.set_page_config(page_title="Credit Affordability", page_icon="🏦", layout="wide")
st.title("10 · Credit Affordability Analysis")
st.caption("Business Objective: check whether credit amounts granted are proportionate to applicant income.")

df = engineer_application_features(load_application_train())
f = apply_common_filters(df)

HIGH_CREDIT_BURDEN = 5   # credit-to-income ratio threshold used only for descriptive flagging, explained below
HIGH_ANNUITY_BURDEN = 0.5  # annuity-to-income ratio threshold

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Avg Credit-to-Income", f"{f['CREDIT_TO_INCOME'].mean():.2f}")
c2.metric("Median Credit-to-Income", f"{f['CREDIT_TO_INCOME'].median():.2f}")
c3.metric("Avg Annuity-to-Income", f"{f['ANNUITY_TO_INCOME'].mean():.2f}")
c4.metric("High Credit-Burden Customers", fmt_number((f["CREDIT_TO_INCOME"] > HIGH_CREDIT_BURDEN).sum()))
c5.metric("High Annuity-Burden Customers", fmt_number((f["ANNUITY_TO_INCOME"] > HIGH_ANNUITY_BURDEN).sum()))

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ch.histogram(f, "CREDIT_TO_INCOME", "Credit-to-Income Distribution"), use_container_width=True)
with col2:
    st.plotly_chart(ch.histogram(f, "ANNUITY_TO_INCOME", "Annuity-to-Income Distribution"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(ch.box(f, x="TARGET", y="CREDIT_TO_INCOME", title="Credit-to-Income by Default Status"), use_container_width=True)
with col4:
    sample = f.sample(min(5000, len(f)), random_state=1)
    st.plotly_chart(ch.scatter(sample, "AMT_INCOME_TOTAL", "AMT_CREDIT", "Income vs Credit"), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    burden_by_income = f.groupby("INCOME_GROUP", observed=True)["CREDIT_TO_INCOME"].mean().reset_index()
    st.plotly_chart(ch.bar(burden_by_income, "INCOME_GROUP", "CREDIT_TO_INCOME", "Avg Credit Burden by Income Group"), use_container_width=True)
with col6:
    burden_by_age = f.groupby("AGE_GROUP", observed=True)["ANNUITY_TO_INCOME"].mean().reset_index()
    st.plotly_chart(ch.bar(burden_by_age, "AGE_GROUP", "ANNUITY_TO_INCOME", "Avg Annuity Burden by Age Group"), use_container_width=True)

st.subheader("Detailed Data Table")
st.dataframe(f.head(500), use_container_width=True)
st.download_button("Download Filtered Dataset (CSV)", f.to_csv(index=False).encode(), "affordability_filtered.csv", "text/csv")

st.subheader("Recommendations")
st.markdown(f"""
- Thresholds of **credit-to-income > {HIGH_CREDIT_BURDEN}** and **annuity-to-income > {HIGH_ANNUITY_BURDEN}** are
  used here purely as *descriptive flags* to size the potentially-stretched segment, not as an approval rule.
- Customers whose `TARGET=1` group shows a visibly higher median credit-to-income ratio (see box plot) suggests
  affordability ratios are worth adding to manual review checklists.
- Combine credit burden with income group — high-burden customers concentrated in "Very Low"/"Low" income groups
  are the highest-priority segment for affordability review.
""")
