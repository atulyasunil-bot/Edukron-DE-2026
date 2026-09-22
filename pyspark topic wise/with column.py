import os
import sys


os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F


spark = (
    SparkSession.builder
    .appName("Assignment03_WithColumn")
    .master("local[2]")
    .getOrCreate()
)

# Sample orders dataset
orders_data = [
    (101, "2026-01-10", 12500.0, 1500.0, 200.0),
    (102, "2026-02-15",   450.0,   50.0,  40.0),
    (103, "2026-03-01",  1800.0,  200.0, 100.0),
    (104, "2026-03-25",     0.0,    0.0,   0.0),
    (105, "2025-11-20", 15000.0, 3000.0, 350.0),
]
columns = ["order_id", "order_date", "total_amount", "discount_amount", "shipping_cost"]
orders = spark.createDataFrame(orders_data, columns)

# Convert order_date string to real Date type
orders = orders.withColumn("order_date", F.to_date("order_date"))

# Calculate order metrics and date features
orders_enriched = (
    orders
    # Calculate net amount after discount
    .withColumn("net_amount", F.round(F.col("total_amount") - F.col("discount_amount"), 2))
    
    # Calculate final invoice amount including shipping
    .withColumn("final_amount", F.round(F.col("net_amount") + F.col("shipping_cost"), 2))
    
    # Calculate discount percentage with zero-division safeguard
    .withColumn(
        "discount_percentage",
        F.round(
            F.when(F.col("total_amount") > 0, (F.col("discount_amount") / F.col("total_amount")) * 100)
            .otherwise(0.0),
            2
        )
    )
    
    # Extract calendar
    .withColumn("order_year", F.year("order_date"))
    .withColumn("order_month", F.month("order_date"))
    .withColumn("order_quarter", F.quarter("order_date"))
    .withColumn("order_week", F.weekofyear("order_date"))
    
    # high value orders
    .withColumn("is_high_value_order", F.col("total_amount") > 10000)
    
    # Categorize final bill
    .withColumn(
        "order_category",
        F.when(F.col("final_amount") < 500, "Low")
        .when(F.col("final_amount") <= 2000, "Medium")
        .otherwise("High")
    )
    
    # Calculate age of order in days from today
    .withColumn("order_age_days", F.datediff(F.current_date(), F.col("order_date")))
)

# Display final enriched dataset
orders_enriched.select(
    "order_id",
    "total_amount",
    "discount_amount",
    "net_amount",
    "shipping_cost",
    "final_amount",
    "discount_percentage",
    "order_year",
    "order_month",
    "order_quarter",
    "order_week",
    "is_high_value_order",
    "order_category",
    "order_age_days"
).show(truncate=False)

# Stop Spark session
spark.stop()