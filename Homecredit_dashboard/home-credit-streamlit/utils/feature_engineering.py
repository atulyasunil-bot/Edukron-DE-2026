"""
feature_engineering.py
------------------------
Pure, deterministic feature-engineering functions. Nothing here trains a model -
these only derive descriptive / ratio features used throughout the EDA pages.
"""

import numpy as np
import pandas as pd


def add_age_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "DAYS_BIRTH" in df.columns:
        df["AGE_YEARS"] = (-df["DAYS_BIRTH"] / 365.25).round(1)
        bins = [0, 30, 40, 50, 60, 200]
        labels = ["20-30", "31-40", "41-50", "51-60", "60+"]
        df["AGE_GROUP"] = pd.cut(df["AGE_YEARS"], bins=bins, labels=labels)
    return df


def add_employment_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "DAYS_EMPLOYED" in df.columns:
        # 365243 is HomeCredit's known "not employed / pensioner" sentinel value
        clean = df["DAYS_EMPLOYED"].replace(365243, np.nan)
        df["EMPLOYMENT_YEARS"] = (-clean / 365.25).round(1)

        def bucket(y):
            if pd.isna(y):
                return "Unemployed / Special"
            if y < 1:
                return "<1 Year"
            elif y < 3:
                return "1-3 Years"
            elif y < 5:
                return "3-5 Years"
            elif y < 10:
                return "5-10 Years"
            elif y < 20:
                return "10-20 Years"
            else:
                return "20+ Years"

        df["EMPLOYMENT_GROUP"] = df["EMPLOYMENT_YEARS"].apply(bucket)
    return df


def add_income_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "AMT_INCOME_TOTAL" in df.columns:
        try:
            df["INCOME_GROUP"] = pd.qcut(
                df["AMT_INCOME_TOTAL"], q=5,
                labels=["Very Low", "Low", "Middle", "High", "Very High"],
                duplicates="drop",
            )
        except ValueError:
            df["INCOME_GROUP"] = "Middle"
        if "CNT_FAM_MEMBERS" in df.columns:
            df["INCOME_PER_FAMILY_MEMBER"] = df["AMT_INCOME_TOTAL"] / df["CNT_FAM_MEMBERS"].replace(0, np.nan)
        if "CNT_CHILDREN" in df.columns:
            df["INCOME_PER_CHILD"] = df["AMT_INCOME_TOTAL"] / df["CNT_CHILDREN"].replace(0, np.nan)
    return df


def add_affordability_ratios(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if {"AMT_CREDIT", "AMT_INCOME_TOTAL"}.issubset(df.columns):
        df["CREDIT_TO_INCOME"] = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"].replace(0, np.nan)
    if {"AMT_ANNUITY", "AMT_INCOME_TOTAL"}.issubset(df.columns):
        df["ANNUITY_TO_INCOME"] = df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"].replace(0, np.nan)
    if {"AMT_GOODS_PRICE", "AMT_INCOME_TOTAL"}.issubset(df.columns):
        df["GOODS_TO_INCOME"] = df["AMT_GOODS_PRICE"] / df["AMT_INCOME_TOTAL"].replace(0, np.nan)
    if {"AMT_CREDIT", "AMT_GOODS_PRICE"}.issubset(df.columns):
        df["CREDIT_TO_GOODS"] = df["AMT_CREDIT"] / df["AMT_GOODS_PRICE"].replace(0, np.nan)
    return df


def engineer_application_features(df: pd.DataFrame) -> pd.DataFrame:
    """Applies the full mandatory feature-engineering pipeline to an application table."""
    df = add_age_features(df)
    df = add_employment_features(df)
    df = add_income_features(df)
    df = add_affordability_ratios(df)
    return df


def aggregate_bureau_features(bureau: pd.DataFrame) -> pd.DataFrame:
    """Customer-level (SK_ID_CURR) aggregates from bureau.csv."""
    g = bureau.groupby("SK_ID_CURR")
    agg = g.agg(
        BUREAU_ACCOUNT_COUNT=("SK_ID_BUREAU", "count"),
        ACTIVE_BUREAU_COUNT=("CREDIT_ACTIVE", lambda x: (x == "Active").sum()),
        CLOSED_BUREAU_COUNT=("CREDIT_ACTIVE", lambda x: (x == "Closed").sum()),
        TOTAL_BUREAU_CREDIT=("AMT_CREDIT_SUM", "sum"),
        TOTAL_BUREAU_DEBT=("AMT_CREDIT_SUM_DEBT", "sum"),
        AVG_BUREAU_CREDIT=("AMT_CREDIT_SUM", "mean"),
        MAX_BUREAU_OVERDUE=("AMT_CREDIT_SUM_OVERDUE", "max"),
        TOTAL_BUREAU_OVERDUE=("AMT_CREDIT_SUM_OVERDUE", "sum"),
    ).reset_index()
    return agg


def aggregate_pos_cash_features(pos: pd.DataFrame) -> pd.DataFrame:
    """Customer-level (SK_ID_CURR) aggregates from POS_CASH_balance.csv."""
    g = pos.groupby("SK_ID_CURR")
    agg = g.agg(
        POS_RECORD_COUNT=("SK_ID_PREV", "count"),
        AVG_DPD=("SK_DPD", "mean"),
        MAX_DPD=("SK_DPD", "max"),
        TOTAL_DPD_EVENTS=("SK_DPD", lambda x: (x > 0).sum()),
        AVG_INSTALMENTS_REMAINING=("CNT_INSTALMENT_FUTURE", "mean"),
        COMPLETED_CONTRACTS=("NAME_CONTRACT_STATUS", lambda x: (x == "Completed").sum()),
    ).reset_index()
    return agg
