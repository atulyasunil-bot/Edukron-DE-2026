import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StringType
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("Mixed10_CompletePipeline")
    .master("local[2]")
    .getOrCreate()
)

OUT_DIR = "./output_capstone_pipeline"
os.makedirs(OUT_DIR, exist_ok=True)

# Sample customers dataset
customers_data = [
    (1, "  aarav ", "sharma", "aarav.s@gmail.com", "bengaluru", "karnataka"),
    (2, "MEERA", "patel  ", "meera.p@yahoo.com", "mumbai", "maharashtra"),
    (3, "rohan", "verma", "rohan.v@corp.in", "delhi", "delhi"),
    (4, "priya", "NAIR", "priya.n@outlook.com", "chennai", "tamil nadu"),
]
customers_cols = ["customer_id", "first_name", "last_name", "email", "city", "state"]
customers = spark.createDataFrame(customers_data, customers_cols)

# Sample orders dataset with intentional DQ issues
orders_data = [
    (101, 1, 15000.0, 1500.0, 200.0, "Completed", "bengaluru", "karnataka", "2025-01-15"),
    (102, 1, 25000.0, 2000.0, 300.0, "Completed", "bengaluru", "karnataka", "2025-02-18"),
    (103, 2,  8000.0,  500.0, 100.0, "Completed", "mumbai", "maharashtra", "2025-01-20"),
    (104, 2,  3000.0,  100.0,  50.0, "Cancelled", "mumbai", "maharashtra", "2025-02-10"),
    (105, 3,  5000.0,  200.0, 100.0, "Cancelled", "delhi", "delhi", "2025-03-01"),
    (106, 3,  4500.0,  150.0,  50.0, "Cancelled", "delhi", "delhi", "2025-03-15"),
    (107, 4, 60000.0, 5000.0, 500.0, "Completed", "chennai", "tamil nadu", "2025-03-22"),
    (108, None, 1200.0, 0.0, 50.0, "Completed", "mumbai", "maharashtra", "2025-02-15"),
    (109, 2, -500.0, 0.0, 0.0, "Completed", "mumbai", "maharashtra", "2025-02-18"),
    (110, 4, 2000.0, 100.0, 50.0, "Completed", "chennai", "tamil nadu", "2030-01-01"),
]
orders_cols = [
    "order_id", "customer_id", "total_amount", "discount_amount",
    "shipping_cost", "order_status", "shipping_city", "shipping_state", "order_date"
]
orders = spark.createDataFrame(orders_data, orders_cols)
orders = orders.withColumn("order_date", F.to_date("order_date"))

# Sample products dataset
products_data = [
    (501, "Ultra Laptop 15", "Electronics"),
    (502, "Wireless Mouse", "Electronics"),
    (503, "Ergonomic Chair", "Furniture"),
    (504, "Standing Desk", "Furniture"),
]
products = spark.createDataFrame(products_data, ["product_id", "product_name", "category"])

# Sample order items dataset
order_items_data = [
    (101, 501, 1, 13500.0),
    (102, 501, 1, 23000.0),
    (103, 502, 5,  7500.0),
    (104, 503, 1,  2900.0),
    (105, 502, 3,  4800.0),
    (106, 502, 3,  4350.0),
    (107, 501, 2, 27000.0),
    (107, 504, 1, 28000.0),
]
order_items = spark.createDataFrame(order_items_data, ["order_id", "product_id", "quantity", "item_amount"])

# Data quality auditing and segregation
dq_flagged = (
    orders
    .withColumn(
        "dq_issue_count",
        F.col("order_id").isNull().cast("int")
        + F.col("customer_id").isNull().cast("int")
        + (F.col("total_amount") < 0).cast("int")
        + (F.col("discount_amount") < 0).cast("int")
        + (F.col("shipping_cost") < 0).cast("int")
        + F.col("order_date").isNull().cast("int")
        + (F.col("order_date") > F.current_date()).cast("int")
    )
    .withColumn("data_quality_status", F.when(F.col("dq_issue_count") == 0, "Valid").otherwise("Invalid"))
)

clean_orders = dq_flagged.filter(F.col("data_quality_status") == "Valid").drop("dq_issue_count")
rejected_orders = dq_flagged.filter(F.col("data_quality_status") == "Invalid")

data_quality_report = dq_flagged.groupBy("data_quality_status").agg(F.count("*").alias("record_count"))
data_quality_report.show()

# Clean and standardize string attributes
customers_clean = (
    customers
    .withColumn("first_name", F.initcap(F.trim(F.col("first_name"))))
    .withColumn("last_name", F.initcap(F.trim(F.col("last_name"))))
    .withColumn("email", F.trim(F.col("email")))
    .withColumn("city", F.initcap(F.trim(F.col("city"))))
    .withColumn("state", F.initcap(F.trim(F.col("state"))))
)

