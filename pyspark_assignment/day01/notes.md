# Day 01 Notes

## Assumptions
- Columns used (confirmed in DATA_DICTIONARY.md): order_id, customer_id, store_id, order_ts, status, channel. Statuses `completed` and `cancelled`.
- Platform: Databricks notebook (`assignment_databricks.py`). Data is in a Unity Catalog Volume at `/Volumes/pyspark_assignment1/default/retail_course/data/`.
- `spark` is pre-created, so `local[2]` could not be set. UTC set with `spark.conf.set`; shuffle partitions 4: ____ (set / blocked).
- The dataset generator ran on my computer (standard Python only) and I uploaded the output to the volume.
- All CSV columns are read as strings (no type guessing). `spark.stop()` is not called in Databricks.

## What triggers execution
`select` and `filter` only build a plan. `show()`, `count()`, `take()` and `collect()` are actions that run the job.

## One error I fixed
`FileNotFoundError` for `.../data/raw`: the CSVs were uploaded straight into the volume root and `manifest.json` into `data/data/`. I listed the volume with `os.walk`, then moved the files with `shutil.move` into `data/raw/` and `data/`. I also hit `NameError: name 'n' is not defined` because I ran the manifest check before the cell that defines `n`; running cells in order fixed it.

## Completion evidence
- Raw orders count: 300 ; manifest: 300 ; match: 270
- Distinct order_id: 275  ; null keys: 0 ; completed: 300 (manifest 270)

- Schema summary (from `outputs/day01/schema_summary.txt`):
  ```
  order_id: string
  customer_id: string
  store_id: string
  order_ts: string
  status: string
  channel: string
  ```
- sample: first rows of `outputs/day01/orders_sample.csv` (paste 3-5 rows here)
- Why `collect()` is unsafe: it pulls all rows into the driver's memory, which can crash it, and moves all data over the network.

## Extra examples (expected vs actual)
| Example | Expected | Actual |
|---|---|---|
| 1. Fixture: S01 orders | O1, O2, O6 | ____ |
| 2. Fixture: count by channel | web=3, store=1, app=2 | ____ |
| 3. show / take / collect | None, 3 rows, 6 rows | ____ |
| 4. Changed assumption: only completed orders | web=2, app=2, no store | ____ |
| 5. Edge case: null channel | correct code 7 = 7; broken code fails (6 != 7) | ____ |

Example 4 explanation: counting only completed orders drops the total from 6 to 4, web goes from 3 to 2 and `store` disappears, because its only order was cancelled.


QUESTIONS AND ANSWERS

11. Read orders.csv and verify its row count against the manifest.
I read the file with spark.read.option("header", True).csv(...) and called count(). I got 300 rows. The manifest lists 300 under raw_counts.orders, so they match. I added an assert so the code stops with an error if the two numbers ever differ.

12. Print the order schema and identify columns read as strings.
printSchema() shows that all six columns are strings: order_id, customer_id, store_id, order_ts, status and channel. That's because I didn't ask Spark to guess types, so it treats everything in a CSV as text. order_ts is really a timestamp, but it comes in as text for now. A later day will fix this with an explicit schema.

13. Select order_id, customer_id, and status and display ten rows.
I wrote orders.select("order_id", "customer_id", "status").show(10, truncate=False). The select only describes what I want, and show is what actually runs it and prints ten rows.

14. Filter orders from S01 and display only their IDs.
I filtered with store_id == "S01" and then selected just order_id. It shows only the IDs of orders from store S01, nothing else.

15. Count completed and cancelled orders separately without using Python loops.
I filtered to the two statuses, grouped by status and counted, so Spark gives me one count per status in a single step. My output was completed = ____ and cancelled = ____ (the manifest suggests 270 and 30, so check yours against that).

16. Create a five-row customer DataFrame with an explicit string schema.
I made a schema with three string columns (customer_id, name, city) and passed five rows to spark.createDataFrame(...). Because I gave the schema myself, Spark didn't have to guess the types.

17. Rename status to order_status without altering the source DataFrame.
I used withColumnRenamed("status", "order_status"). The original orders still has status, and only the new DataFrame has order_status. DataFrames don't change in place, and every change gives back a new one.

