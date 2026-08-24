import streamlit as st
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="Segment Analysis", layout="wide")
orders, people, returns = load_data()

st.title("Page 6 — Segment Analysis")

seg = orders.groupby("Segment")[["Sales", "Profit"]].sum()
seg["Margin %"] = (seg["Profit"] / seg["Sales"] * 100).round(1)
st.dataframe(seg, use_container_width=True)

fig, ax = plt.subplots()
seg["Sales"].plot(kind="pie", autopct="%1.0f%%", ylabel="", ax=ax)
st.pyplot(fig)
