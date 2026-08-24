import streamlit as st
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="Sub-Category Analysis", layout="wide")
orders, people, returns = load_data()

st.title("Page 3 — Sub-Category Analysis")
st.caption("Which specific sub-categories actually make money.")

sub = orders.groupby("Sub-Category")[["Sales", "Profit"]].sum().sort_values("Profit")
st.dataframe(sub, use_container_width=True)

colors = sub["Profit"].apply(lambda x: "crimson" if x < 0 else "steelblue")
fig, ax = plt.subplots(figsize=(8, 6))
sub["Profit"].plot(kind="barh", ax=ax, color=colors)
ax.set_xlabel("Profit ($)")
st.pyplot(fig)
