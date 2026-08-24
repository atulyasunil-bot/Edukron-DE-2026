import streamlit as st
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="Time Trend Analysis", layout="wide")
orders, people, returns = load_data()

st.title("Page 8 — Time Trend Analysis")

monthly = orders.set_index("Order Date").resample("ME")[["Sales", "Profit"]].sum()
fig, ax = plt.subplots()
monthly["Sales"].plot(ax=ax)
ax.set_ylabel("Sales ($)")
st.pyplot(fig)

st.subheader("Yearly Totals")
yearly = orders.groupby(orders["Order Date"].dt.year)[["Sales", "Profit"]].sum()
st.dataframe(yearly, use_container_width=True)
