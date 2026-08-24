import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data, apply_common_filters
from utils.kpis import show_kpi_row, core_kpis, money

st.set_page_config(page_title="Superstore Sales Analytics Dashboard", layout="wide")

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
df_raw = load_data()

st.sidebar.title("📊 Superstore Dashboard")
PAGES = [
    "1. Executive Overview", "2. Sales Analysis", "3. Profit Analysis",
    "4. Regional Analysis", "5. State Analysis", "6. City Analysis",
    "7. Category Analysis", "8. Sub-Category Analysis", "9. Product Analysis",
    "10. Customer Analysis", "11. Segment Analysis", "12. Order Analysis",
    "13. Shipping Analysis", "14. Discount Analysis", "15. Loss Analysis",
    "16. Time Series Analysis", "17. Growth Analysis", "18. Sales vs Profit",
    "19. Top & Bottom Performers", "20. Data Explorer",
]
page = st.sidebar.radio("Navigate", PAGES)

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")
df = apply_common_filters(df_raw, st.sidebar)

if df.empty:
    st.warning("No data matches the selected filters. Adjust filters in the sidebar.")
    st.stop()

st.title("Superstore Sales Analytics Dashboard")
st.caption(page)

# ---------------------------------------------------------------------------
# Helper chart functions
# ---------------------------------------------------------------------------
def bar(data, x, y, title, color=None, orientation="v", top_n=None, ascending=False):
    d = data.copy()
    if top_n:
        d = d.sort_values(y, ascending=ascending).head(top_n)
    fig = px.bar(d, x=x, y=y, color=color, title=title, orientation=orientation)
    st.plotly_chart(fig, use_container_width=True)


def line(data, x, y, title, color=None):
    fig = px.line(data.sort_values(x), x=x, y=y, color=color, title=title, markers=True)
    st.plotly_chart(fig, use_container_width=True)


def scatter(data, x, y, title, color=None, size=None):
    fig = px.scatter(data, x=x, y=y, color=color, size=size, title=title, opacity=0.6)
    st.plotly_chart(fig, use_container_width=True)


def group_sum(data, by, cols=("Sales", "Profit", "Quantity")):
    return data.groupby(by)[list(cols)].sum().reset_index()


# ---------------------------------------------------------------------------
# PAGE 1 - EXECUTIVE OVERVIEW
# ---------------------------------------------------------------------------
if page.startswith("1."):
    show_kpi_row(core_kpis(df))
    monthly = df.groupby("Order Month")[["Sales", "Profit"]].sum().reset_index()
    c1, c2 = st.columns(2)
    with c1:
        line(monthly, "Order Month", "Sales", "Monthly Sales Trend")
    with c2:
        bar(group_sum(df, "Region"), "Region", "Sales", "Sales by Region", color="Region")
    c3, c4 = st.columns(2)
    with c3:
        bar(group_sum(df, "Category"), "Category", "Sales", "Sales by Category", color="Category")
    with c4:
        bar(group_sum(df, "Category"), "Category", "Profit", "Profit by Category", color="Category")
    scatter(df, "Sales", "Profit", "Sales vs Profit (order line level)", color="Category")

    best_region = group_sum(df, "Region").sort_values("Sales", ascending=False).iloc[0]
    best_cat = group_sum(df, "Category").sort_values("Sales", ascending=False).iloc[0]
    best_month = monthly.sort_values("Sales", ascending=False).iloc[0]
    best_profit_month = monthly.sort_values("Profit", ascending=False).iloc[0]
    st.subheader("Highlights")
    st.markdown(f"""
- **Best Performing Region:** {best_region['Region']} ({money(best_region['Sales'])})
- **Best Performing Category:** {best_cat['Category']} ({money(best_cat['Sales'])})
- **Highest Sales Month:** {best_month['Order Month']} ({money(best_month['Sales'])})
- **Highest Profit Month:** {best_profit_month['Order Month']} ({money(best_profit_month['Profit'])})
""")

