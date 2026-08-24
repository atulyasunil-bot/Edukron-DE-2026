import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="Regional Managers", layout="wide")
orders, people, returns = load_data()

st.title("Page 13 — Regional Managers")

st.dataframe(people, use_container_width=True)

st.subheader("Sales by Manager")
mgr_sales = orders.merge(people, on="Region").groupby("Regional Manager")["Sales"].sum().sort_values(ascending=False)
st.dataframe(mgr_sales, use_container_width=True)
