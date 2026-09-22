import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("Mixed01_SalesAnalysis")
    .master("local[2]")
    .getOrCreate()
)

OUT_DIR = "./output_sales_analysis"
os.makedirs(OUT_DIR, exist_ok=True)

# Sample customers dataset
customers_data = [
    (1, "Aarav", "Sharma"),
    (2, "Meera", "Patel"),
    (3, "Rohan", "Verma"),
    (4, "Priya", "Nair"),
    (5, "Ananya", "Iyer"),
]
customers = spark.createDataFrame(customers_data, ["customer_id", "first_name", "last_name"])

# Sample orders dataset
orders_data = [
    (101, 1, 15000.0, 1500.0, "Completed", "2025-01-15"),
    (102, 1, 60000.0, 5000.0, "Completed", "2025-02-18"),
    (103, 2,  8000.0,  500.0, "Completed", "2025-01-20"),
    (104, 2, 45000.0, 2000.0, "Completed", "2025-03-05"),
    (105, 3,  3500.0,  200.0, "Cancelled", "2025-02-10"),
    (106, 4, 120000.0, 10000.0, "Completed", "2025-03-22"),
]
orders_cols = ["order_id", "customer_id", "total_amount", "discount_amount", "order_status", "order_date"]
orders = spark.createDataFrame(orders_data, orders_cols)
orders = orders.withColumn("order_date", F.to_date("order_date"))

# Sample products dataset
products_data = [
    (501, "Laptop Pro", "Electronics"),
    (502, "Wireless Mouse", "Electronics"),
    (503, "Ergonomic Chair", "Furniture"),
    (504, "Standing Desk", "Furniture"),
    (505, "Coffee Maker", "Appliances"),
]
products = spark.createDataFrame(products_data, ["product_id", "product_name", "category"])

# Sample order items dataset
order_items_data = [
    (101, 501, 1, 13500.0),
    (102, 501, 3, 40500.0),
    (102, 503, 1, 14500.0),
    (103, 502, 5,  7500.0),
    (104, 504, 2, 43000.0),
    (106, 501, 5, 67500.0),
    (106, 504, 2, 42500.0),
]
order_items = spark.createDataFrame(order_items_data, ["order_id", "product_id", "quantity", "item_amount"])

# Filter completed orders and compute net order amount
completed_orders = (
    orders
    .filter(F.col("order_status") == "Completed")
    .withColumn("net_amount", F.round(F.col("total_amount") - F.col("discount_amount"), 2))
)

# Join completed orders with items and product metadata
order_product = (
    completed_orders.select("order_id", "customer_id")
    .join(order_items, "order_id")
    .join(products, "product_id")
)
order_product.cache()

# Total revenue by product category
revenue_by_category = (
    order_product
    .groupBy("category")
    .agg(F.round(F.sum("item_amount"), 2).alias("revenue"))
    .orderBy(F.col("revenue").desc())
)
revenue_by_category.show()

# Top products in every category ranked by revenue
product_revenue = (
    order_product
    .groupBy("category", "product_id", "product_name")
    .agg(F.round(F.sum("item_amount"), 2).alias("revenue"))
)
top_per_category = (
    product_revenue
    .withColumn("rnk", F.rank().over(Window.partitionBy("category").orderBy(F.col("revenue").desc())))
    .filter(F.col("rnk") <= 5)
    .orderBy("category", "rnk")
)
top_per_category.show(truncate=False)

# Customer lifetime spending and high-value customer ranking
customer_ltv = (
    completed_orders
    .groupBy("customer_id")
    .agg(F.round(F.sum("net_amount"), 2).alias("lifetime_spending"))
)
customer_ltv.orderBy(F.col("lifetime_spending").desc()).show()

# Customers who never placed an order
never_ordered = customers.join(orders, "customer_id", "left_anti")
never_ordered.show()

# Products that were never sold
sold_products = order_items.select("product_id").distinct()
never_sold = products.join(sold_products, "product_id", "left_anti")
never_sold.show()

# Monthly revenue and month-over-month percentage change
monthly_revenue = (
    completed_orders
    .withColumn("year_month", F.date_format("order_date", "yyyy-MM"))
    .groupBy("year_month")
    .agg(F.round(F.sum("net_amount"), 2).alias("revenue"))
    .orderBy("year_month")
)

mom = (
    monthly_revenue
    .withColumn("prev_month_revenue", F.lag("revenue", 1).over(Window.orderBy("year_month")))
    .withColumn("mom_change", F.round(F.col("revenue") - F.col("prev_month_revenue"), 2))
    .withColumn(
        "mom_change_pct",
        F.round(
            F.when(
                F.col("prev_month_revenue") > 0,
                ((F.col("revenue") - F.col("prev_month_revenue")) / F.col("prev_month_revenue")) * 100
            ).otherwise(0.0),
            2
        )
    )
)
mom.show()

# Earliest and latest order dates per customer
by_cust_date = Window.partitionBy("customer_id").orderBy("order_date")
by_cust_date_desc = Window.partitionBy("customer_id").orderBy(F.col("order_date").desc())

first_last_order = (
    orders
    .withColumn("first_order_date", F.first("order_date").over(by_cust_date))
    .withColumn("latest_order_date", F.first("order_date").over(by_cust_date_desc))
    .select("customer_id", "first_order_date", "latest_order_date")
    .distinct()
    .orderBy("customer_id")
)
first_last_order.show()

# Customer segments derived from lifetime spend
customer_segments = (
    customer_ltv
    .withColumn(
        "customer_segment",
        F.when(F.col("lifetime_spending") > 100000, "Platinum")
        .when(F.col("lifetime_spending") > 50000, "Gold")
        .when(F.col("lifetime_spending") > 10000, "Silver")
        .otherwise("Bronze")
    )
)
customer_segments.show()

# Write customer lifetime segmentation to Parquet
customer_segments.write.mode("overwrite").parquet(f"{OUT_DIR}/customer_segments")

# Read Parquet file back to verify write
df_saved = spark.read.parquet(f"{OUT_DIR}/customer_segments")
df_saved.show()

order_product.unpersist()

spark.stop()