# ---------------------------------------------------------------------------
# PAGE 2 - SALES ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("2."):
    orders = df["Order ID"].nunique()
    kpis = {
        "Total Sales": money(df["Sales"].sum()),
        "Avg Sales/Order": money(df.groupby("Order ID")["Sales"].sum().mean()),
        "Max Order Sales": money(df.groupby("Order ID")["Sales"].sum().max()),
        "Min Order Sales": money(df.groupby("Order ID")["Sales"].sum().min()),
        "Number of Orders": f"{orders:,}",
    }
    show_kpi_row(kpis)
    c1, c2 = st.columns(2)
    with c1:
        line(df.groupby("Order Month")["Sales"].sum().reset_index(), "Order Month", "Sales", "Sales by Month")
    with c2:
        bar(df.groupby("Order Year")["Sales"].sum().reset_index(), "Order Year", "Sales", "Sales by Year")
    c3, c4 = st.columns(2)
    with c3:
        bar(df.groupby("Order Quarter")["Sales"].sum().reset_index(), "Order Quarter", "Sales", "Sales by Quarter")
    with c4:
        bar(group_sum(df, "Region"), "Region", "Sales", "Sales by Region", color="Region")
    st.plotly_chart(px.histogram(df, x="Sales", nbins=50, title="Sales Distribution"), use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE 3 - PROFIT ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("3."):
    loss = df.loc[df["Profit"] < 0, "Profit"].sum()
    kpis = {
        "Total Profit": money(df["Profit"].sum()),
        "Average Profit": money(df["Profit"].mean()),
        "Profit Margin %": f"{(df['Profit'].sum()/df['Sales'].sum()*100):.1f}%",
        "Maximum Profit": money(df["Profit"].max()),
        "Total Loss": money(loss),
    }
    show_kpi_row(kpis)
    c1, c2 = st.columns(2)
    with c1:
        line(df.groupby("Order Month")["Profit"].sum().reset_index(), "Order Month", "Profit", "Monthly Profit Trend")
    with c2:
        bar(group_sum(df, "Region"), "Region", "Profit", "Profit by Region", color="Region")
    c3, c4 = st.columns(2)
    with c3:
        bar(group_sum(df, "Category"), "Category", "Profit", "Profit by Category", color="Category")
    with c4:
        bar(group_sum(df, "Sub-Category"), "Sub-Category", "Profit", "Profit by Sub-Category", color="Sub-Category")
    st.plotly_chart(px.histogram(df, x="Profit", nbins=50, title="Profit Distribution"), use_container_width=True)
    scatter(df, "Sales", "Profit", "Sales vs Profit", color="Category")

    cat_profit = group_sum(df, "Category")
    reg_profit = group_sum(df, "Region")
    subcat_profit = group_sum(df, "Sub-Category")
    worst_prod = df.groupby("Product Name")["Profit"].sum().sort_values().index[0]
    st.subheader("Insights")
    st.markdown(f"""
- **Most Profitable Category:** {cat_profit.sort_values('Profit', ascending=False).iloc[0]['Category']}
- **Most Profitable Region:** {reg_profit.sort_values('Profit', ascending=False).iloc[0]['Region']}
- **Highest Loss Category:** {subcat_profit.sort_values('Profit').iloc[0]['Sub-Category']}
- **Highest Loss Product:** {worst_prod}
""")

# ---------------------------------------------------------------------------
# PAGE 4 - REGIONAL ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("4."):
    reg = df.groupby("Region").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"), Quantity=("Quantity", "sum"),
        Customers=("Customer ID", "nunique"),
    ).reset_index()
    reg["Margin %"] = (reg["Profit"] / reg["Sales"] * 100).round(1)
    reg["Avg Order Value"] = (reg["Sales"] / reg["Orders"]).round(2)
    show_kpi_row({
        "Regions": f"{reg.shape[0]}",
        "Total Regional Sales": money(reg['Sales'].sum()),
        "Total Regional Profit": money(reg['Profit'].sum()),
        "Total Orders": f"{reg['Orders'].sum():,}",
    })
    c1, c2 = st.columns(2)
    with c1:
        bar(reg, "Region", "Sales", "Sales by Region", color="Region")
    with c2:
        bar(reg, "Region", "Profit", "Profit by Region", color="Region")
    c3, c4 = st.columns(2)
    with c3:
        bar(reg, "Region", "Orders", "Orders by Region", color="Region")
    with c4:
        bar(reg, "Region", "Margin %", "Regional Profit Margin", color="Region")
    st.subheader("Comparison Table")
    st.dataframe(reg, use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE 5 - STATE ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("5."):
    state = df.groupby("State").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"), Orders=("Order ID", "nunique"),
        Customers=("Customer ID", "nunique"),
    ).reset_index()
    show_kpi_row({
        "Total States": f"{state.shape[0]}",
        "Best State (Sales)": state.sort_values('Sales', ascending=False).iloc[0]['State'],
        "Best State (Profit)": state.sort_values('Profit', ascending=False).iloc[0]['State'],
        "Worst State (Profit)": state.sort_values('Profit').iloc[0]['State'],
    })
    c1, c2 = st.columns(2)
    with c1:
        bar(state, "State", "Sales", "Top 10 States by Sales", top_n=10)
    with c2:
        bar(state, "State", "Profit", "Top 10 States by Profit", top_n=10)
    bar(state, "State", "Profit", "Bottom 10 States by Profit", top_n=10, ascending=True)
    st.subheader("State-wise Table")
    st.dataframe(state.sort_values("Sales", ascending=False), use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE 6 - CITY ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("6."):
    city = df.groupby("City").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
    show_kpi_row({
        "Number of Cities": f"{city.shape[0]}",
        "Top Sales City": city.sort_values('Sales', ascending=False).iloc[0]['City'],
        "Top Profit City": city.sort_values('Profit', ascending=False).iloc[0]['City'],
        "Lowest Profit City": city.sort_values('Profit').iloc[0]['City'],
    })
    c1, c2 = st.columns(2)
    with c1:
        bar(city, "City", "Sales", "Top 10 Cities by Sales", top_n=10)
    with c2:
        bar(city, "City", "Profit", "Top 10 Cities by Profit", top_n=10)
    bar(city, "City", "Profit", "Bottom 10 Cities by Profit", top_n=10, ascending=True)

# ---------------------------------------------------------------------------
# PAGE 7 - CATEGORY ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("7."):
    cat = df.groupby("Category").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"), Discount=("Discount", "mean"),
    ).reset_index()
    cat["Margin %"] = (cat["Profit"] / cat["Sales"] * 100).round(1)
    show_kpi_row({
        "Total Sales": money(cat['Sales'].sum()),
        "Total Profit": money(cat['Profit'].sum()),
        "Total Quantity": f"{cat['Quantity'].sum():,}",
        "Total Orders": f"{cat['Orders'].sum():,}",
    })
    c1, c2 = st.columns(2)
    with c1:
        bar(cat, "Category", "Sales", "Sales by Category", color="Category")
    with c2:
        bar(cat, "Category", "Profit", "Profit by Category", color="Category")
    c3, c4 = st.columns(2)
    with c3:
        bar(cat, "Category", "Quantity", "Quantity by Category", color="Category")
    with c4:
        bar(cat, "Category", "Discount", "Average Discount by Category", color="Category")
    scatter(df, "Sales", "Profit", "Sales vs Profit by Category", color="Category")

