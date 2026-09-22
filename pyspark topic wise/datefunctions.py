import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder
    .appName("Assignment10_DateFunctions")
    .master("local[2]")
    .getOrCreate()
)

# Sample customers dataset
customers_data = [
    (1, "Aarav", "Sharma", "2024-01-15"),
    (2, "Meera", "Patel", "2025-06-20"),
    (3, "Rohan", "Verma", "2023-11-05"),
    (4, "Priya", "Nair", "2026-08-10"),
]
customers = spark.createDataFrame(customers_data, ["customer_id", "first_name", "last_name", "registration_date"])
customers = customers.withColumn("registration_date", F.to_date("registration_date"))

# Sample orders dataset
orders_data = [
    (101, 1, 1500.0, "2026-09-20"),
    (102, 2, 2500.0, "2026-09-21"),
    (103, 1,  800.0, "2026-08-31"),
    (104, 3,  450.0, "2026-01-15"),
    (105, 2, 3200.0, "2025-12-31"),
    (106, 4, 1200.0, "2026-09-15"),
]
orders = spark.createDataFrame(orders_data, ["order_id", "customer_id", "total_amount", "order_date"])
orders = orders.withColumn("order_date", F.to_date("order_date"))
orders.cache()

# Extract year from order date
orders.withColumn("order_year", F.year("order_date")).select("order_id", "order_date", "order_year").show()

# Extract month from order date
orders.withColumn("order_month", F.month("order_date")).select("order_id", "order_date", "order_month").show()

# Filter orders placed on weekends where Sunday is 1 and Saturday is 7
weekend_orders = orders.filter(F.dayofweek("order_date").isin(1, 7))
weekend_orders.show()

# Filter orders placed on Monday where day of week is 2
monday_orders = orders.filter(F.dayofweek("order_date") == 2)
monday_orders.show()

# Calculate order age in days from current date
orders_age = orders.withColumn("order_age_days", F.datediff(F.current_date(), "order_date"))
orders_age.select("order_id", "order_date", "order_age_days").show()

# Filter customers registered more than one year ago
old_customers = customers.filter(F.datediff(F.current_date(), "registration_date") > 365)
old_customers.show()

# Calculate elapsed months since customer registration
customers_months = customers.withColumn(
    "months_since_registration",
    F.round(F.months_between(F.current_date(), "registration_date"), 2)
)
customers_months.select("customer_id", "registration_date", "months_since_registration").show()

# Filter orders placed within the last 30 days
last_30_days = orders.filter(F.datediff(F.current_date(), "order_date") <= 30)
last_30_days.show()

# Filter orders placed on the last calendar day of the month
month_end_orders = orders.filter(F.col("order_date") == F.last_day("order_date"))
month_end_orders.show()

# Format order date to year and month string
orders.withColumn("year_month", F.date_format("order_date", "yyyy-MM")).select("order_id", "order_date", "year_month").show()

spark.stop()