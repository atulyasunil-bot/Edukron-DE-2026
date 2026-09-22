import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder
    .appName("Assignment11_StringFunctions")
    .master("local[2]")
    .getOrCreate()
)

OUT_DIR = "./output_string_functions"
os.makedirs(OUT_DIR, exist_ok=True)

# Sample customers dataset
customers_data = [
    (1, "aarav", "sharma", "aarav.sharma@gmail.com", "+91-9876543210", "  bengaluru  "),
    (2, "Meera", "patel", "meera_p@yahoo.co.in", "+1-4155552671", "mumbai"),
    (3, "rohan", "VERMA", "rohan.v@outlook.com", "+44-2071838750", "NEW   delhi"),
    (4, "Priya", "Nair", "priya_nair@corp.net", "+91-9123456780", "chennai "),
]
customers_cols = ["customer_id", "first_name", "last_name", "email", "phone", "city"]
customers = spark.createDataFrame(customers_data, customers_cols)

# Uppercase first name
customers.withColumn("first_name_upper", F.upper("first_name")).select("first_name", "first_name_upper").show()

# Lowercase first name
customers.withColumn("first_name_lower", F.lower("first_name")).select("first_name", "first_name_lower").show()

# Concatenate first and last name with space separator
customers_full = customers.withColumn("full_name", F.concat_ws(" ", F.initcap("first_name"), F.initcap("last_name")))
customers_full.select("full_name").show()

# Calculate character length of full name
customers_full.withColumn("name_length", F.length("full_name")).select("full_name", "name_length").show()

# Extract email username before the @ sign
customers.withColumn("email_username", F.regexp_extract("email", r"^([^@]+)@", 1)).select("email", "email_username").show()

# Clean and standardize city names to title case
transformed_customers = customers_full.withColumn(
    "city_standardized",
    F.initcap(F.trim(F.regexp_replace(F.col("city"), r"\s+", " ")))
)
transformed_customers.select("city", "city_standardized").show()

# Write transformed records to Parquet file
transformed_customers.write.mode("overwrite").parquet(f"{OUT_DIR}/customers_string_cleaned")

# Read Parquet file back to verify write
df_saved = spark.read.parquet(f"{OUT_DIR}/customers_string_cleaned")
df_saved.select("customer_id", "full_name", "city_standardized").show(truncate=False)

spark.stop()
