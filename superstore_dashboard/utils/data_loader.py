import pandas as pd
import streamlit as st
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_superstore.csv")


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Load and lightly clean the Superstore dataset."""
    df = pd.read_csv(path, parse_dates=["Order Date", "Ship Date"])

    # Standardize column names some Superstore exports use
    rename_map = {
        "Country/Region": "Country",
        "State/Province": "State",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"] = pd.to_datetime(df["Ship Date"])
    df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
    df["Order Year"] = df["Order Date"].dt.year
    df["Order Month"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Order Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
    df["Profit Margin"] = (df["Profit"] / df["Sales"].replace(0, pd.NA)) * 100
    return df


def apply_common_filters(df: pd.DataFrame, sidebar) -> pd.DataFrame:
    """Apply the shared sidebar filters used across most pages."""
    min_d, max_d = df["Order Date"].min(), df["Order Date"].max()
    date_range = sidebar.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    regions = sidebar.multiselect("Region", sorted(df["Region"].dropna().unique()))
    states = sidebar.multiselect("State", sorted(df["State"].dropna().unique()))
    segments = sidebar.multiselect("Segment", sorted(df["Segment"].dropna().unique()))
    categories = sidebar.multiselect("Category", sorted(df["Category"].dropna().unique()))
    subcats = sidebar.multiselect("Sub-Category", sorted(df["Sub-Category"].dropna().unique()))
    ship_modes = sidebar.multiselect("Ship Mode", sorted(df["Ship Mode"].dropna().unique()))

    mask = pd.Series(True, index=df.index)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        mask &= df["Order Date"].between(start, end)
    if regions:
        mask &= df["Region"].isin(regions)
    if states:
        mask &= df["State"].isin(states)
    if segments:
        mask &= df["Segment"].isin(segments)
    if categories:
        mask &= df["Category"].isin(categories)
    if subcats:
        mask &= df["Sub-Category"].isin(subcats)
    if ship_modes:
        mask &= df["Ship Mode"].isin(ship_modes)

    return df[mask]
