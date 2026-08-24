import streamlit as st
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="State & City Analysis", layout="wide")
orders, people, returns = load_data()

st.title("Page 5 — State & City Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 States by Sales")
    state = orders.groupby("State/Province")["Sales"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    state.plot(kind="barh", ax=ax)
    ax.invert_yaxis()
    ax.set_xlabel("Sales ($)")
    st.pyplot(fig)

with col2:
    st.subheader("10 Cities With Biggest Losses")
    city_loss = orders.groupby("City")["Profit"].sum().sort_values().head(10)
    st.dataframe(city_loss, use_container_width=True)
