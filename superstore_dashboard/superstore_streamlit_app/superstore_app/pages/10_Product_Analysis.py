import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="Product Analysis", layout="wide")
orders, people, returns = load_data()

st.title("Page 11 — Product Analysis")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Top 10 Loss-Making Products")
    top_losses = orders.groupby("Product Name")["Profit"].sum().sort_values().head(10)
    st.dataframe(top_losses, use_container_width=True)

with col2:
    st.subheader("Top 10 Sellers by Sales")
    top_sellers = orders.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(10)
    st.dataframe(top_sellers, use_container_width=True)
