import streamlit as st
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_data

st.set_page_config(page_title="Correlation Overview", layout="wide")
orders, people, returns = load_data()

st.title("Page 14 — Correlation Overview")

num_cols = ["Sales", "Quantity", "Discount", "Profit"]
corr = orders[num_cols].corr()
st.dataframe(corr.round(2), use_container_width=True)

fig, ax = plt.subplots()
im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
ax.set_xticks(range(len(num_cols)))
ax.set_xticklabels(num_cols, rotation=45)
ax.set_yticks(range(len(num_cols)))
ax.set_yticklabels(num_cols)
for i in range(len(num_cols)):
    for j in range(len(num_cols)):
        ax.text(j, i, f"{corr.iloc[i,j]:.2f}", ha="center", va="center")
plt.colorbar(im)
st.pyplot(fig)

st.divider()
st.subheader("Summary")
st.markdown("""
- Technology leads on sales; Furniture drags on margin.
- Tables and Bookcases are the biggest loss-making sub-categories.
- West and East regions are the strongest performers.
- Discounts above ~20% consistently push orders into a loss.
- Discount and Profit are negatively correlated — the clearest lever in the data.
""")
