import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="Discount vs Profit", layout="wide")
orders, people, returns = load_data()

st.title("Page 7 — Discount vs Profit")

orders["Discount Bucket"] = pd.cut(orders["Discount"], bins=[-0.01, 0, 0.2, 0.4, 1],
                                    labels=["0%", "1-20%", "21-40%", "40%+"])
disc = orders.groupby("Discount Bucket")[["Sales", "Profit"]].sum()
disc["Margin %"] = (disc["Profit"] / disc["Sales"] * 100).round(1)
st.dataframe(disc, use_container_width=True)

fig, ax = plt.subplots()
ax.scatter(orders["Discount"], orders["Profit"], alpha=0.3, s=10)
ax.axhline(0, color="red", linestyle="--")
ax.set_xlabel("Discount")
ax.set_ylabel("Profit ($)")
st.pyplot(fig)

st.caption("Profit turns negative once discount goes past roughly 20%.")
