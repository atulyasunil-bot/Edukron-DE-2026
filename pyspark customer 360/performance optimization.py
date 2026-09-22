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
    .appName("Mixed09_PerformanceOptimization")
    .master("local[2]")
    .getOrCreate()
)

OUT_DIR = "./output_perf_optimization"
os.makedirs(OUT_DIR, exist_ok=True)


def timed(label, fn):
    t0 = time.time()
    result = fn()
    elapsed = time.time() - t0
    print(f"{label}: {elapsed:.2f}s")
    return result, elapsed


# Synthetic dataset scaled for benchmarking
orders_count = 100_000
customers_count = 10_000
products_count = 500

customers = (
    spark.range(1, customers_count + 1)
    .withColumnRenamed("id", "customer_id")
    .withColumn("first_name", F.concat(F.lit("Cust_"), F.col("customer_id")))
)

products = (
    spark.range(1, products_count + 1)
    .withColumnRenamed("id", "product_id")
    .withColumn("product_name", F.concat(F.lit("Product_"), F.col("product_id")))
    .withColumn(
        "category",
        F.when(F.col("product_id") % 3 == 0, "Electronics")
        .when(F.col("product_id") % 3 == 1, "Furniture")
        .otherwise("Apparel")
    )
)

orders = (
    spark.range(1, orders_count + 1)
    .withColumnRenamed("id", "order_id")
    .withColumn("customer_id", (F.rand(seed=42) * customers_count).cast("int") + 1)
    .withColumn("order_status", F.when(F.col("order_id") % 10 == 0, "Cancelled").otherwise("Completed"))
)

order_items = (
    spark.range(1, orders_count * 2)
    .withColumnRenamed("id", "item_id")
    .withColumn("order_id", (F.rand(seed=12) * orders_count).cast("int") + 1)
    .withColumn("product_id", (F.rand(seed=34) * products_count).cast("int") + 1)
    .withColumn("item_amount", F.round((F.rand(seed=56) * 500) + 10, 2))
)


def build_pipeline(orders_df, customers_df, order_items_df, products_df):
    filtered_orders = orders_df.filter(F.col("order_status") != "Cancelled")
    orders_customers = filtered_orders.join(customers_df, "customer_id")
    items_products = order_items_df.join(products_df, "product_id")
    order_level = (
        orders_customers.join(items_products, "order_id")
        .withColumn("revenue", F.round(F.col("item_amount"), 2))
    )
    customer_revenue = order_level.groupBy("customer_id").agg(F.round(F.sum("revenue"), 2).alias("customer_revenue"))
    product_revenue = order_level.groupBy("product_id").agg(F.round(F.sum("revenue"), 2).alias("product_revenue"))
    category_revenue = order_level.groupBy("category").agg(F.round(F.sum("revenue"), 2).alias("category_revenue"))
    return order_level, customer_revenue, product_revenue, category_revenue


# Experiment 1: No caching (full DAG recomputed per action)
order_level1, cust_rev1, prod_rev1, cat_rev1 = build_pipeline(orders, customers, order_items, products)
_, t_no_cache = timed(
    "Experiment 1 (no caching, 3 actions)",
    lambda: (cust_rev1.count(), prod_rev1.count(), cat_rev1.count())
)

# Experiment 2: Default caching
order_level2, cust_rev2, prod_rev2, cat_rev2 = build_pipeline(orders, customers, order_items, products)
order_level2.cache()
order_level2.count()
_, t_cache = timed(
    "Experiment 2 (order_level cached, 3 actions)",
    lambda: (cust_rev2.count(), prod_rev2.count(), cat_rev2.count())
)
order_level2.unpersist()

# Experiment 3: Explicit persist level (MEMORY_AND_DISK)
order_level3, cust_rev3, prod_rev3, cat_rev3 = build_pipeline(orders, customers, order_items, products)
order_level3.persist(StorageLevel.MEMORY_AND_DISK)
order_level3.count()
_, t_persist = timed(
    "Experiment 3 (order_level persist MEMORY_AND_DISK, 3 actions)",
    lambda: (cust_rev3.count(), prod_rev3.count(), cat_rev3.count())
)
order_level3.unpersist()

print(f"\nBenchmark Summary: no-cache={t_no_cache:.2f}s | cache()={t_cache:.2f}s | persist()={t_persist:.2f}s\n")

# Experiment 4: Repartition versus Coalesce
print("Initial partition count:", orders.rdd.getNumPartitions())

repart = orders.repartition(8)
print("After repartition(8):", repart.rdd.getNumPartitions(), "partitions (full shuffle)")

coal = orders.coalesce(1)
print("After coalesce(1):", coal.rdd.getNumPartitions(), "partitions (no shuffle, merges partitions)")

timed("Write after repartition(8)", lambda: repart.write.mode("overwrite").parquet(f"{OUT_DIR}/_perf_repart"))
timed("Write after coalesce(1)", lambda: coal.write.mode("overwrite").parquet(f"{OUT_DIR}/_perf_coalesce"))

# Experiment 5: Join strategies (Sort-Merge vs Broadcast)
print("\nExperiment 5: Join strategies")

# Sort-Merge / Shuffle Hash join between two large tables
t0 = time.time()
order_items.join(orders.select("order_id", "customer_id"), "order_id").count()
print(f"Sort-Merge join (order_items x orders): {time.time() - t0:.2f}s")
order_items.join(orders.select("order_id", "customer_id"), "order_id").explain()

# Broadcast join using small dimension table
t0 = time.time()
order_items.join(F.broadcast(products.select("product_id", "category")), "product_id").count()
print(f"Broadcast join (order_items x products): {time.time() - t0:.2f}s")
order_items.join(F.broadcast(products.select("product_id", "category")), "product_id").explain()

spark.stop()