clean_orders_derived = (
    clean_orders
    .withColumn("shipping_city", F.initcap(F.trim(F.col("shipping_city"))))
    .withColumn("shipping_state", F.initcap(F.trim(F.col("shipping_state"))))
    .withColumn("net_amount", F.round(F.col("total_amount") - F.col("discount_amount"), 2))
    .withColumn("year_month", F.date_format("order_date", "yyyy-MM"))
)

# Join valid orders with customers, items, and products
order_level = (
    clean_orders_derived
    .join(customers_clean, "customer_id")
    .join(order_items, "order_id")
    .join(products, "product_id")
)
order_level.cache()
order_level.count()

# Business aggregations
daily_sales = (
    order_level
    .groupBy("order_date")
    .agg(
        F.round(F.sum("item_amount"), 2).alias("daily_revenue"),
        F.count("*").alias("daily_line_items")
    )
)

monthly_sales = (
    order_level
    .groupBy("year_month")
    .agg(F.round(F.sum("item_amount"), 2).alias("monthly_revenue"))
)

customer_sales = (
    order_level
    .groupBy("customer_id", "first_name", "last_name")
    .agg(F.round(F.sum("item_amount"), 2).alias("customer_revenue"))
)

product_sales = (
    order_level
    .groupBy("product_id", "product_name")
    .agg(
        F.round(F.sum("item_amount"), 2).alias("product_revenue"),
        F.sum("quantity").alias("units_sold")
    )
)

category_sales = (
    order_level
    .groupBy("category")
    .agg(F.round(F.sum("item_amount"), 2).alias("category_revenue"))
)

# Window analytics
customer_rank = customer_sales.withColumn(
    "customer_rank",
    F.rank().over(Window.orderBy(F.col("customer_revenue").desc()))
)
customer_rank.show(truncate=False)

product_rank = product_sales.withColumn(
    "product_rank",
    F.rank().over(Window.orderBy(F.col("product_revenue").desc()))
)
product_rank.show(truncate=False)

w_month = Window.orderBy("year_month")
running_sales = (
    monthly_sales
    .withColumn("previous_month_sales", F.lag("monthly_revenue", 1).over(w_month))
    .withColumn(
        "running_sales",
        F.round(
            F.sum("monthly_revenue").over(
                w_month.rowsBetween(Window.unboundedPreceding, Window.currentRow)
            ),
            2
        )
    )
)
running_sales.show()


# Customer risk scoring UDF
def customer_risk(cancelled_ratio):
    if cancelled_ratio is None:
        return "Unknown"
    if cancelled_ratio >= 0.5:
        return "High Risk"
    elif cancelled_ratio >= 0.2:
        return "Medium Risk"
    return "Low Risk"


customer_risk_udf = F.udf(customer_risk, StringType())

customer_order_stats = (
    orders
    .groupBy("customer_id")
    .agg(
        F.count("*").alias("total_orders"),
        F.count(F.when(F.col("order_status") == "Cancelled", True)).alias("cancelled_orders")
    )
    .withColumn("cancelled_ratio", F.round(F.col("cancelled_orders") / F.col("total_orders"), 3))
    .withColumn("risk_category", customer_risk_udf(F.col("cancelled_ratio")))
)
customer_order_stats.show()

# Partition sizing optimization
daily_sales_out = daily_sales.withColumn("year_month", F.date_format("order_date", "yyyy-MM")).coalesce(2)
monthly_sales_out = monthly_sales.coalesce(1)
customer_sales_out = customer_sales.coalesce(2)

# Persist pipeline outputs to storage
daily_sales_out.write.mode("overwrite").partitionBy("year_month").parquet(f"{OUT_DIR}/pipeline_daily_sales")
monthly_sales_out.write.mode("overwrite").parquet(f"{OUT_DIR}/pipeline_monthly_sales")
customer_sales_out.write.mode("overwrite").parquet(f"{OUT_DIR}/pipeline_customer_sales")
product_sales.coalesce(2).write.mode("overwrite").parquet(f"{OUT_DIR}/pipeline_product_sales")
data_quality_report.write.mode("overwrite").option("header", "true").csv(f"{OUT_DIR}/pipeline_data_quality")
rejected_orders.write.mode("overwrite").parquet(f"{OUT_DIR}/pipeline_rejected_data")

# Read Parquet verification check
df_saved = spark.read.parquet(f"{OUT_DIR}/pipeline_monthly_sales")
df_saved.show()

order_level.unpersist()

spark.stop()
