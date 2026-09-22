import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StringType

spark = (
    SparkSession.builder
    .appName("Assignment13_UDF")
    .master("local[2]")
    .getOrCreate()
)

OUT_DIR = "./output_udf"
os.makedirs(OUT_DIR, exist_ok=True)

# Sample customers dataset
customers_data = [
    (1, "1998-05-14", "+91-9876543210"),
    (2, "1980-11-20", "+1-4155552671"),
    (3, "1965-02-28", "+44-2071838750"),
    (4, "2005-09-01", "+91-9123456780"),
    (5, None, None),
]
customers = spark.createDataFrame(customers_data, ["customer_id", "date_of_birth", "phone"])
customers = customers.withColumn("date_of_birth", F.to_date("date_of_birth"))

# Sample orders dataset
orders_data = [
    (101, 350.0),
    (102, 1200.0),
    (103, 5500.0),
    (104, None),
]
orders = spark.createDataFrame(orders_data, ["order_id", "total_amount"])

# Country mapping python function and UDF registration
COUNTRY_MAP = {
    "IN": "India",
    "US": "United States",
    "UK": "United Kingdom",
    "AU": "Australia",
    "SG": "Singapore"
}


def country_code_to_name(code):
    if code is None:
        return None
    return COUNTRY_MAP.get(code.upper(), "Unknown")


country_name_udf = F.udf(country_code_to_name, StringType())

# Apply country mapping UDF
demo_countries = spark.createDataFrame([("IN",), ("US",), ("UK",), ("AU",), ("SG",), ("ZZ",)], ["country_code"])
demo_countries.withColumn("country_name", country_name_udf(F.col("country_code"))).show()


# Customer age category python function and UDF registration
def age_category(dob_year):
    if dob_year is None:
        return None
    age = 2026 - dob_year
    if age < 25:
        return "Young Adult"
    elif age < 45:
        return "Adult"
    elif age < 60:
        return "Middle Aged"
    return "Senior"


age_category_udf = F.udf(age_category, StringType())

# Apply age category UDF
customers_with_age = (
    customers
    .withColumn("birth_year", F.year("date_of_birth"))
    .withColumn("age_category", age_category_udf(F.col("birth_year")))
)
customers_with_age.select("customer_id", "date_of_birth", "age_category").show()


# Order amount category python function and UDF registration
def order_amount_category(amount):
    if amount is None:
        return None
    if amount < 500:
        return "Low"
    elif amount <= 2000:
        return "Medium"
    return "High"


order_amount_category_udf = F.udf(order_amount_category, StringType())

# Apply order amount category UDF
orders_categorized = orders.withColumn("order_category", order_amount_category_udf(F.col("total_amount")))
orders_categorized.show()


# Phone masking python function and UDF registration
def mask_phone(phone):
    if phone is None:
        return None
    digits_start = phone.rfind("-") + 1
    prefix, number = phone[:digits_start], phone[digits_start:]
    if len(number) <= 4:
        return prefix + "X" * len(number)
    return prefix + "X" * (len(number) - 4) + number[-4:]


mask_phone_udf = F.udf(mask_phone, StringType())

# Apply phone masking UDF
customers_masked = customers_with_age.withColumn("phone_masked", mask_phone_udf(F.col("phone")))
customers_masked.select("customer_id", "phone", "phone_masked").show(truncate=False)

# Compare with native Spark functions
orders_native = orders.withColumn(
    "order_category_native",
    F.when(F.col("total_amount") < 500, "Low")
    .when(F.col("total_amount") <= 2000, "Medium")
    .otherwise("High")
)
orders_native.show()

# Write transformed customers with masked phone and age category to Parquet
customers_masked.write.mode("overwrite").parquet(f"{OUT_DIR}/customers_udf_processed")

# Read Parquet file back to verify write
df_saved = spark.read.parquet(f"{OUT_DIR}/customers_udf_processed")
df_saved.select("customer_id", "age_category", "phone_masked").show(truncate=False)

spark.stop()