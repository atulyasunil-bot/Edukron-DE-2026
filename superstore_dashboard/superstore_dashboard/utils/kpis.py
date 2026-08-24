import streamlit as st
import pandas as pd


def money(x):
    return f"${x:,.0f}" if pd.notna(x) else "N/A"


def show_kpi_row(kpi_dict: dict):
    """kpi_dict: {label: value_string}"""
    cols = st.columns(len(kpi_dict))
    for col, (label, value) in zip(cols, kpi_dict.items()):
        col.metric(label, value)


def core_kpis(df: pd.DataFrame) -> dict:
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order ID"].nunique()
    total_customers = df["Customer ID"].nunique()
    margin = (total_profit / total_sales * 100) if total_sales else 0
    return {
        "Total Sales": money(total_sales),
        "Total Profit": money(total_profit),
        "Total Orders": f"{total_orders:,}",
        "Total Customers": f"{total_customers:,}",
        "Profit Margin %": f"{margin:.1f}%",
    }
