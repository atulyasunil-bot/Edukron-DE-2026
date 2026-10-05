# Notebook

```python
# Databricks notebook source
# MAGIC %md
# MAGIC Goal and concepts-
# MAGIC SparkSession; driver and executors; lazy evaluation; transformations and actions; schemas.

# COMMAND ----------

# MAGIC %md
# MAGIC 1.Create an environment and run the dataset generator.
# MAGIC
# MAGIC 2.Start local[2] with UTC timestamps and four shuffle partitions.
# MAGIC
# MAGIC 3.Read orders.csv and print its schema, count, and ten rows.
# MAGIC
# MAGIC 4.Select order_id, customer_id, status and explain what triggers execution.
# MAGIC
# MAGIC 5.Create a five-row DataFrame manually with an explicit schema.

# COMMAND ----------

#1.
print(os.listdir(f"{BASE}/data/raw"))

# COMMAND ----------

spark.conf.set("spark.sql.session.timeZone", "UTC")
spark.conf.set("spark.sql.shuffle.partitions", "4")   # may be blocked on serverless

print(spark.conf.get("spark.sql.session.timeZone"))
print(spark.conf.get("spark.sql.shuffle.partitions"))

# COMMAND ----------

orders = spark.read.option("header", True).csv(f"{BASE}/data/raw/orders.csv")
orders.printSchema()
print(orders.count())          # 300, matches the manifest
orders.show(10, truncate=False)

# COMMAND ----------

slim = orders.select("order_id", "customer_id", "status")   # lazy, nothing runs
slim.show(10, truncate=False)                                # action, this runs the job

# COMMAND ----------

from pyspark.sql import types as T

cust_schema = T.StructType([
    T.StructField("customer_id", T.StringType(), True),
    T.StructField("name", T.StringType(), True),
    T.StructField("city", T.StringType(), True),
])
customers = spark.createDataFrame(
    [("C1", "Asha", "Bengaluru"), ("C2", "Ravi", "Mumbai"),
     ("C3", "Meera", "Delhi"), ("C4", "Kiran", "Pune"), ("C5", "Zoya", "Chennai")],
    schema=cust_schema)
customers.printSchema()
customers.show()

# COMMAND ----------

# MAGIC %md
# MAGIC 1.Filter orders for store S01. Create your own tiny fixture, predict the result, and then verify it in Spark.
# MAGIC
# MAGIC 2.Count orders by channel. Create your own tiny fixture, predict the result, and then verify it in Spark.
# MAGIC
# MAGIC 3.Compare show(), take(3), and collect() on a tiny subset. Create your own tiny fixture, predict the result, and then verify it in Spark.
# MAGIC
# MAGIC 4.Change one assumption in today's business logic and explain how the output changes.
# MAGIC
# MAGIC 5.Add one edge-case check that fails when you intentionally break your code.

# COMMAND ----------

from pyspark.sql import functions as F

schema = "order_id string, customer_id string, store_id string, channel string, status string"
rows = [
    ("O1", "C1", "S01", "web",   "completed"),
    ("O2", "C2", "S01", "store", "cancelled"),
    ("O3", "C3", "S02", "web",   "completed"),
    ("O4", "C4", "S02", "app",   "completed"),
    ("O5", "C5", "S03", "web",   "cancelled"),
    ("O6", "C1", "S01", "app",   "completed"),
]
fx = spark.createDataFrame(rows, schema)

# 1) Filter store S01. Prediction: O1, O2, O6
ids = {r["order_id"] for r in fx.filter(F.col("store_id") == "S01").collect()}
print("1) expected: ['O1','O2','O6'] | actual:", sorted(ids))
assert ids == {"O1", "O2", "O6"}


# COMMAND ----------

# 2) Count by channel. Prediction: web=3, store=1, app=2
counts = {r["channel"]: r["count"] for r in fx.groupBy("channel").count().collect()}
print("2) expected: web=3, store=1, app=2 | actual:", counts)
assert counts == {"web": 3, "store": 1, "app": 2}

# COMMAND ----------

# 3) show vs take vs collect. Prediction: None, 3 rows, 6 rows
shown = fx.show(3)
taken = fx.take(3)
collected = fx.collect()
print("3) show returned:", shown, "| take:", len(taken), "| collect:", len(collected))
assert shown is None and len(taken) == 3 and len(collected) == 6

# COMMAND ----------

# 4) Changed assumption: only completed orders count. Prediction: web=2, app=2, no store
changed = {r["channel"]: r["count"]
           for r in fx.filter(F.col("status") == "completed").groupBy("channel").count().collect()}
print("4) expected: web=2, app=2 | actual:", changed)
assert changed == {"web": 2, "app": 2}

# COMMAND ----------

# 5) Edge case: a null channel must not be lost. Correct passes, broken fails.
fx_null = spark.createDataFrame(rows + [("O7", "C6", "S02", None, "completed")], schema)

def good(df):
    return {r["channel"]: r["count"] for r in df.groupBy("channel").count().collect()}

def broken(df):
    return {r["channel"]: r["count"]
            for r in df.filter(F.col("channel").isNotNull()).groupBy("channel").count().collect()}

total = fx_null.count()
assert sum(good(fx_null).values()) == total
print("5) correct version passed:", sum(good(fx_null).values()), "==", total)
try:
    assert sum(broken(fx_null).values()) == total
    print("5) UNEXPECTED: broken version passed")
except AssertionError:
    print("5) broken version failed as intended:", sum(broken(fx_null).values()), "!=", total)

# COMMAND ----------

# MAGIC %md
# MAGIC Daily question bank - 30 questions

# COMMAND ----------

# MAGIC %md
# MAGIC Foundation questions (1-10)
# MAGIC
# MAGIC 1.What problem does PySpark solve when retail data outgrows one computer?
# MAGIC
# MAGIC 2.What is a SparkSession, and how do you create one?
# MAGIC
# MAGIC 3.What does local[2] mean in the supplied setup?
# MAGIC
# MAGIC 4.What is the driver's role in a Spark application?
# MAGIC
# MAGIC 5.What work is performed by executors?
# MAGIC
# MAGIC 6.What is a DataFrame, and what does its schema describe?
# MAGIC
# MAGIC 7.How do transformations differ from actions?
# MAGIC
# MAGIC 8.Why does constructing a filter not immediately read every row?
# MAGIC
# MAGIC 9.How do you display five orders without collecting the whole table?
# MAGIC
# MAGIC 10.How do you stop a SparkSession after an assignment?

# COMMAND ----------

# MAGIC %md
# MAGIC 1.When a retailer has millions of orders, one computer gets too slow or runs out of memory. PySpark lets me split the data into pieces, process the pieces at the same time on many cores or machines, and join the results.

# COMMAND ----------

# MAGIC %md
# MAGIC 2.It's the first step to Spark. Everything I do, like reading a file or building a DataFrame, starts from it. Locally I create it with SparkSession.builder.master("local[2]").appName("day01").getOrCreate(). In Databricks I don't create it, because a spark object is already there in every notebook.

# COMMAND ----------

# MAGIC %md
# MAGIC 3.It means Spark runs on my own computer with no cluster, using 2 worker threads. So two tasks can run at once.

# COMMAND ----------

# MAGIC %md
# MAGIC 4.The driver is the manager. It runs the code, works out the plan for what needs doing, breaks the plan into small tasks, hands the tasks out, and gathers the results back. whenever I use print or collect() commands ends up on the driver.

# COMMAND ----------

# MAGIC %md
# MAGIC 5.Executors are the workers. They do the actual tasks on their own slices of the data, such as reading file chunks, filtering rows and counting. They can also hold cached data, and they send results back to the driver.

# COMMAND ----------

# MAGIC %md
# MAGIC 6.A DataFrame is a table of rows and named columns, like a spreadsheet, but spread across many machines. The schema is its blueprint. It lists each column's name, its data type (string, integer, timestamp and so on) and whether it can be null.

# COMMAND ----------

# MAGIC %md
# MAGIC 7.A transformation, such as select, filter or withColumn, only describes  and gives back a new DataFrame, and nothing runs yet. 
# MAGIC An action, such as show, count, take or collect, forces Spark to actually do the work and give me a result.

# COMMAND ----------

# MAGIC %md
# MAGIC 8.Spark is lazy. When I write a filter, it only adds a step to a plan. It waits until an action asks for a result, and then it can look at the whole plan and run it in the cheapest way. This saves work if I never need the data, or if later steps let it skip rows.

# COMMAND ----------

# MAGIC %md
# MAGIC 9.I use orders.show(5), which prints just five rows. orders.limit(5) also works. Both stop early, so the full table is never pulled into the driver's memory.

# COMMAND ----------

# MAGIC %md
# MAGIC 10.Locally I call spark.stop(), which frees the resources. In Databricks I shouldn't call it, because the platform manages the session and stopping it can break the notebook. I just finish the notebook or detach the compute.

# COMMAND ----------

# MAGIC %md
# MAGIC Hands-on questions (11-20)
# MAGIC 1.Read orders.csv and verify its row count against the manifest.
# MAGIC
# MAGIC 2.Print the order schema and identify columns read as strings.
# MAGIC
# MAGIC 3.Select order_id, customer_id, and status and display ten rows.
# MAGIC
# MAGIC 4.Filter orders from S01 and display only their IDs.
# MAGIC
# MAGIC 5.Count completed and cancelled orders separately without using Python loops.
# MAGIC
# MAGIC 6.Create a five-row customer DataFrame with an explicit string schema.
# MAGIC
# MAGIC 7.Rename status to order_status without altering the source DataFrame.
# MAGIC
# MAGIC 8.Find the distinct channel values and explain why the result is small.
# MAGIC
# MAGIC 9.Compare show(3), take(3), and collect() on a five-row fixture.
# MAGIC
# MAGIC 10.Set the session timezone to UTC and verify the configuration value.

# COMMAND ----------

import json
from pyspark.sql import functions as F
from pyspark.sql import types as T

BASE = "/Volumes/pyspark_assignment1/default/retail_course"
orders = spark.read.option("header", True).csv(f"{BASE}/data/raw/orders.csv")

# Q11: row count vs manifest
with open(f"{BASE}/data/manifest.json") as f:
    manifest = json.load(f)
n, expected = orders.count(), manifest["raw_counts"]["orders"]
print("Q11 actual:", n, "| manifest:", expected)
assert n == expected

# COMMAND ----------

# Q12: schema (all columns come in as string because there is no inferSchema)
print("Q12 schema:")
orders.printSchema()
print("Q12 string columns:", [f.name for f in orders.schema.fields
                              if isinstance(f.dataType, T.StringType)])

# COMMAND ----------

# Q13: select three columns, show ten rows
print("Q13:")
orders.select("order_id", "customer_id", "status").show(10, truncate=False)

# COMMAND ----------

# Q14: S01 orders, IDs only
print("Q14:")
orders.filter(F.col("store_id") == "S01").select("order_id").show(truncate=False)

# COMMAND ----------

# Q15: completed vs cancelled, no Python loop
print("Q15:")
(orders.filter(F.col("status").isin("completed", "cancelled"))
       .groupBy("status").count().show())


# COMMAND ----------

# Q16: five-row customer DataFrame, explicit all-string schema
cust_schema = T.StructType([
    T.StructField("customer_id", T.StringType(), True),
    T.StructField("name", T.StringType(), True),
    T.StructField("city", T.StringType(), True),
])
customers = spark.createDataFrame(
    [("C1", "Asha", "Bengaluru"), ("C2", "Ravi", "Mumbai"),
     ("C3", "Meera", "Delhi"), ("C4", "Kiran", "Pune"), ("C5", "Zoya", "Chennai")],
    schema=cust_schema)
print("Q16:")
customers.printSchema()
customers.show()


# COMMAND ----------

# Q17: rename without touching the source
renamed = orders.withColumnRenamed("status", "order_status")
print("Q17 source columns:", orders.columns)
print("Q17 renamed columns:", renamed.columns)
assert "status" in orders.columns and "order_status" in renamed.columns


# COMMAND ----------

# Q18: distinct channels
channels = orders.select("channel").distinct()
print("Q18 distinct channels:", channels.count())
channels.show()

# COMMAND ----------

# Q19: show(3) vs take(3) vs collect() on a five-row fixture
five = customers          
shown = five.show(3)
taken = five.take(3)
collected = five.collect()
print("Q19 show returned:", shown, "| take length:", len(taken), "| collect length:", len(collected))

# COMMAND ----------

# Q20: set and verify the timezone
spark.conf.set("spark.sql.session.timeZone", "UTC")
print("Q20 timezone:", spark.conf.get("spark.sql.session.timeZone"))

# COMMAND ----------

# MAGIC %md
# MAGIC Advance question
# MAGIC
# MAGIC 21.Predict how many actions run when the same filtered DataFrame is counted twice.
# MAGIC
# MAGIC 22.Explain why reading 300 rows locally does not demonstrate cluster scalability.
# MAGIC
# MAGIC 23.Reproduce an unresolved-column error and explain its message.
# MAGIC
# MAGIC 24.Explain why DataFrame rows have no guaranteed order unless explicitly sorted.
# MAGIC
# MAGIC 25.Show that withColumn returns a new DataFrame rather than mutating the original.
# MAGIC
# MAGIC 26.Design a safe inspection strategy for a billion-row orders table.
# MAGIC
# MAGIC 27.Compare where SparkSession objects and distributed row data live.
# MAGIC
# MAGIC 28.Identify driver-side Python code and distributed work in your solution.
# MAGIC
# MAGIC 29.Predict when a missing input path fails: during read construction or an action; verify.
# MAGIC
# MAGIC 30.Write a reusable session factory and a five-row smoke-check script.

# COMMAND ----------

from pyspark.sql import SparkSession, functions as F

BASE = "/Volumes/pyspark_assignment1/default/retail_course"
orders = spark.read.option("header", True).csv(f"{BASE}/data/raw/orders.csv")

# Q21: same filtered DataFrame counted twice = two actions, two separate runs
s01 = orders.filter(F.col("store_id") == "S01")   
c1 = s01.count()                                     
c2 = s01.count()                                      
print("Q21 counts:", c1, c2, "-> 2 actions ran")

# COMMAND ----------

# Q23: unresolved column error
try:
    orders.select("no_such_column").show()
except Exception as e:
    print("Q23 error type:", type(e).__name__)
    print("Q23 message:", str(e)[:400])

# COMMAND ----------

# Q24: no guaranteed order unless sorted
print("Q24 unsorted first 5:", [r["order_id"] for r in orders.limit(5).collect()])
print("Q24 sorted first 5:  ", [r["order_id"] for r in orders.orderBy("order_id").limit(5).collect()])

# COMMAND ----------

# Q25: withColumn returns a new DataFrame
with_flag = orders.withColumn("is_s01", F.col("store_id") == "S01")
print("Q25 original columns:", orders.columns)
print("Q25 new columns:     ", with_flag.columns)
assert "is_s01" not in orders.columns and "is_s01" in with_flag.columns

# COMMAND ----------

# Q26: safe inspection of a huge table (never collect the whole thing)
orders.printSchema()                                  
orders.limit(5).show()                                 
orders.sample(0.01, seed=1).limit(10).show()          
print("Q26 rows for one store:", orders.filter(F.col("store_id") == "S01").count())

# COMMAND ----------

# Q29: when does a missing path fail?
stage = "read construction"
try:
    missing = spark.read.option("header", True).csv(f"{BASE}/data/raw/does_not_exist.csv")
    stage = "action (.count)"
    missing.count()
except Exception as e:
    print("Q29 failed during:", stage, "| error type:", type(e).__name__)
    print("Q29 message:", str(e)[:200])

# COMMAND ----------

# Q30: session factory + five-row smoke check
def get_spark(app_name="day01"):
    s = SparkSession.builder.appName(app_name).getOrCreate()   # returns the existing session in Databricks
    s.conf.set("spark.sql.session.timeZone", "UTC")
    return s

def smoke_check(s):
    rows = [("O1", "C1", "S01", "web", "completed"),
            ("O2", "C2", "S01", "store", "cancelled"),
            ("O3", "C3", "S02", "web", "completed"),
            ("O4", "C4", "S02", "app", "completed"),
            ("O5", "C5", "S03", "web", "cancelled")]
    df = s.createDataFrame(rows, "order_id string, customer_id string, store_id string, "
                                 "channel string, status string")
    assert df.count() == 5
    assert df.filter(F.col("store_id") == "S01").count() == 2
    by = {r["channel"]: r["count"] for r in df.groupBy("channel").count().collect()}
    assert by == {"web": 3, "store": 1, "app": 1}, by
    return "smoke check passed"

print("Q30:", smoke_check(get_spark()))

# COMMAND ----------

# MAGIC %md
# MAGIC Completion checks
# MAGIC
# MAGIC 1.The raw orders count equals data/manifest.json;
# MAGIC 2.explain why collect() is unsafe for large data. 
# MAGIC 3.Complete all 30 numbered daily questions, retaining expected-versus-actual evidence for coding exercises and written reasoning for conceptual/design questions.
# MAGIC 4.Compare values and business keys, not only row counts.
# MAGIC 5.Save the input fixture and expected rows for at least one example.
# MAGIC 6.Sort only when presentation or a deterministic comparison needs it.

# COMMAND ----------

import csv, json, os
from pyspark.sql import functions as F

BASE = "/Volumes/pyspark_assignment1/default/retail_course"
OUT = f"{BASE}/outputs/day01"
os.makedirs(OUT, exist_ok=True)

orders = spark.read.option("header", True).csv(f"{BASE}/data/raw/orders.csv")
with open(f"{BASE}/data/manifest.json") as f:
    manifest = json.load(f)

# 1) Manifest check on count AND business key (order_id is the key, one row per order)
n = orders.count()
n_distinct = orders.select("order_id").distinct().count()
null_keys = orders.filter(F.col("order_id").isNull() | (F.trim("order_id") == "")).count()
print("rows:", n, "| distinct order_id:", n_distinct, "| null/blank keys:", null_keys,
      "| manifest:", manifest["raw_counts"]["orders"])
assert n == n_distinct == manifest["raw_counts"]["orders"] and null_keys == 0

# COMMAND ----------

# 2) Values, not just counts: status split must match the manifest's completed_orders
completed = orders.filter(F.col("status") == "completed").count()
print("completed:", completed, "| manifest:", manifest["completed_orders"])
assert completed == manifest["completed_orders"]


# COMMAND ----------

# 3) Referential check on keys (orders should point to known customers and stores)
customers = spark.read.option("header", True).csv(f"{BASE}/data/raw/customers.csv")
stores = spark.read.option("header", True).csv(f"{BASE}/data/raw/stores.csv")
print("orders with unknown customer:", orders.join(customers, "customer_id", "left_anti").count())
print("orders with unknown store:   ", orders.join(stores, "store_id", "left_anti").count())

# COMMAND ----------

# 4) Saved fixture + expected rows (compared by full row values, not only counts)
fixture = [
    ("O1", "C1", "S01", "web",   "completed"),
    ("O2", "C2", "S01", "store", "cancelled"),
    ("O3", "C3", "S02", "web",   "completed"),
    ("O4", "C4", "S02", "app",   "completed"),
    ("O5", "C5", "S03", "web",   "cancelled"),
    ("O6", "C1", "S01", "app",   "completed"),
]
cols = ["order_id", "customer_id", "store_id", "channel", "status"]
expected_s01 = [r for r in fixture if r[2] == "S01"]   # my prediction, written by hand

with open(f"{OUT}/fixture_orders.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(cols); w.writerows(fixture)
with open(f"{OUT}/expected_s01.json", "w") as f:
    json.dump([dict(zip(cols, r)) for r in expected_s01], f, indent=2)

fx = spark.createDataFrame(fixture, ", ".join(f"{c} string" for c in cols))
actual_s01 = [tuple(r) for r in fx.filter(F.col("store_id") == "S01").collect()]

# COMMAND ----------

# Sorting here is needed only because Spark gives no row order; it makes the comparison deterministic
assert sorted(actual_s01) == sorted(expected_s01)
print("fixture S01 rows match expected:", sorted(actual_s01))
print("saved:", os.listdir(OUT))

# COMMAND ----------

# MAGIC %md
# MAGIC REVIEW QUESTIONS 
# MAGIC 1. What is the input and output grain, and which operation can change the row count?
# MAGIC
# MAGIC The input grain is one row per order, and order_id is the key. I checked this in Cell 3: 300 rows and 300 distinct order_id values. The output grain depends onselect, withColumnRenamed and withColumn keep it at one row per order, so the count stays 300.
# MAGIC filter can reduce the row count, for example S01 orders only.
# MAGIC distinct reduces it to one row per unique value, which gives the small channel list.
# MAGIC groupBy(...).count() changes the grain completely, to one row per status or per channel.
# MAGIC limit and sample cut the row count to a fixed or random number.
# MAGIC
# MAGIC 2. Which null, duplicate, time, or retry case could make today's result wrong?
# MAGIC
# MAGIC Null: blank CSV cells read as null. A null status would drop out of my completed and cancelled counts without any error. A null channel forms its own group in groupBy, which is why my edge-case example (Ex5) counts it, and why dropping nulls makes the totals disagree.
# MAGIC
# MAGIC Duplicate: if the same order_id appeared twice, my counts would be too high. I checked for this in Cell 3, and the result was 0 duplicates. Repeated order_id is expected only in order lines, not in orders.
# MAGIC
# MAGIC Time: order_ts arrives as a text string, not a timestamp. Sorting or comparing it as text could give wrong answers, and any later conversion depends on the session timezone, which is why I set it to UTC.
# MAGIC
# MAGIC Retry: running the notebook again is safe today because it only reads data. But uploading the files twice or rerunning the generator could create extra copies, like the misplaced data/data/ folder I had. A wrong layout would double-count or break the paths.
# MAGIC
# MAGIC 3. Which action executes your work, and where could a shuffle or state growth occur?
# MAGIC
# MAGIC The actions are show(), count(), take() and collect(). select, filter and withColumn are lazy and run nothing until an action needs a result.
# MAGIC
# MAGIC Shuffles happen when rows with the same key have to be brought together across partitions:
# MAGIC
# MAGIC groupBy(...).count(), as in my status and channel counts.
# MAGIC distinct(), which needs to compare rows across partitions.
# MAGIC orderBy(), which sorts across all the data.
# MAGIC
# MAGIC filter, select and withColumn need no shuffle. I set shuffle partitions to 4 where Databricks allowed it, and it was set to 4. State growth does not apply because this is batch work, and nothing stays in memory between runs. It matters in streaming days, where state grows as Spark remembers events.

# COMMAND ----------

# MAGIC %md STRETCH CHALLENGE
# MAGIC
# MAGIC Turn today's logic into a reusable function with explicit inputs and document one scale limitation. For streaming days, include a saved lastProgress record and explain state and checkpoint behavior.

# COMMAND ----------

from pyspark.sql import DataFrame, functions as F

def summarize_orders(orders: DataFrame,
                     group_col: str = "channel",
                     store_id: str | None = None,
                     statuses: tuple = ("completed", "cancelled"),
                     max_groups: int = 100) -> dict:
   
    df = orders if store_id is None else orders.filter(F.col("store_id") == store_id)

    total = df.count()
    distinct_ids = df.select("order_id").distinct().count()

    # refuse to pull a big grouped result to the driver
    grouped = df.groupBy(group_col).count().limit(max_groups + 1).collect()
    if len(grouped) > max_groups:
        raise ValueError(f"{group_col} has more than {max_groups} groups; "
                         f"refusing to collect it to the driver")

    by_status = (df.filter(F.col("status").isin(*statuses))
                   .groupBy("status").count().collect())

    return {
        "total_rows": total,
        "distinct_order_ids": distinct_ids,
        "by_group": {r[group_col]: r["count"] for r in grouped},
        "by_status": {r["status"]: r["count"] for r in by_status},
    }


# Test 1: tiny fixture with predictions
schema = "order_id string, customer_id string, store_id string, channel string, status string"
rows = [
    ("O1", "C1", "S01", "web",   "completed"),
    ("O2", "C2", "S01", "store", "cancelled"),
    ("O3", "C3", "S02", "web",   "completed"),
    ("O4", "C4", "S02", "app",   "completed"),
    ("O5", "C5", "S03", "web",   "cancelled"),
    ("O6", "C1", "S01", "app",   "completed"),
]
fx = spark.createDataFrame(rows, schema)

all_stores = summarize_orders(fx)
assert all_stores == {"total_rows": 6, "distinct_order_ids": 6,
                      "by_group": {"web": 3, "store": 1, "app": 2},
                      "by_status": {"completed": 4, "cancelled": 2}}

s01 = summarize_orders(fx, store_id="S01")
assert s01["total_rows"] == 3 and s01["by_status"] == {"completed": 2, "cancelled": 1}

# Test 2: the safety limit fires when the grouping column has too many values
try:
    summarize_orders(fx, group_col="order_id", max_groups=3)
    print("UNEXPECTED: limit did not fire")
except ValueError as e:
    print("limit fired as intended:", e)

# Test 3: run on the real data
BASE = "/Volumes/pyspark_assignment1/default/retail_course"
orders = spark.read.option("header", True).csv(f"{BASE}/data/raw/orders.csv")
print(summarize_orders(orders))

# COMMAND ----------

import json, base64

ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
nb_path = ctx.notebookPath().get()

# Export the notebook source through the workspace API
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ExportFormat

w = WorkspaceClient()
resp = w.workspace.export(nb_path, format=ExportFormat.SOURCE)
source = base64.b64decode(resp.content).decode("utf-8")

with open("/Workspace/Shared/answer.md", "w") as f:
    f.write("# Notebook\n\n```python\n" + source + "\n```\n")

print("Saved full notebook code to /Workspace/Shared/answer.md")
```
