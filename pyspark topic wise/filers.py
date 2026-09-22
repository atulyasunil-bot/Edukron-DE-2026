import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder
    .appName("Assignment05_Filters")
    .master("local[2]")
    .getOrCreate()
)

# Sample orders dataset
orders_data = [
    (101, 7500.0, 1600.0, "Completed", "UPI", "Karnataka", "Bengaluru", "2025-04-12"),
    (102, 1200.0,  100.0, "Cancelled", "Card", "Maharashtra", "Mumbai", "2025-06-18"),
    (103, 9500.0,  800.0, "Completed", "UPI", "Maharashtra", "Pune", "2026-01-10"),
    (104,  450.0,    0.0, "Pending", "UPI", "Delhi", None, "2025-08-22"),
    (105, 6000.0, 1500.0, "Completed", "UPI", "Karnataka", "Mysuru", "2025-11-05"),
    (106, 3200.0,  200.0, "Completed", "NetBanking", "Tamil Nadu", "Chennai", "2024-12-01"),
    (107, None,      0.0, "Cancelled", "Card", "Karnataka", None, "2025-02-14"),
]

columns = [
    "order_id", "total_amount", "discount_amount", "order_status",
    "payment_method", "shipping_state", "shipping_city", "order_date"
]

orders = spark.createDataFrame(orders_data, columns)
orders = orders.withColumn("order_date", F.to_date("order_date"))
orders.cache()

# Orders greater than 5000
q1 = orders.filter(F.col("total_amount") > 5000)

# Completed orders
q2 = orders.filter(F.col("order_status") == "Completed")

# Cancelled orders
q3 = orders.filter(F.col("order_status") == "Cancelled")

# Orders from Karnataka
q4 = orders.filter(F.col("shipping_state") == "Karnataka")

# Orders from Karnataka or Maharashtra
q5 = orders.filter(F.col("shipping_state").isin("Karnataka", "Maharashtra"))

# Orders between 1000 and 10000
q6 = orders.filter(F.col("total_amount").between(1000, 10000))

# Orders placed during 2025
q7 = orders.filter(F.year(F.col("order_date")) == 2025)

# Discount greater than 20% of total amount
q8 = orders.filter(F.col("discount_amount") > (0.20 * F.col("total_amount")))

# Payment method is UPI
q9 = orders.filter(F.col("payment_method") == "UPI")

# Status is not Cancelled
q10 = orders.filter(F.col("order_status") != "Cancelled")

# Shipping city is NULL
q11 = orders.filter(F.col("shipping_city").isNull())

# Total amount is NOT NULL
q12 = orders.filter(F.col("total_amount").isNotNull())

# Multiple conditions: Completed, UPI, and total amount > 1000
q13 = orders.filter(
    (F.col("order_status") == "Completed") &
    (F.col("payment_method") == "UPI") &
    (F.col("total_amount") > 1000)
)

# Top value completed orders matching specific criteria
q14 = orders.filter(
    (F.col("order_status") == "Completed") &
    (F.col("total_amount") > 5000) &
    (F.col("discount_amount") > 500) &
    (F.col("payment_method") == "UPI")
)

# Display counts for each filtered view
queries = [
    ("Total amount > 5000", q1),
    ("Completed orders", q2),
    ("Cancelled orders", q3),
    ("Karnataka orders", q4),
    ("Karnataka or Maharashtra", q5),
    ("Between 1000 and 10000", q6),
    ("Year 2025", q7),
    ("Discount > 20%", q8),
    ("UPI payment", q9),
    ("Status not Cancelled", q10),
    ("Shipping city is NULL", q11),
    ("Total amount NOT NULL", q12),
    ("Completed + UPI + amount > 1000", q13),
    ("Top value completed combo", q14),
]

for label, df in queries:
    print(f"{label:<35} -> {df.count()} rows")

spark.stop()