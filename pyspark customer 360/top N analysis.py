import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("Mixed07_TopNAnalysis")
    .master("local[2]")
    .getOrCreate()
)

OUT_DIR = "./output_topn_analysis"
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
    (101, 1, 15000.0, "Karnataka"),
    (102, 1,  8000.0, "Karnataka"),
    (103, 1, 22000.0, "Karnataka"),
    (104, 2,  5000.0, "Maharashtra"),
    (105, 2, 45000.0, "Maharashtra"),
    (106, 3,  3500.0, "Delhi"),
    (107, 3, 12000.0, "Delhi"),
    (108, 4, 90000.0, "Karnataka"),
    (109, 5, 25000.0, "Tamil Nadu"),
    (110, 5, 18000.0, "Tamil Nadu"),
]
orders = spark.createDataFrame(orders_data, ["order_id", "customer_id", "total_amount", "shipping_state"])

# Sample products dataset
products_data = [
    (501, "Ultra Laptop 15", "Electronics"),
    (502, "Wireless Mouse", "Electronics"),
    (503, "Mechanical Keyboard", "Electronics"),
    (504, "Ergonomic Chair", "Furniture"),
    (505, "Standing Desk", "Furniture"),
    (506, "Monitor Arm", "Furniture"),
]
products = spark.createDataFrame(products_data, ["product_id", "product_name", "category"])

# Sample order items dataset
order_items_data = [
    (101, 501, 15000.0),
    (102, 502,  8000.0),
    (103, 503, 22000.0),
    (104, 504,  5000.0),
    (105, 505, 45000.0),
    (106, 502,  3500.0),
    (107, 506, 12000.0),
    (108, 501, 90000.0),
    (109, 505, 25000.0),
    (110, 504, 18000.0),
]
order_items = spark.createDataFrame(order_items_data, ["order_id", "product_id", "item_amount"])

# Top customers ranked by total spending
customer_spend = (
    orders
    .groupBy("customer_id")
    .agg(F.round(F.sum("total_amount"), 2).alias("total_spending"))
)

top_customers = (
    customer_spend
    .join(customers, "customer_id")
    .orderBy(F.col("total_spending").desc())
    .select("customer_id", "first_name", "last_name", "total_spending")
)
top_customers.show(10, truncate=False)

# Top products within every category ranked by revenue
order_product = order_items.join(products, "product_id")
category_revenue = (
    order_product
    .groupBy("category", "product_id", "product_name")
    .agg(F.round(F.sum("item_amount"), 2).alias("revenue"))
)

top_products_per_category = (
    category_revenue
    .withColumn("rnk", F.rank().over(Window.partitionBy("category").orderBy(F.col("revenue").desc())))
    .filter(F.col("rnk") <= 5)
    .orderBy("category", "rnk")
)
top_products_per_category.show(truncate=False)

# Top states ranked by total order revenue
state_revenue = (
    orders
    .groupBy("shipping_state")
    .agg(F.round(F.sum("total_amount"), 2).alias("revenue"))
    .orderBy(F.col("revenue").desc())
)
state_revenue.show(3, truncate=False)

# Top orders for every customer
top_orders_per_customer = (
    orders
    .withColumn(
        "rnk",
        F.row_number().over(Window.partitionBy("customer_id").orderBy(F.col("total_amount").desc()))
    )
    .filter(F.col("rnk") <= 5)
    .orderBy("customer_id", "rnk")
    .select("customer_id", "order_id", "total_amount", "rnk")
)
top_orders_per_customer.show(truncate=False)

# Percentage contribution of each product to total category revenue
category_total = (
    category_revenue
    .groupBy("category")
    .agg(F.round(F.sum("revenue"), 2).alias("category_total_revenue"))
)

contribution = (
    category_revenue
    .join(category_total, "category")
    .withColumn(
        "pct_of_category_revenue",
        F.round((F.col("revenue") / F.col("category_total_revenue")) * 100, 2)
    )
    .orderBy("category", F.col("pct_of_category_revenue").desc())
)
contribution.show(truncate=False)

# Write category product performance to Parquet
contribution.write.mode("overwrite").partitionBy("category").parquet(f"{OUT_DIR}/product_category_contribution")

# Read Parquet file back to verify write
df_saved = spark.read.parquet(f"{OUT_DIR}/product_category_contribution")
df_saved.select("category", "product_name", "revenue", "pct_of_category_revenue").show(truncate=False)

spark.stop()