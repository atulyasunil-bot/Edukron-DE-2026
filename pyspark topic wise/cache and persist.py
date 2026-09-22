import os
import sys
import time

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark import StorageLevel
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder
    .appName("Assignment14_CacheAndPersist")
    .master("local[2]")
    .getOrCreate()
)

OUT_DIR = "./output_cache_persist"
os.makedirs(OUT_DIR, exist_ok=True)

# Generate a synthetic dataset large enough to demonstrate timing differences
rows_count = 200_000
orders = (
    spark.range(0, rows_count)
    .withColumn("order_id", F.col("id") + 1000)
    .withColumn("customer_id", (F.col("id") % 500) + 1)
    .withColumn("total_amount", F.round((F.rand(seed=42) * 5000) + 50, 2))
    .withColumn("discount_amount", F.round(F.col("total_amount") * 0.10, 2))
    .withColumn("shipping_cost", F.round((F.rand(seed=24) * 100) + 10, 2))
    .drop("id")
)

# Benchmark without cache: plan recomputes on each action
heavy_uncached = orders.filter(F.col("total_amount") > 100)

t0 = time.time()
heavy_uncached.agg(F.sum("total_amount")).collect()
heavy_uncached.agg(F.sum("discount_amount")).collect()
heavy_uncached.agg(F.sum("shipping_cost")).collect()
t_uncached = time.time() - t0
print(f"Without cache (3 actions): {t_uncached:.3f}s")

# Benchmark with cache: materialized after the first action
heavy_cached = orders.filter(F.col("total_amount") > 100).cache()
heavy_cached.count()

t0 = time.time()
heavy_cached.agg(F.sum("total_amount")).collect()
heavy_cached.agg(F.sum("discount_amount")).collect()
heavy_cached.agg(F.sum("shipping_cost")).collect()
t_cached = time.time() - t0
print(f"With cache (3 actions): {t_cached:.3f}s")

# Free memory by unpersisting
heavy_cached.unpersist()

# Demonstrate persist with an explicit StorageLevel
heavy_persisted = (
    orders
    .filter(F.col("total_amount") > 1000)
    .persist(StorageLevel.MEMORY_AND_DISK)
)

# Trigger materialization and persist to storage
heavy_persisted.count()

# Write persisted summary results to Parquet
summary_df = heavy_persisted.groupBy("customer_id").agg(
    F.count("order_id").alias("order_count"),
    F.round(F.sum("total_amount"), 2).alias("total_spend"),
    F.round(F.avg("total_amount"), 2).alias("avg_spend")
)
summary_df.write.mode("overwrite").parquet(f"{OUT_DIR}/customer_spend_summary")

# Read Parquet file back to verify write
df_saved = spark.read.parquet(f"{OUT_DIR}/customer_spend_summary")
df_saved.orderBy(F.col("total_spend").desc()).show(5, truncate=False)

# Free persisted storage
heavy_persisted.unpersist()

print("""
Conceptual Summary
------------------
1. Lazy Evaluation:
   Transformations (filter, select, groupBy) build an execution lineage (DAG).
   Computation is triggered only when an action (count, collect, write) is called.

2. cache() vs persist():
   cache() defaults to MEMORY_AND_DISK in modern Spark DataFrames.
   persist() accepts an explicit StorageLevel (e.g., MEMORY_ONLY, DISK_ONLY, MEMORY_AND_DISK_2).

3. When to Cache:
   - DataFrames reused across multiple downstream actions or queries.
   - Outputs of computationally heavy steps (wide joins, shuffles, UDFs).

4. When NOT to Cache:
   - Single-use DataFrames (adds memory/serialization overhead for zero reuse).
   - Datasets larger than available executor memory that trigger heavy disk spilling.
""")

spark.stop()