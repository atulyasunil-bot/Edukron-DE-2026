import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from utils.data_loader import load_application_train, load_bureau, load_pos_cash
from utils.feature_engineering import engineer_application_features, aggregate_bureau_features, aggregate_pos_cash_features
from utils.metrics import fmt_number, fmt_pct, fmt_currency

st.set_page_config(page_title="Executive Insights & Recommendations", page_icon="🏦", layout="wide")
st.title("20 · Executive Insights & Business Recommendations")
st.caption("A management summary drawing on all previous pages — conclusions, not exploratory charts.")

df = engineer_application_features(load_application_train())
bureau_agg = aggregate_bureau_features(load_bureau())
pos_agg = aggregate_pos_cash_features(load_pos_cash())
df = df.merge(bureau_agg, on="SK_ID_CURR", how="left").merge(pos_agg, on="SK_ID_CURR", how="left")
df["TOTAL_BUREAU_DEBT"] = df["TOTAL_BUREAU_DEBT"].fillna(0)
df["MAX_DPD"] = df["MAX_DPD"].fillna(0)
df["CREDIT_UTIL_HIGH"] = False  # credit_card_balance.csv not available in this upload set

high_burden = (df["ANNUITY_TO_INCOME"] > df["ANNUITY_TO_INCOME"].quantile(0.75)).sum()
late_customers = (df["MAX_DPD"] > 0).sum()
bureau_debt_customers = (df["TOTAL_BUREAU_DEBT"] > 0).sum()

st.subheader("Executive KPIs")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Customers", fmt_number(len(df)))
c2.metric("Default Rate", fmt_pct(df["TARGET"].mean() * 100))
c3.metric("Total Credit Exposure", fmt_currency(df["AMT_CREDIT"].sum()))
c4.metric("Average Credit", fmt_currency(df["AMT_CREDIT"].mean()))
c5.metric("Average Income", fmt_currency(df["AMT_INCOME_TOTAL"].mean()))

c6, c7, c8, c9 = st.columns(4)
c6.metric("High Annuity-Burden Customers", fmt_number(high_burden))
c7.metric("Customers with POS/CASH DPD History", fmt_number(late_customers))
c8.metric("Customers with Bureau Debt", fmt_number(bureau_debt_customers))
c9.metric("Customers in Elevated/High Risk (see pg 19)", "See page 19")

st.divider()
st.subheader("Top 10 Portfolio Insights")

top_income_default = (df.groupby("INCOME_GROUP", observed=True)["TARGET"].mean() * 100).idxmax()
top_emp_default = (df.groupby("EMPLOYMENT_GROUP")["TARGET"].mean() * 100).idxmax()
top_occ_default = (df.groupby("OCCUPATION_TYPE")["TARGET"].mean() * 100).idxmax()
top_edu_default = (df.groupby("NAME_EDUCATION_TYPE")["TARGET"].mean() * 100).idxmax()
median_cti = df["CREDIT_TO_INCOME"].median()

st.markdown(f"""
1. Customers in the **{top_emp_default}** employment group show the highest observed default rate across the
   portfolio — employment tenure is a meaningful, monitorable signal.
2. The **{top_income_default}** income group carries the highest observed default rate among income segments,
   suggesting affordability stress concentrates there.
3. Occupation **{top_occ_default}** shows a notably different repayment pattern than the portfolio average.
4. Education level **{top_edu_default}** is associated with a higher observed default rate than other education
   groups.
5. The typical (median) credit-to-income ratio across the portfolio is **{median_cti:.2f}x** income — a useful
   affordability benchmark for manual review triggers.
6. **{fmt_number(bureau_debt_customers)}** customers carry existing external bureau debt, meaning affordability
   assessments should account for obligations beyond the current application.
7. **{fmt_number(late_customers)}** customers have at least one recorded days-past-due event in their POS/CASH
   history — a group worth proactive monitoring even where current status looks fine.
8. Application volume and credit sizing vary meaningfully by contract type (see page 09), which should inform
   channel-specific operational planning.
9. Age-group and family-size cross-cuts (pages 05, 08, 11) show default rate is not evenly distributed across
   demographics, supporting segment-specific review policies rather than one-size-fits-all rules.
10. The rule-based EDA risk segments (page 19) directionally align with observed default rates, supporting their
    use as a lightweight, explainable early-warning lens pending any future modelling work.
""")

st.subheader("Business Recommendations (15+)")
st.markdown("""
**Affordability**
1. Flag customers whose credit-to-income ratio sits above the portfolio's 75th percentile for manual affordability review.
2. Monitor customers with unusually high annuity-to-income burden as a distinct watch list.
3. Use income-per-family-member, not raw income, when assessing household affordability.

**Repayment**
4. Build an early-warning report for customers with repeated late POS/CASH installments.
5. Track customers whose payment delay trend is worsening month over month (once installments_payments.csv is available).
6. Treat any non-zero days-past-due history as a persistent flag, not something that resets once resolved.

**Bureau**
7. Review customers holding multiple active external credit lines concurrently.
8. Prioritise review of customers with non-zero bureau overdue amounts, regardless of size.
9. Incorporate bureau-derived total debt into affordability calculations alongside the current application.

**Credit Cards** *(pending credit_card_balance.csv)*
10. Once available, monitor customers consistently near their credit limit (high utilization) as a stress signal.

**Employment**
11. Include employment stability/tenure explicitly in manual-review dashboards, not just income.
12. Separate "Unemployed/Special" pensioners from genuinely unemployed applicants for differentiated treatment.

**Data Quality**
13. Improve collection of high-missing-value fields with business importance identified on page 03 (e.g. building/apartment quality fields, occupation type).
14. Standardise sentinel values (e.g. `DAYS_EMPLOYED = 365243`) at the source system level to avoid repeated ad-hoc cleaning.

**Portfolio Monitoring**
15. Develop a monthly dashboard tracking risk-segment movement (page 19) so shifts in the portfolio's risk mix are caught early.
16. Re-baseline percentile thresholds used for descriptive flags (credit-to-income, annuity-to-income) periodically as portfolio composition changes.
""")
