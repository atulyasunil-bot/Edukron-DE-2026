"""
Assignment 13 - UDF
=====================
"""
import sys
sys.path.insert(0, "/home/claude/solutions")
from pyspark.sql.functions import udf, col, year, when, datediff, current_date, regexp_replace
from pyspark.sql.types import StringType
from common import get_spark, read_customers, read_orders

spark = get_spark("assignment-13-udf")
customers = read_customers(spark)
orders = read_orders(spark)

COUNTRY_MAP = {"IN": "India", "US": "United States", "UK": "United Kingdom", "AU": "Australia", "SG": "Singapore"}

# 1. Normal Python function
def country_code_to_name(code):
    if code is None:
        return None
    return COUNTRY_MAP.get(code.upper(), "Unknown")

# 2. Convert into a PySpark UDF
country_name_udf = udf(country_code_to_name, StringType())

# 3. Apply it. This dataset's `country` column already holds full names
# (e.g. "India"), so demonstrate on a small made-up code column instead
# of pretending the sample data has 2-letter codes.
demo = spark.createDataFrame([("IN",), ("US",), ("UK",), ("AU",), ("SG",), ("ZZ",)], ["country_code"])
demo.withColumn("country_name", country_name_udf(col("country_code"))).show()

# 4. UDF that categorizes customers by age
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

age_category_udf = udf(age_category, StringType())
customers.withColumn("birth_year", year("date_of_birth")) \
         .withColumn("age_category", age_category_udf(col("birth_year"))) \
         .select("customer_id", "date_of_birth", "age_category").show(5)

# 5. UDF that categorizes orders by amount
def order_amount_category(amount):
    if amount is None:
        return None
    if amount < 500:
        return "Low"
    elif amount <= 2000:
        return "Medium"
    return "High"

order_amount_category_udf = udf(order_amount_category, StringType())
orders.withColumn("order_category", order_amount_category_udf(col("total_amount"))) \
      .select("order_id", "total_amount", "order_category").show(5)

# 6. UDF that masks phone numbers, e.g. "+91-6107420369" -> "+91-XXXXXX0369"
def mask_phone(phone):
    if phone is None:
        return None
    digits_start = phone.rfind("-") + 1
    prefix, number = phone[:digits_start], phone[digits_start:]
    if len(number) <= 4:
        return prefix + "X" * len(number)
    return prefix + "X" * (len(number) - 4) + number[-4:]

mask_phone_udf = udf(mask_phone, StringType())
customers.withColumn("phone_masked", mask_phone_udf(col("phone"))).select("phone", "phone_masked").show(5, truncate=False)

# Bonus: same order-amount categorization using native Spark functions
orders_native = orders.withColumn(
    "order_category_native",
    when(col("total_amount") < 500, "Low").when(col("total_amount") <= 2000, "Medium").otherwise("High"),
)
orders_native.select("order_id", "total_amount", "order_category_native").show(5)
# Conceptually: the native `when`/`otherwise` version runs inside the JVM
# and Catalyst can push it into the physical plan, reorder it, or skip it
# entirely via predicate pushdown. The UDF version serializes each row out
# to a Python worker process and back, which is much slower at scale and
# opaque to the Catalyst optimizer - use a UDF only when there really is
# no native function that expresses the logic (e.g. the phone-masking
# and dictionary-lookup UDFs above don't have a clean one-liner native
# equivalent; the amount-bucketing one does, so prefer `when` there).

spark.stop()
