"""
metrics.py
-----------
Number formatting + small statistical helpers reused for KPI cards.
"""

import pandas as pd
import numpy as np


def fmt_currency(x, symbol="$"):
    if pd.isna(x):
        return "N/A"
    if abs(x) >= 1_000_000:
        return f"{symbol}{x/1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"{symbol}{x/1_000:.1f}K"
    return f"{symbol}{x:,.0f}"


def fmt_pct(x, decimals=2):
    if pd.isna(x):
        return "N/A"
    return f"{x:.{decimals}f}%"


def fmt_number(x):
    if pd.isna(x):
        return "N/A"
    return f"{x:,.0f}"


def default_rate(df, group_col=None):
    """Overall or group-wise default rate (%) from TARGET column."""
    if "TARGET" not in df.columns:
        return None
    if group_col is None:
        return round(df["TARGET"].mean() * 100, 2)
    return (df.groupby(group_col)["TARGET"].mean() * 100).round(2).reset_index(name="Default Rate %")


def value_counts_df(df, col, top_n=None):
    vc = df[col].value_counts(dropna=True).reset_index()
    vc.columns = [col, "Count"]
    if top_n:
        vc = vc.head(top_n)
    return vc
