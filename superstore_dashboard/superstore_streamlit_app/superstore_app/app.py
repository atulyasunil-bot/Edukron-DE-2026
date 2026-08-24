import streamlit as st
import matplotlib.pyplot as plt
from data_loader import load_data

st.set_page_config(page_title="Superstore Dashboard", layout="wide")

orders, people, returns = load_data()

st.title("Superstore Sales & Profit Dashboard")
st.caption("Page 1 — Executive Overview")

total_sales = orders["Sales"].sum()
total_profit = orders["Profit"].sum()
total_orders = orders["Order ID"].nunique()
total_customers = orders["Customer ID"].nunique()
avg_discount = orders["Discount"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Sales", f"${total_sales:,.0f}")
c2.metric("Total Profit", f"${total_profit:,.0f}")
c3.metric("Profit Margin", f"{total_profit/total_sales*100:.1f}%")
c4.metric("Total Orders", f"{total_orders:,}")
c5.metric("Avg Discount", f"{avg_discount*100:.1f}%")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales by Category")
    cat_sales = orders.groupby("Category")["Sales"].sum()
    fig, ax = plt.subplots()
    cat_sales.plot(kind="bar", ax=ax)
    ax.set_ylabel("Sales ($)")
    plt.xticks(rotation=0)
    st.pyplot(fig)

with col2:
    st.subheader("Sales by Region")
    reg_sales = orders.groupby("Region")["Sales"].sum()
    fig, ax = plt.subplots()
    reg_sales.plot(kind="bar", ax=ax, color="darkorange")
    ax.set_ylabel("Sales ($)")
    plt.xticks(rotation=0)
    st.pyplot(fig)

st.info("Use the sidebar to navigate to the other 13 pages.")
