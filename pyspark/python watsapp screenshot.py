import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = SparkSession.builder \
    .appName("UsersReport") \
    .master("local[2]") \
    .getOrCreate()

print("=" * 60)
print("Q3: Users Report (Clean & Beginner Friendly)")
print("=" * 60)

users_data = [
    (1, "alice", "active",   "2026-03-28"),
    (2, "bob",   "active",   "2025-11-15"),
    (3, "carol", "inactive", "2026-01-05"),
    (4, "dave",  "pending",  "2026-03-30"),
]
columns = ["user_id", "user_name", "status", "registration_date"]
df = spark.createDataFrame(users_data, columns)

df = df.withColumn("registration_date", F.to_date("registration_date"))

today = F.lit("2026-04-01").cast("date")

# Adding column one by one

report = (
    df
    # 1. Capital letter
    .withColumn("user_name_upper", F.upper(F.col("user_name")))

    # 2. Extract numeric month
    .withColumn("registration_month", F.month(F.col("registration_date")))

    # 3. Calculate age of account
    .withColumn("days_since_registration", F.datediff(today, F.col("registration_date")))

    # 4.Using simple IF/ELSE IF/ELSE logic:
    .withColumn(
        "user_category",
        F.when((F.col("status") == "active") & (F.col("days_since_registration") <= 10), "Recently Active")
         .when(F.col("status") == "active", "Active User")
         .when(F.col("status") == "inactive", "Inactive User")
         .otherwise("Pending User")
    )
)

report.show(truncate=False)