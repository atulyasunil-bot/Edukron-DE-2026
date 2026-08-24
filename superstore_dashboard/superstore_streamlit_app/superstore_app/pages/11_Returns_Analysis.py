import streamlit as st
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="Returns Analysis", layout="wide")
orders, people, returns = load_data()

st.title("Page 12 — Returns Analysis")

returned_orders = orders.merge(returns, on="Order ID", how="inner")

c1, c2, c3 = st.columns(3)
c1.metric("Returned Orders", f"{returned_orders['Order ID'].nunique():,}")
c2.metric("Sales Tied to Returns", f"${returned_orders['Sales'].sum():,.0f}")
c3.metric("Profit Tied to Returns", f"${returned_orders['Profit'].sum():,.0f}")

fig, ax = plt.subplots()
returned_orders.groupby("Category")["Order ID"].nunique().plot(kind="bar", ax=ax)
ax.set_ylabel("Returned Orders")
plt.xticks(rotation=0)
st.pyplot(fig)
