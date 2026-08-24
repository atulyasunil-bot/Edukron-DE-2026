"""
preprocessing.py
-----------------
Reusable, side-effect-free data-quality helper functions used across pages:
missing values, duplicates, dtype summaries, outlier flags.
No model training happens anywhere in this file.
"""

import numpy as np
import pandas as pd


def missing_value_table(df: pd.DataFrame) -> pd.DataFrame:
    """Column-wise missing count / percentage, sorted descending."""
    miss = df.isnull().sum()
    pct = (miss / len(df)) * 100
    out = pd.DataFrame({"Column": miss.index, "Missing Count": miss.values, "Missing %": pct.values.round(2)})
    out = out[out["Missing Count"] > 0].sort_values("Missing %", ascending=False).reset_index(drop=True)
    return out


def missing_bucket(pct: float) -> str:
    if pct == 0:
        return "0% Missing"
    elif pct <= 5:
        return "0-5% Missing"
    elif pct <= 20:
        return "5-20% Missing"
    elif pct <= 40:
        return "20-40% Missing"
    elif pct <= 60:
        return "40-60% Missing"
    else:
        return "60%+ Missing"


def dtype_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        s = df[col]
        row = {
            "Column": col,
            "Data Type": str(s.dtype),
            "Missing Count": int(s.isnull().sum()),
            "Missing %": round(s.isnull().mean() * 100, 2),
            "Unique Values": int(s.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(s):
            row["Minimum"] = s.min()
            row["Maximum"] = s.max()
            row["Mean"] = round(s.mean(), 2) if pd.notnull(s.mean()) else np.nan
            row["Median"] = s.median()
        else:
            row["Minimum"] = row["Maximum"] = row["Mean"] = row["Median"] = np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def duplicate_summary(df: pd.DataFrame, id_col: str = None) -> dict:
    out = {"full_row_duplicates": int(df.duplicated().sum())}
    if id_col and id_col in df.columns:
        out["duplicate_ids"] = int(df[id_col].duplicated().sum())
        out["unique_ids"] = int(df[id_col].nunique())
    return out


def iqr_outlier_flags(series: pd.Series, k: float = 1.5) -> pd.Series:
    """Returns boolean mask of IQR-based outliers. Does not remove anything."""
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return (series < lower) | (series > upper)


def outlier_summary(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    rows = []
    for c in cols:
        if c not in df.columns:
            continue
        s = df[c].dropna()
        if s.empty or not pd.api.types.is_numeric_dtype(s):
            continue
        mask = iqr_outlier_flags(s)
        rows.append({
            "Column": c,
            "Outlier Count": int(mask.sum()),
            "Outlier %": round(mask.mean() * 100, 2),
            "Q1": s.quantile(0.25),
            "Q3": s.quantile(0.75),
            "Min": s.min(),
            "Max": s.max(),
        })
    return pd.DataFrame(rows)