18. Find the distinct channel values and explain why the result is small.
orders.select("channel").distinct() returned ____ channels (write the number and names you see). The result is small because distinct keeps one row for each unique value. Even with millions of orders, the number of channels stays the same.

19. Compare show(3), take(3), and collect() on a five-row fixture.
show(3) only prints three rows on screen and returns nothing. take(3) hands back a Python list holding three rows. collect() hands back a list of all five rows. On a big table, collect() is dangerous because it pulls every row into the driver's memory.

20. Set the session timezone to UTC and verify the configuration value.
I ran spark.conf.set("spark.sql.session.timeZone", "UTC") and then read it back with spark.conf.get(...), which printed UTC. Reading it back confirms the setting really took effect.

21. Predict how many actions run when the same filtered DataFrame is counted twice.
Two actions run, one for each count(). The filter itself is just a plan. Spark doesn't remember the result between the two counts, so it reads the file and applies the filter twice. If I wanted to avoid that, I'd call .cache() first. My output was ____ and ____.

22. Explain why reading 300 rows locally does not demonstrate cluster scalability.
300 rows fit easily in one process, so nothing is really being split up. There's no network travel, no costly shuffling, no uneven partitions and no machines failing. It proves my logic is correct, but it says nothing about how the job behaves with millions of rows on many machines.

23. Reproduce an unresolved-column error and explain its message.
Selecting "no_such_column" raises an AnalysisException. The message says Spark can't find a column with that name, and it usually suggests similar names that do exist. It happens before any data is read, because Spark checks column names against the schema while building the plan. My error type was ____.

24. Explain why DataFrame rows have no guaranteed order unless explicitly sorted.
The data is stored in partitions, and the partitions are processed in parallel and combined in whatever order they finish. So the order can change between runs. Only orderBy promises an order. In my output the unsorted first five were ____ and the sorted ones were ____.

25. Show that withColumn returns a new DataFrame rather than mutating the original.
After orders.withColumn("is_s01", ...), the new DataFrame has the extra is_s01 column. orders.columns is unchanged. The assert in my code checks both. DataFrames are immutable, so every change gives back a new one.

26. Design a safe inspection strategy for a billion-row orders table.
I'd never use collect(). I'd start with printSchema(), which costs almost nothing. Then I'd look at a few rows with limit(5).show(). For a feel of the data I'd take a tiny sample(0.01). For specific questions I'd filter first, for example one store or one day, and then count. Anything I want to keep, I'd write out as a small sample file.

27. Compare where SparkSession objects and distributed row data live.
The SparkSession is a Python object in the driver, which is the machine running my notebook. The rows live in partitions on the executors, which hold slices of the data. The driver only gets rows when I call something like take() or collect().

28. Identify driver-side Python code and distributed work in your solution.
Driver-side: my Python variables, building the schema, writing spark.read..., building the plan, print, and the results of take() and collect(). Distributed: the actual reading of the CSV, filter, groupBy, distinct and counting, which run as tasks on the executors.

29. Predict when a missing input path fails: during read construction or an action; verify.
My prediction was that it fails right at spark.read.csv(...), because Spark has to look at the file to build the schema (it reads the header). In Databricks the result was: failed during ____ with error type ____. If it fails at .count() instead, that means the check was delayed until the action, which can happen on serverless compute.

30. Write a reusable session factory and a five-row smoke-check script.
get_spark() returns the session and sets the timezone to UTC. getOrCreate() gives back the existing session in Databricks. smoke_check() builds a five-row table and uses asserts to check the total, the S01 filter (2 rows) and the channel counts (web=3, store=1, app=1). It prints smoke check passed when everything holds.


Why collect() is unsafe for large data (for your notes)

collect() brings every row from all the executors into one place, the driver's memory. On a small table that's fine. On a huge table it can make the driver run out of memory and crash the whole notebook. It also moves all the data across the network and is slow. Safer ways are show(n), take(n), limit(n), or filtering and aggregating first so only a small result reaches the driver.