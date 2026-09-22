import os
import shutil
import sys

# Environment and Hadoop paths
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["PATH"] = r"C:\hadoop\bin;" + os.environ["PATH"]

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

# Initialize Spark session
spark = (
    SparkSession.builder
    .appName("Assignment02_FileWrites")
    .master("local[2]")
    .getOrCreate()
)

OUT_DIR = "./output_orders"
os.makedirs(OUT_DIR, exist_ok=True)

# Sample orders data
orders_data = [
    (1001, 1, "Completed", 150.00, "2024-01-15"),
    (1002, 2, "Pending",    85.50, "2024-01-20"),
    (1003, 1, "Completed", 220.00, "2024-02-10"),
    (1004, 3, "Cancelled",  45.00, "2024-02-14"),
    (1005, 2, "Completed", 310.25, "2024-03-01"),
    (1006, 4, "Pending",   120.00, "2024-03-05"),
]
columns = ["order_id", "customer_id", "order_status", "amount", "order_date"]
orders = spark.createDataFrame(orders_data, columns)
orders = orders.withColumn("order_date", F.to_date("order_date"))

# Display base orders table
orders.show()

# Write as CSV
orders.write.mode("overwrite").option("header", "true").csv(f"{OUT_DIR}/orders_csv")

# Write as JSON
orders.write.mode("overwrite").json(f"{OUT_DIR}/orders_json")

# Write as Parquet
orders.write.mode("overwrite").parquet(f"{OUT_DIR}/orders_parquet")

# Write partitioned by order status
orders.write.mode("overwrite").partitionBy("order_status").parquet(f"{OUT_DIR}/orders_by_status")

# Demonstrate overwrite mode
demo_path = f"{OUT_DIR}/orders_mode_demo"
orders.limit(4).write.mode("overwrite").parquet(demo_path)

# Demonstrate append mode
orders.limit(2).write.mode("append").parquet(demo_path)

# Read partitioned data back
back = spark.read.parquet(f"{OUT_DIR}/orders_by_status")
back.show()

# Stop Spark session
spark.stop()