# ---------------------------------------------------------------------------
# PAGE 8 - SUB-CATEGORY ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("8."):
    sub = df.groupby("Sub-Category").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"),
        Discount=("Discount", "mean"),
    ).reset_index()
    sub["Margin %"] = (sub["Profit"] / sub["Sales"] * 100).round(1)
    c1, c2 = st.columns(2)
    with c1:
        bar(sub.sort_values("Sales", ascending=False), "Sub-Category", "Sales", "Sales by Sub-Category")
    with c2:
        bar(sub.sort_values("Profit", ascending=False), "Sub-Category", "Profit", "Profit by Sub-Category")
    c3, c4 = st.columns(2)
    with c3:
        bar(sub.sort_values("Quantity", ascending=False), "Sub-Category", "Quantity", "Quantity by Sub-Category")
    with c4:
        bar(sub.sort_values("Discount", ascending=False), "Sub-Category", "Discount", "Discount by Sub-Category")
    best = sub.sort_values("Profit", ascending=False).iloc[0]
    worst = sub.sort_values("Profit").iloc[0]
    top_sales = sub.sort_values("Sales", ascending=False).iloc[0]
    st.subheader("Highlights")
    st.markdown(f"""
- **Best Sub-Category (Profit):** {best['Sub-Category']}
- **Worst Sub-Category (Profit):** {worst['Sub-Category']}
- **Highest Sales Sub-Category:** {top_sales['Sub-Category']}
- **Highest Loss Sub-Category:** {worst['Sub-Category']}
""")
    st.dataframe(sub.sort_values("Sales", ascending=False), use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE 9 - PRODUCT ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("9."):
    prod = df.groupby(["Product Name", "Category", "Sub-Category"]).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"), Discount=("Discount", "mean"),
    ).reset_index()
    show_kpi_row({
        "Total Products": f"{prod.shape[0]:,}",
        "Highest Selling Product": prod.sort_values('Sales', ascending=False).iloc[0]['Product Name'][:30],
        "Most Profitable Product": prod.sort_values('Profit', ascending=False).iloc[0]['Product Name'][:30],
        "Most Loss-Making Product": prod.sort_values('Profit').iloc[0]['Product Name'][:30],
    })
    top_sales = prod.sort_values("Sales", ascending=False).head(10)
    top_profit = prod.sort_values("Profit", ascending=False).head(10)
    bottom_profit = prod.sort_values("Profit").head(10)
    bar(top_sales, "Product Name", "Sales", "Top 10 Products by Sales")
    bar(top_profit, "Product Name", "Profit", "Top 10 Products by Profit")
    bar(bottom_profit, "Product Name", "Profit", "Bottom 10 Products by Profit")
    st.subheader("Product Table")
    st.dataframe(prod.sort_values("Sales", ascending=False), use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE 10 - CUSTOMER ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("10."):
    cust = df.groupby("Customer Name").agg(
        Orders=("Order ID", "nunique"), Sales=("Sales", "sum"),
        Profit=("Profit", "sum"), Quantity=("Quantity", "sum"),
    ).reset_index()
    show_kpi_row({
        "Total Customers": f"{cust.shape[0]:,}",
        "Avg Sales/Customer": money(cust['Sales'].mean()),
        "Avg Profit/Customer": money(cust['Profit'].mean()),
        "Top Customer": cust.sort_values('Sales', ascending=False).iloc[0]['Customer Name'],
    })
    bar(cust.sort_values("Sales", ascending=False).head(10), "Customer Name", "Sales", "Top 10 Customers by Sales")
    bar(cust.sort_values("Profit", ascending=False).head(10), "Customer Name", "Profit", "Top 10 Customers by Profit")
    st.plotly_chart(px.histogram(cust, x="Sales", nbins=40, title="Customer Sales Distribution"), use_container_width=True)
    st.plotly_chart(px.histogram(cust, x="Profit", nbins=40, title="Customer Profit Distribution"), use_container_width=True)
    st.dataframe(cust.sort_values("Sales", ascending=False), use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE 11 - SEGMENT ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("11."):
    seg = df.groupby("Segment").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"), Customers=("Customer ID", "nunique"),
        Discount=("Discount", "mean"),
    ).reset_index()
    seg["Margin %"] = (seg["Profit"] / seg["Sales"] * 100).round(1)
    show_kpi_row({
        "Segments": f"{seg.shape[0]}",
        "Total Sales": money(seg['Sales'].sum()),
        "Total Profit": money(seg['Profit'].sum()),
        "Total Customers": f"{seg['Customers'].sum():,}",
    })
    c1, c2 = st.columns(2)
    with c1:
        bar(seg, "Segment", "Sales", "Sales by Segment", color="Segment")
    with c2:
        bar(seg, "Segment", "Profit", "Profit by Segment", color="Segment")
    c3, c4 = st.columns(2)
    with c3:
        bar(seg, "Segment", "Margin %", "Profit Margin by Segment", color="Segment")
    with c4:
        bar(seg, "Segment", "Discount", "Discount by Segment", color="Segment")

# ---------------------------------------------------------------------------
# PAGE 12 - ORDER ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("12."):
    orders = df.groupby("Order ID").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"),
        Date=("Order Date", "min"), Customer=("Customer Name", "first"),
    ).reset_index()
    show_kpi_row({
        "Total Orders": f"{orders.shape[0]:,}",
        "Avg Order Value": money(orders['Sales'].mean()),
        "Avg Qty/Order": f"{orders['Quantity'].mean():.1f}",
        "Avg Profit/Order": money(orders['Profit'].mean()),
    })
    line(df.groupby("Order Month")["Order ID"].nunique().reset_index(name="Orders"), "Order Month", "Orders", "Orders by Month")
    c1, c2 = st.columns(2)
    with c1:
        bar(df.groupby("Region")["Order ID"].nunique().reset_index(name="Orders"), "Region", "Orders", "Orders by Region")
    with c2:
        bar(df.groupby("Category")["Order ID"].nunique().reset_index(name="Orders"), "Category", "Orders", "Orders by Category")
    st.plotly_chart(px.histogram(orders, x="Sales", nbins=50, title="Order Value Distribution"), use_container_width=True)
    st.subheader("Order Table")
    st.dataframe(orders.sort_values("Date", ascending=False), use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE 13 - SHIPPING ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("13."):
    ship = df.groupby("Ship Mode").agg(
        Shipments=("Order ID", "nunique"), Sales=("Sales", "sum"),
        Profit=("Profit", "sum"), AvgDays=("Shipping Days", "mean"),
    ).reset_index()
    show_kpi_row({
        "Total Shipments": f"{df['Order ID'].nunique():,}",
        "Most Used Mode": ship.sort_values('Shipments', ascending=False).iloc[0]['Ship Mode'],
        "Avg Shipping Days": f"{df['Shipping Days'].mean():.1f}",
        "Fastest Mode": ship.sort_values('AvgDays').iloc[0]['Ship Mode'],
    })
    c1, c2 = st.columns(2)
    with c1:
        bar(ship, "Ship Mode", "Shipments", "Orders by Ship Mode", color="Ship Mode")
    with c2:
        bar(ship, "Ship Mode", "Sales", "Sales by Ship Mode", color="Ship Mode")
    c3, c4 = st.columns(2)
    with c3:
        bar(ship, "Ship Mode", "Profit", "Profit by Ship Mode", color="Ship Mode")
    with c4:
        bar(ship, "Ship Mode", "AvgDays", "Average Delivery Days by Ship Mode", color="Ship Mode")
    st.plotly_chart(px.pie(ship, names="Ship Mode", values="Shipments", title="Shipping Mode Distribution"), use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE 14 - DISCOUNT ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("14."):
    show_kpi_row({
        "Average Discount": f"{df['Discount'].mean()*100:.1f}%",
        "Maximum Discount": f"{df['Discount'].max()*100:.0f}%",
        "Sales (Discounted)": money(df.loc[df['Discount'] > 0, 'Sales'].sum()),
        "Profit (Discounted)": money(df.loc[df['Discount'] > 0, 'Profit'].sum()),
    })
    scatter(df, "Discount", "Sales", "Discount vs Sales")
    scatter(df, "Discount", "Profit", "Discount vs Profit")
    c1, c2 = st.columns(2)
    with c1:
        bar(df.groupby("Category")["Discount"].mean().reset_index(), "Category", "Discount", "Average Discount by Category")
    with c2:
        bar(df.groupby("Sub-Category")["Discount"].mean().reset_index(), "Sub-Category", "Discount", "Average Discount by Sub-Category")
    st.plotly_chart(px.histogram(df, x="Discount", nbins=20, title="Discount Distribution"), use_container_width=True)

    bins = [-0.01, 0, 0.10, 0.20, 0.30, 0.50, 1.01]
    labels = ["0%", "1-10%", "11-20%", "21-30%", "31-50%", "Above 50%"]
    df_disc = df.copy()
    df_disc["Discount Range"] = pd.cut(df_disc["Discount"], bins=bins, labels=labels)
    range_profit = df_disc.groupby("Discount Range", observed=True)["Profit"].sum().reset_index()
    bar(range_profit, "Discount Range", "Profit", "Profit by Discount Range")

# ---------------------------------------------------------------------------
# PAGE 15 - LOSS ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("15."):
    loss_df = df[df["Profit"] < 0]
    show_kpi_row({
        "Total Loss": money(loss_df['Profit'].sum()),
        "Loss Orders": f"{loss_df['Order ID'].nunique():,}",
        "Loss-Making Products": f"{loss_df['Product Name'].nunique():,}",
        "Loss-Making Customers": f"{loss_df['Customer Name'].nunique():,}",
    })
    c1, c2 = st.columns(2)
    with c1:
        bar(loss_df.groupby("Category")["Profit"].sum().reset_index(), "Category", "Profit", "Loss by Category")
    with c2:
        bar(loss_df.groupby("Sub-Category")["Profit"].sum().reset_index(), "Sub-Category", "Profit", "Loss by Sub-Category")
    c3, c4 = st.columns(2)
    with c3:
        bar(loss_df.groupby("Region")["Profit"].sum().reset_index(), "Region", "Profit", "Loss by Region")
    with c4:
        bar(loss_df.groupby("State")["Profit"].sum().reset_index(), "State", "Profit", "Loss by State", top_n=10, ascending=True)
    bar(loss_df.groupby("Product Name")["Profit"].sum().reset_index(), "Product Name", "Profit", "Top 10 Loss-Making Products", top_n=10, ascending=True)
    bar(loss_df.groupby("Customer Name")["Profit"].sum().reset_index(), "Customer Name", "Profit", "Top 10 Loss-Making Customers", top_n=10, ascending=True)
    st.subheader("Loss Records")
    st.dataframe(loss_df, use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE 16 - TIME SERIES ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("16."):
    view = st.selectbox("Time View", ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"], index=2)
    freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M", "Quarterly": "Q", "Yearly": "Y"}
    ts = df.set_index("Order Date").resample(freq_map[view]).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"), Quantity=("Quantity", "sum"),
    ).reset_index()

    monthly = df.groupby("Order Month")["Sales"].sum().sort_index()
    cur_month_sales = monthly.iloc[-1] if len(monthly) else 0
    prev_month_sales = monthly.iloc[-2] if len(monthly) > 1 else 0
    mom = ((cur_month_sales - prev_month_sales) / prev_month_sales * 100) if prev_month_sales else 0
    yearly = df.groupby("Order Year")["Sales"].sum().sort_index()
    cur_year_sales = yearly.iloc[-1] if len(yearly) else 0
    prev_year_sales = yearly.iloc[-2] if len(yearly) > 1 else 0
    yoy = ((cur_year_sales - prev_year_sales) / prev_year_sales * 100) if prev_year_sales else 0

    show_kpi_row({
        "Current Month Sales": money(cur_month_sales),
        "Previous Month Sales": money(prev_month_sales),
        "MoM Growth": f"{mom:.1f}%",
        "Current Year Sales": money(cur_year_sales),
        "YoY Growth": f"{yoy:.1f}%",
    })
    line(ts, "Order Date", "Sales", f"{view} Sales Trend")
    line(ts, "Order Date", "Profit", f"{view} Profit Trend")
    line(ts, "Order Date", "Orders", f"{view} Order Trend")
    line(ts, "Order Date", "Quantity", f"{view} Quantity Trend")

# ---------------------------------------------------------------------------
# PAGE 17 - GROWTH ANALYSIS
# ---------------------------------------------------------------------------
elif page.startswith("17."):
    monthly = df.groupby("Order Month").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
    monthly["Sales Growth %"] = monthly["Sales"].pct_change() * 100
    monthly["Profit Growth %"] = monthly["Profit"].pct_change() * 100

    quarterly = df.groupby("Order Quarter")["Sales"].sum().reset_index()
    quarterly["QoQ Growth %"] = quarterly["Sales"].pct_change() * 100

    yearly = df.groupby("Order Year")["Sales"].sum().reset_index()
    yearly["YoY Growth %"] = yearly["Sales"].pct_change() * 100

    show_kpi_row({
        "Latest MoM Growth": f"{monthly['Sales Growth %'].iloc[-1]:.1f}%" if len(monthly) > 1 else "N/A",
        "Latest QoQ Growth": f"{quarterly['QoQ Growth %'].iloc[-1]:.1f}%" if len(quarterly) > 1 else "N/A",
        "Latest YoY Growth": f"{yearly['YoY Growth %'].iloc[-1]:.1f}%" if len(yearly) > 1 else "N/A",
        "Latest Profit Growth": f"{monthly['Profit Growth %'].iloc[-1]:.1f}%" if len(monthly) > 1 else "N/A",
    })
    line(monthly, "Order Month", "Sales Growth %", "Monthly Growth %")
    line(quarterly, "Order Quarter", "QoQ Growth %", "Quarterly Growth %")
    line(yearly, "Order Year", "YoY Growth %", "Yearly Growth %")
    fig = px.line(monthly, x="Order Month", y=["Sales Growth %", "Profit Growth %"], title="Sales Growth vs Profit Growth", markers=True)
    st.plotly_chart(fig, use_container_width=True)
    st.info("Formula: Sales Growth % = (Current Sales − Previous Sales) / Previous Sales × 100")

# ---------------------------------------------------------------------------
# PAGE 18 - SALES VS PROFIT
# ---------------------------------------------------------------------------
elif page.startswith("18."):
    group_by = st.selectbox("Group / Color by", ["Region", "Category", "Segment", "Sub-Category"])
    scatter(df, "Sales", "Profit", "Sales vs Profit", color=group_by)
    scatter(df, "Sales", "Discount", "Sales vs Discount", color=group_by)
    scatter(df, "Quantity", "Sales", "Quantity vs Sales", color=group_by)
    scatter(df, "Quantity", "Profit", "Quantity vs Profit", color=group_by)
    scatter(df, "Discount", "Profit", "Discount vs Profit", color=group_by)

    hi_sales = df["Sales"].median()
    hi_profit = df["Profit"].median()
    q1 = df[(df.Sales >= hi_sales) & (df.Profit >= hi_profit)].shape[0]
    q2 = df[(df.Sales >= hi_sales) & (df.Profit < hi_profit)].shape[0]
    q3 = df[(df.Sales < hi_sales) & (df.Profit >= hi_profit)].shape[0]
    q4 = df[(df.Sales >= hi_sales) & (df.Profit < 0)].shape[0]
    st.subheader("Quadrant Insights (relative to median)")
    st.markdown(f"""
- **High Sales + High Profit:** {q1:,} line items
- **High Sales + Low Profit:** {q2:,} line items
- **Low Sales + High Profit:** {q3:,} line items
- **High Sales + Negative Profit:** {q4:,} line items
""")

# ---------------------------------------------------------------------------
# PAGE 19 - TOP & BOTTOM PERFORMERS
# ---------------------------------------------------------------------------
elif page.startswith("19."):
    n = st.select_slider("Show Top / Bottom N", options=[5, 10, 20], value=10)
    tabs = st.tabs(["Products", "Customers", "States", "Cities", "Sub-Categories"])

    with tabs[0]:
        prod = df.groupby("Product Name").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        bar(prod.sort_values("Sales", ascending=False).head(n), "Product Name", "Sales", f"Top {n} Products by Sales")
        bar(prod.sort_values("Profit", ascending=False).head(n), "Product Name", "Profit", f"Top {n} Products by Profit")
        bar(prod.sort_values("Profit").head(n), "Product Name", "Profit", f"Bottom {n} Products by Profit")
    with tabs[1]:
        cust = df.groupby("Customer Name").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        bar(cust.sort_values("Sales", ascending=False).head(n), "Customer Name", "Sales", f"Top {n} Customers by Sales")
        bar(cust.sort_values("Profit", ascending=False).head(n), "Customer Name", "Profit", f"Top {n} Customers by Profit")
        bar(cust.sort_values("Profit").head(n), "Customer Name", "Profit", f"Bottom {n} Customers by Profit")
    with tabs[2]:
        state = df.groupby("State").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        bar(state.sort_values("Sales", ascending=False).head(n), "State", "Sales", f"Top {n} States by Sales")
        bar(state.sort_values("Profit").head(n), "State", "Profit", f"Bottom {n} States by Profit")
    with tabs[3]:
        city = df.groupby("City").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        bar(city.sort_values("Sales", ascending=False).head(n), "City", "Sales", f"Top {n} Cities by Sales")
        bar(city.sort_values("Profit").head(n), "City", "Profit", f"Bottom {n} Cities by Profit")
    with tabs[4]:
        sub = df.groupby("Sub-Category").agg(Profit=("Profit", "sum")).reset_index()
        bar(sub.sort_values("Profit").head(n), "Sub-Category", "Profit", f"Bottom {n} Sub-Categories by Profit")

# ---------------------------------------------------------------------------
# PAGE 20 - DATA EXPLORER
# ---------------------------------------------------------------------------
elif page.startswith("20."):
    search = st.text_input("Search by Order ID, Customer Name, or Product Name")
    d = df.copy()
    if search:
        s = search.lower()
        d = d[
            d["Order ID"].str.lower().str.contains(s, na=False)
            | d["Customer Name"].str.lower().str.contains(s, na=False)
            | d["Product Name"].str.lower().str.contains(s, na=False)
        ]
    show_kpi_row({
        "Records": f"{d.shape[0]:,}",
        "Total Sales": money(d['Sales'].sum()),
        "Total Profit": money(d['Profit'].sum()),
        "Total Quantity": f"{d['Quantity'].sum():,}",
        "Avg Discount": f"{d['Discount'].mean()*100:.1f}%" if len(d) else "0%",
    })
    st.dataframe(d, use_container_width=True, height=500)

    summary = pd.DataFrame({
        "Metric": ["Records", "Total Sales", "Total Profit", "Total Quantity", "Avg Discount"],
        "Value": [d.shape[0], d["Sales"].sum(), d["Profit"].sum(), d["Quantity"].sum(),
                  d["Discount"].mean() if len(d) else 0],
    })
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇️ Download Filtered CSV", d.to_csv(index=False).encode("utf-8"),
                            "filtered_superstore.csv", "text/csv")
    with c2:
        st.download_button("⬇️ Download Summary CSV", summary.to_csv(index=False).encode("utf-8"),
                            "summary.csv", "text/csv")

st.markdown("---")
st.caption("Superstore Sales Analytics Dashboard · Built with Streamlit & Plotly")
