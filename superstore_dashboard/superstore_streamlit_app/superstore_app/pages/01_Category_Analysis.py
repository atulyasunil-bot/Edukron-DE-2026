import streamlit as st
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="Category Analysis", layout="wide")
orders, people, returns = load_data()

st.title("Page 2 — Category Analysis")

cat = orders.groupby("Category")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False)
cat["Margin %"] = (cat["Profit"] / cat["Sales"] * 100).round(1)
st.dataframe(cat, use_container_width=True)

fig, ax = plt.subplots()
cat[["Sales", "Profit"]].plot(kind="bar", ax=ax)
plt.xticks(rotation=0)
st.pyplot(fig)
