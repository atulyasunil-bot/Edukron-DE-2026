import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "superstore.xls")
    orders = pd.read_excel(path, sheet_name="Orders")
    people = pd.read_excel(path, sheet_name="People")
    returns = pd.read_excel(path, sheet_name="Returns")

    orders["Order Date"] = pd.to_datetime(orders["Order Date"])
    orders["Ship Date"] = pd.to_datetime(orders["Ship Date"])
    orders["Ship Days"] = (orders["Ship Date"] - orders["Order Date"]).dt.days

    return orders, people, returns
