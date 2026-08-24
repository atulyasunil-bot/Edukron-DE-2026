import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from utils.data_loader import load_application_train
from utils.feature_engineering import engineer_application_features
from utils.preprocessing import outlier_summary
from utils import charts as ch
from utils.metrics import fmt_number, fmt_currency

st.set_page_config(page_title="Outlier & Distribution Analysis", page_icon="🏦", layout="wide")
st.title("04 · Outlier & Distribution Analysis")
st.caption("Business Objective: flag unusual numerical values before they distort downstream EDA — without blindly deleting them.")

df = engineer_application_features(load_application_train())

VARS = ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE",
        "DAYS_BIRTH", "DAYS_EMPLOYED", "CNT_CHILDREN", "CNT_FAM_MEMBERS"]
VARS = [v for v in VARS if v in df.columns]

summary = outlier_summary(df, VARS)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Numerical Columns Checked", fmt_number(len(VARS)))
c2.metric("Variables with Outliers", fmt_number((summary["Outlier Count"] > 0).sum()))
c3.metric("Maximum Income", fmt_currency(df["AMT_INCOME_TOTAL"].max()))
c4.metric("Maximum Credit", fmt_currency(df["AMT_CREDIT"].max()))
c5.metric("Maximum Annuity", fmt_currency(df["AMT_ANNUITY"].max()))

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ch.histogram(df, "AMT_INCOME_TOTAL", "Income Distribution"), use_container_width=True)
with col2:
    st.plotly_chart(ch.box(df, y="AMT_INCOME_TOTAL", title="Income Outliers (Box Plot)"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(ch.box(df, y="AMT_CREDIT", title="Credit Amount Outliers (Box Plot)"), use_container_width=True)
with col4:
    st.plotly_chart(ch.box(df, y="AMT_ANNUITY", title="Annuity Outliers (Box Plot)"), use_container_width=True)

col5 = st.container()
sample = df.sample(min(5000, len(df)), random_state=1)
st.plotly_chart(ch.scatter(sample, "AMT_INCOME_TOTAL", "AMT_CREDIT", "Income vs Credit (sampled)"), use_container_width=True)

st.subheader("IQR-Based Outlier Summary Table")
st.dataframe(summary, use_container_width=True)

st.subheader("Techniques Considered")
st.markdown("""
- **IQR Method** — used above to flag values beyond `Q1 - 1.5*IQR` / `Q3 + 1.5*IQR`; flagged, not removed.
- **Percentile Capping / Winsorization** — recommended for `AMT_INCOME_TOTAL`, which has a small number of extreme
  high-income applicants that would otherwise dominate mean-based KPIs.
- **Log Transformation** — recommended when visualising `AMT_CREDIT` / `AMT_INCOME_TOTAL` distributions, since both
  are strongly right-skewed.
- **Business-rule validation** — `DAYS_EMPLOYED` contains a known sentinel value (365243) used by Home Credit to
  mark pensioners/unemployed applicants; this is a **data-entry convention**, not a true outlier, and is corrected
  in the feature-engineering step rather than capped statistically.
""")

st.subheader("Classifying Flagged Values")
st.markdown("""
| Pattern | Classification | Action |
|---|---|---|
| A handful of very high `AMT_INCOME_TOTAL` values (multi-million) | True extreme customer | Keep, but cap for chart scaling only |
| `DAYS_EMPLOYED = 365243` | Data entry / sentinel issue | Recode to NaN, engineer "Unemployed / Special" category |
| `CNT_CHILDREN` > 10 | Potential invalid value | Flag for manual review, do not silently drop |
| `AMT_ANNUITY` outliers aligned with equally high `AMT_CREDIT` | Consistent, not anomalous | Keep as-is |
""")
