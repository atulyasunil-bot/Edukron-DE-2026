import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("Mixed03_ProductPerformance")
    .master("local[2]")
    .getOrCreate()
)

OUT_DIR = "./output_product_performance"
os.makedirs(OUT_DIR, exist_ok=True)

# Sample products dataset
products_data = [
    (501, "Ultra Laptop 15", "Electronics", "Dell", 40000.0, 55000.0, "2025-01-10"),
    (502, "Wireless Mouse", "Electronics", "Logitech", 500.0, 1200.0, "2024-05-15"),
    (503, "Mechanical Keyboard", "Electronics", "Keychron", 3500.0, 6500.0, "2023-08-20"),
    (504, "Ergonomic Chair", "Furniture", "Featherlite", 7000.0, 12000.0, "2025-02-01"),
    (505, "Standing Desk", "Furniture", "Ikea", 15000.0, 22000.0, "2023-01-15"),
    (506, "Ceramic Mug", "Kitchen", "ClayCraft", 150.0, 400.0, "2026-03-01"),
]
products_cols = ["product_id", "product_name", "category", "brand", "unit_cost", "selling_price", "launch_date"]
products = spark.createDataFrame(products_data, products_cols)
products = products.withColumn("launch_date", F.to_date("launch_date"))

# Sample orders dataset
orders_data = [
    (101, 1, "2025-01-15"),
    (102, 2, "2025-01-20"),
    (103, 1, "2025-02-10"),
    (104, 3, "2025-02-25"),
    (105, 4, "2025-03-12"),
]
orders = spark.createDataFrame(orders_data, ["order_id", "customer_id", "order_date"])
orders = orders.withColumn("order_date", F.to_date("order_date"))

# Sample order items dataset
order_items_data = [
    (101, 501, 1, 55000.0, 55000.0),
    (101, 502, 2, 1200.0,  2400.0),
    (102, 504, 1, 12000.0, 12000.0),
    (103, 501, 2, 53000.0, 106000.0),
    (104, 502, 5, 1100.0,  5500.0),
    (105, 504, 2, 11500.0, 23000.0),
    (105, 505, 1, 22000.0, 22000.0),
]
order_items_cols = ["order_id", "product_id", "quantity", "unit_price", "item_amount"]
order_items = spark.createDataFrame(order_items_data, order_items_cols)

# Join order items with orders metadata
order_product = order_items.join(orders.select("order_id", "customer_id", "order_date"), "order_id")
order_product.cache()

# Compute overall product performance metrics
product_stats = (
    order_product
    .join(products, "product_id")
    .groupBy("product_id", "product_name", "category", "brand", "unit_cost", "selling_price", "launch_date")
    .agg(
        F.sum("quantity").alias("quantity_sold"),
        F.round(F.sum("item_amount"), 2).alias("revenue"),
        F.round(F.avg("unit_price"), 2).alias("average_selling_price"),
        F.countDistinct("customer_id").alias("unique_customers"),
    )
    .withColumn("profit", F.round(F.col("revenue") - (F.col("unit_cost") * F.col("quantity_sold")), 2))
)

# Top 3 products per category ranked by revenue
product_stats = product_stats.withColumn(
    "category_rank",
    F.rank().over(Window.partitionBy("category").orderBy(F.col("revenue").desc()))
)

(
    product_stats
    .filter(F.col("category_rank") <= 3)
    .orderBy("category", "category_rank")
    .select("category", "category_rank", "product_name", "revenue", "profit")
    .show(truncate=False)
)

# Identify products with zero sales using left anti join
zero_sales = products.join(order_items.select("product_id").distinct(), "product_id", "left_anti")
zero_sales.select("product_id", "product_name", "category").show(truncate=False)

# Filter products launched in the last 2 years (730 days)
recent_products = products.filter(F.datediff(F.current_date(), "launch_date") <= 730)
recent_products.select("product_id", "product_name", "launch_date").show(truncate=False)

# Products whose revenue is above their category average
category_avg = (
    product_stats
    .groupBy("category")
    .agg(F.round(F.avg("revenue"), 2).alias("category_avg_revenue"))
)

above_avg = (
    product_stats
    .join(category_avg, "category")
    .filter(F.col("revenue") > F.col("category_avg_revenue"))
    .select("product_name", "category", "revenue", "category_avg_revenue")
)
above_avg.show(truncate=False)

# Products with at least one month-over-month sales quantity increase
monthly_product_sales = (
    order_product
    .withColumn("year_month", F.date_format("order_date", "yyyy-MM"))
    .groupBy("product_id", "year_month")
    .agg(F.sum("quantity").alias("qty"))
)

mom = (
    monthly_product_sales
    .withColumn("prev_qty", F.lag("qty", 1).over(Window.partitionBy("product_id").orderBy("year_month")))
    .withColumn("increased", F.col("qty") > F.col("prev_qty"))
)

products_with_growth = mom.filter(F.col("increased")).select("product_id").distinct()
products_with_growth.show()

# Final output selection and partitioned Parquet write
final = product_stats.select(
    "product_id", "product_name", "category", "brand",
    "quantity_sold", "revenue", "profit", "unique_customers", "category_rank",
)

final.write.mode("overwrite").partitionBy("category").parquet(f"{OUT_DIR}/product_performance")

# Read Parquet back to verify write
df_saved = spark.read.parquet(f"{OUT_DIR}/product_performance")
df_saved.select("product_id", "product_name", "category", "revenue", "profit").show(truncate=False)

order_product.unpersist()

spark.stop()