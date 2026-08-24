"""
filters.py
-----------
Common sidebar filter widgets shared across pages. Each function returns the
filtered dataframe so pages can chain multiple filters together.
"""

import streamlit as st


def multiselect_filter(df, col, label=None, key=None):
    if col not in df.columns:
        return df
    options = sorted(df[col].dropna().unique().tolist())
    label = label or col.replace("_", " ").title()
    selected = st.sidebar.multiselect(label, options, default=[], key=key or col)
    if selected:
        return df[df[col].isin(selected)]
    return df


def range_filter(df, col, label=None, key=None):
    if col not in df.columns or df[col].dropna().empty:
        return df
    label = label or col.replace("_", " ").title()
    lo, hi = float(df[col].min()), float(df[col].max())
    if lo == hi:
        return df
    selected = st.sidebar.slider(label, lo, hi, (lo, hi), key=key or col)
    return df[(df[col] >= selected[0]) & (df[col] <= selected[1])]


def target_filter(df, key="target_filter"):
    if "TARGET" not in df.columns:
        return df
    choice = st.sidebar.radio("Default Status", ["All", "Non-Default (0)", "Default (1)"], key=key)
    if choice == "Non-Default (0)":
        return df[df["TARGET"] == 0]
    elif choice == "Default (1)":
        return df[df["TARGET"] == 1]
    return df


def apply_common_filters(df):
    """Applies the standard sidebar filter set used on most application-level pages."""
    st.sidebar.markdown("### Filters")
    filtered = df.copy()
    if "CODE_GENDER" in filtered.columns:
        filtered = multiselect_filter(filtered, "CODE_GENDER", "Gender")
    if "AGE_GROUP" in filtered.columns:
        filtered = multiselect_filter(filtered, "AGE_GROUP", "Age Group")
    if "INCOME_GROUP" in filtered.columns:
        filtered = multiselect_filter(filtered, "INCOME_GROUP", "Income Group")
    if "NAME_EDUCATION_TYPE" in filtered.columns:
        filtered = multiselect_filter(filtered, "NAME_EDUCATION_TYPE", "Education")
    if "NAME_FAMILY_STATUS" in filtered.columns:
        filtered = multiselect_filter(filtered, "NAME_FAMILY_STATUS", "Family Status")
    if "NAME_CONTRACT_TYPE" in filtered.columns:
        filtered = multiselect_filter(filtered, "NAME_CONTRACT_TYPE", "Contract Type")
    filtered = target_filter(filtered)
    st.sidebar.markdown(f"**{len(filtered):,} / {len(df):,} rows selected**")
    return filtered
