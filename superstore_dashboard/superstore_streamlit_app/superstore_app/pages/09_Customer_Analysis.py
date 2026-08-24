import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="Customer Analysis", layout="wide")
orders, people, returns = load_data()

st.title("Page 10 — Customer Analysis")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Top 10 Customers by Sales")
    top_customers = orders.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).head(10)
    st.dataframe(top_customers, use_container_width=True)

with col2:
    st.subheader("5 Least Profitable Customers")
    cust_profit = orders.groupby("Customer Name")["Profit"].sum().sort_values().head(5)
    st.dataframe(cust_profit, use_container_width=True)
