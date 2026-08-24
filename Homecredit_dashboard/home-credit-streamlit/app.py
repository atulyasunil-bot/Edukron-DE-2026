"""
app.py
-------
Home / landing page of the Home Credit 20-Page EDA & Preprocessing Streamlit
application.

Run with:  streamlit run app.py
"""

import streamlit as st
from utils.data_loader import available_files

st.set_page_config(
    page_title="Home Credit Analytics",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 Home Credit — 20-Page EDA & Preprocessing Dashboard")

st.markdown(
    """
Welcome. This application is a **pure exploratory data analysis, data-cleaning
and feature-engineering** dashboard built on the Home Credit Default Risk
dataset.
"""
)

st.divider()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.subheader("📊 Portfolio & Data Quality")
    st.markdown("""
- 01 · Executive Portfolio Overview
- 02 · Data Quality Dashboard
- 03 · Missing Value Analysis
- 04 · Outlier & Distribution Analysis
""")
with col2:
    st.subheader("👤 Customer Profile")
    st.markdown("""
- 05 · Customer Demographics
- 06 · Income Analysis
- 07 · Employment Analysis
- 08 · Family & Housing Analysis
""")
with col3:
    st.subheader("💳 Loan & Risk")
    st.markdown("""
- 09 · Current Loan Application Analysis
- 10 · Credit Affordability Analysis
- 11 · Default Risk EDA
- 12 · Risk Factor Exploration
""")
with col4:
    st.subheader("🏛️ Bureau & History")
    st.markdown("""
- 13 · Bureau Credit History
- 14 · Bureau Balance Analysis
- 15 · Previous Applications *(optional file)*
- 16 · POS / CASH Loan Analysis
""")

col5, col6 = st.columns(2)
with col5:
    st.subheader("💰 Repayment")
    st.markdown("""
- 17 · Installment Payment Analysis *(optional file)*
- 18 · Credit Card Balance Analysis *(optional file)*
""")
with col6:
    st.subheader("🎯 Segmentation & Insights")
    st.markdown("""
- 19 · Customer Risk Segmentation (rule-based)
- 20 · Executive Insights & Recommendations
""")

st.divider()
st.subheader("Dataset availability check")
files = available_files()
cols = st.columns(4)
for i, (name, present) in enumerate(files.items()):
    with cols[i % 4]:
        st.metric(name, "✅ Found" if present else "⚠️ Not uploaded")

st.info(
    "Pages 15, 17 and 18 rely on `previous_application.csv`, "
    "`installments_payments.csv` and `credit_card_balance.csv`, which were not "
    "part of the uploaded file set. Those pages display clear placeholders and "
    "instructions for the corresponding CSV instead of failing."
)
