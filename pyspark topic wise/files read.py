import os
import shutil
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

spark = (
    SparkSession.builder
    .appName("Assignment01_FileReads")
    .master("local[2]")
    .getOrCreate()
)

# Hadoop crash
sc = spark.sparkContext
conf = sc._jsc.hadoopConfiguration()
conf.set("fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem")
try:
    native_io = sc._gateway.jvm.org.apache.hadoop.io.nativeio.NativeIO.Windows
    field = native_io.getClass().getDeclaredField("nativeLoaded")
    field.setAccessible(True)
    field.set(None, False)
except Exception:
    pass

print("=" * 60)
print("Assignment 1: Mastering File Reads & Formats in Spark")
print("=" * 60)

DATA_DIR = "./sample_data"
OUT_DIR = "./output_data"
os.makedirs(DATA_DIR, exist_ok=True)

# Setup sample files
with open(f"{DATA_DIR}/customers.csv", "w", encoding="utf-8") as f:
    f.write("customer_id,name,age,city\n")
    f.write("1,Aarav,28,Bengaluru\n")
    f.write("2,Meera,34,Mumbai\n")
    f.write("3,Rohan,22,Delhi\n")

with open(f"{DATA_DIR}/orders.csv", "w", encoding="utf-8") as f:
    f.write("order_id,customer_id,amount\n")
    f.write("5001,1,250.50\n")
    f.write("5002,2,499.00\n")

#  Raw Read
print("\n Raw Read ")
df_raw = spark.read.csv(f"{DATA_DIR}/customers.csv")
df_raw.show()

#  Read with header & inferSchema
print("\n CSV with Header + Inferred Schema ")
df_inferred = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{DATA_DIR}/customers.csv")
)
df_inferred.show()

# Read with explicit schema
print("\n CSV with User-Defined Schema ")
orders_schema = StructType([
    StructField("order_id", IntegerType(), True),
    StructField("customer_id", IntegerType(), True),
    StructField("amount", DoubleType(), True),
])
df_orders = spark.read.csv(f"{DATA_DIR}/orders.csv", header=True, schema=orders_schema)
df_orders.show()


spark.stop()