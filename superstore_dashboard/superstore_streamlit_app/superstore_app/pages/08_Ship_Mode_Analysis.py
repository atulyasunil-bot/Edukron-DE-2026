import streamlit as st
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="Ship Mode Analysis", layout="wide")
orders, people, returns = load_data()

st.title("Page 9 — Ship Mode Analysis")

ship = orders.groupby("Ship Mode")[["Sales", "Profit"]].sum()
st.dataframe(ship, use_container_width=True)

fig, ax = plt.subplots()
orders.groupby("Ship Mode")["Ship Days"].mean().sort_values().plot(kind="bar", ax=ax)
ax.set_ylabel("Avg Ship Days")
plt.xticks(rotation=0)
st.pyplot(fig)
