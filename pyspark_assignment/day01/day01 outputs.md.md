Goal and concepts-
SparkSession; driver and executors; lazy evaluation; transformations and actions; schemas.

1.Create an environment and run the dataset generator.

2.Start local[2] with UTC timestamps and four shuffle partitions.

3.Read orders.csv and print its schema, count, and ten rows.

4.Select order_id, customer_id, status and explain what triggers execution.

5.Create a five-row DataFrame manually with an explicit schema.

    ['customers.csv', 'order_items.csv', 'orders.csv', 'products.csv', 'returns.csv', 'stores.csv']
    

    UTC
    4
    

    root
     |-- order_id: string (nullable = true)
     |-- customer_id: string (nullable = true)
     |-- store_id: string (nullable = true)
     |-- order_ts: string (nullable = true)
     |-- status: string (nullable = true)
     |-- channel: string (nullable = true)
    
    300
    +--------+-----------+--------+--------------------+---------+-------+
    |order_id|customer_id|store_id|order_ts            |status   |channel|
    +--------+-----------+--------+--------------------+---------+-------+
    |O0001   |C015       |S01     |2026-07-01T09:00:00Z|completed|store  |
    |O0002   |C004       |S01     |2026-07-02T10:00:00Z|completed|store  |
    |O0003   |C070       |S04     |2026-07-03T11:00:00Z|completed|online |
    |O0004   |C055       |S03     |2026-07-04T12:00:00Z|completed|store  |
    |O0005   |C078       |S03     |2026-07-05T13:00:00Z|completed|store  |
    |O0006   |C049       |S01     |2026-07-06T14:00:00Z|completed|online |
    |O0007   |C030       |S01     |2026-07-07T15:00:00Z|completed|store  |
    |O0008   |C022       |S05     |2026-07-08T16:00:00Z|completed|store  |
    |O0009   |C042       |S01     |2026-07-09T17:00:00Z|completed|online |
    |O0010   |C073       |S03     |2026-07-10T18:00:00Z|cancelled|store  |
    +--------+-----------+--------+--------------------+---------+-------+
    only showing top 10 rows
    

    +--------+-----------+---------+
    |order_id|customer_id|status   |
    +--------+-----------+---------+
    |O0001   |C015       |completed|
    |O0002   |C004       |completed|
    |O0003   |C070       |completed|
    |O0004   |C055       |completed|
    |O0005   |C078       |completed|
    |O0006   |C049       |completed|
    |O0007   |C030       |completed|
    |O0008   |C022       |completed|
    |O0009   |C042       |completed|
    |O0010   |C073       |cancelled|
    +--------+-----------+---------+
    only showing top 10 rows
    

    root
     |-- customer_id: string (nullable = true)
     |-- name: string (nullable = true)
     |-- city: string (nullable = true)
    
    +-----------+-----+---------+
    |customer_id| name|     city|
    +-----------+-----+---------+
    |         C1| Asha|Bengaluru|
    |         C2| Ravi|   Mumbai|
    |         C3|Meera|    Delhi|
    |         C4|Kiran|     Pune|
    |         C5| Zoya|  Chennai|
    +-----------+-----+---------+
    
    

1.Filter orders for store S01. Create your own tiny fixture, predict the result, and then verify it in Spark.

2.Count orders by channel. Create your own tiny fixture, predict the result, and then verify it in Spark.

3.Compare show(), take(3), and collect() on a tiny subset. Create your own tiny fixture, predict the result, and then verify it in Spark.

4.Change one assumption in today's business logic and explain how the output changes.

5.Add one edge-case check that fails when you intentionally break your code.

    1) expected: ['O1','O2','O6'] | actual: ['O1', 'O2', 'O6']
    

    2) expected: web=3, store=1, app=2 | actual: {'web': 3, 'store': 1, 'app': 2}
    

    +--------+-----------+--------+-------+---------+
    |order_id|customer_id|store_id|channel|   status|
    +--------+-----------+--------+-------+---------+
    |      O1|         C1|     S01|    web|completed|
    |      O2|         C2|     S01|  store|cancelled|
    |      O3|         C3|     S02|    web|completed|
    +--------+-----------+--------+-------+---------+
    only showing top 3 rows
    3) show returned: None | take: 3 | collect: 6
    

    4) expected: web=2, app=2 | actual: {'web': 2, 'app': 2}
    

    5) correct version passed: 7 == 7
    5) broken version failed as intended: 6 != 7
    

Daily question bank - 30 questions

Foundation questions (1-10)

1.What problem does PySpark solve when retail data outgrows one computer?

2.What is a SparkSession, and how do you create one?

3.What does local[2] mean in the supplied setup?

4.What is the driver's role in a Spark application?

5.What work is performed by executors?

6.What is a DataFrame, and what does its schema describe?

7.How do transformations differ from actions?

8.Why does constructing a filter not immediately read every row?

9.How do you display five orders without collecting the whole table?

10.How do you stop a SparkSession after an assignment?

1.When a retailer has millions of orders, one computer gets too slow or runs out of memory. PySpark lets me split the data into pieces, process the pieces at the same time on many cores or machines, and join the results.

2.It's the first step to Spark. Everything I do, like reading a file or building a DataFrame, starts from it. Locally I create it with SparkSession.builder.master("local[2]").appName("day01").getOrCreate(). In Databricks I don't create it, because a spark object is already there in every notebook.

3.It means Spark runs on my own computer with no cluster, using 2 worker threads. So two tasks can run at once.

4.The driver is the manager. It runs the code, works out the plan for what needs doing, breaks the plan into small tasks, hands the tasks out, and gathers the results back. whenever I use print or collect() commands ends up on the driver.

5.Executors are the workers. They do the actual tasks on their own slices of the data, such as reading file chunks, filtering rows and counting. They can also hold cached data, and they send results back to the driver.

6.A DataFrame is a table of rows and named columns, like a spreadsheet, but spread across many machines. The schema is its blueprint. It lists each column's name, its data type (string, integer, timestamp and so on) and whether it can be null.

7.A transformation, such as select, filter or withColumn, only describes  and gives back a new DataFrame, and nothing runs yet. 
An action, such as show, count, take or collect, forces Spark to actually do the work and give me a result.

8.Spark is lazy. When I write a filter, it only adds a step to a plan. It waits until an action asks for a result, and then it can look at the whole plan and run it in the cheapest way. This saves work if I never need the data, or if later steps let it skip rows.

9.I use orders.show(5), which prints just five rows. orders.limit(5) also works. Both stop early, so the full table is never pulled into the driver's memory.

10.Locally I call spark.stop(), which frees the resources. In Databricks I shouldn't call it, because the platform manages the session and stopping it can break the notebook. I just finish the notebook or detach the compute.

Hands-on questions (11-20)
1.Read orders.csv and verify its row count against the manifest.

2.Print the order schema and identify columns read as strings.

3.Select order_id, customer_id, and status and display ten rows.

4.Filter orders from S01 and display only their IDs.

5.Count completed and cancelled orders separately without using Python loops.

6.Create a five-row customer DataFrame with an explicit string schema.

7.Rename status to order_status without altering the source DataFrame.

8.Find the distinct channel values and explain why the result is small.

9.Compare show(3), take(3), and collect() on a five-row fixture.

10.Set the session timezone to UTC and verify the configuration value.

    Q11 actual: 300 | manifest: 300
    

    Q12 schema:
    root
     |-- order_id: string (nullable = true)
     |-- customer_id: string (nullable = true)
     |-- store_id: string (nullable = true)
     |-- order_ts: string (nullable = true)
     |-- status: string (nullable = true)
     |-- channel: string (nullable = true)
    
    Q12 string columns: ['order_id', 'customer_id', 'store_id', 'order_ts', 'status', 'channel']
    

    Q13:
    +--------+-----------+---------+
    |order_id|customer_id|status   |
    +--------+-----------+---------+
    |O0001   |C015       |completed|
    |O0002   |C004       |completed|
    |O0003   |C070       |completed|
    |O0004   |C055       |completed|
    |O0005   |C078       |completed|
    |O0006   |C049       |completed|
    |O0007   |C030       |completed|
    |O0008   |C022       |completed|
    |O0009   |C042       |completed|
    |O0010   |C073       |cancelled|
    +--------+-----------+---------+
    only showing top 10 rows
    

    Q14:
    +--------+
    |order_id|
    +--------+
    |O0001   |
    |O0002   |
    |O0006   |
    |O0007   |
    |O0009   |
    |O0012   |
    |O0017   |
    |O0020   |
    |O0024   |
    |O0026   |
    |O0037   |
    |O0040   |
    |O0051   |
    |O0055   |
    |O0057   |
    |O0058   |
    |O0060   |
    |O0061   |
    |O0062   |
    |O0076   |
    +--------+
    only showing top 20 rows
    

    Q15:
    +---------+-----+
    |   status|count|
    +---------+-----+
    |completed|  270|
    |cancelled|   30|
    +---------+-----+
    
    

    Q16:
    root
     |-- customer_id: string (nullable = true)
     |-- name: string (nullable = true)
     |-- city: string (nullable = true)
    
    +-----------+-----+---------+
    |customer_id| name|     city|
    +-----------+-----+---------+
    |         C1| Asha|Bengaluru|
    |         C2| Ravi|   Mumbai|
    |         C3|Meera|    Delhi|
    |         C4|Kiran|     Pune|
    |         C5| Zoya|  Chennai|
    +-----------+-----+---------+
    
    

    Q17 source columns: ['order_id', 'customer_id', 'store_id', 'order_ts', 'status', 'channel']
    Q17 renamed columns: ['order_id', 'customer_id', 'store_id', 'order_ts', 'order_status', 'channel']
    

    Q18 distinct channels: 2
    +-------+
    |channel|
    +-------+
    | online|
    |  store|
    +-------+
    
    

    +-----------+-----+---------+
    |customer_id| name|     city|
    +-----------+-----+---------+
    |         C1| Asha|Bengaluru|
    |         C2| Ravi|   Mumbai|
    |         C3|Meera|    Delhi|
    +-----------+-----+---------+
    only showing top 3 rows
    Q19 show returned: None | take length: 3 | collect length: 5
    

    Q20 timezone: UTC
    

Advance question

21.Predict how many actions run when the same filtered DataFrame is counted twice.

22.Explain why reading 300 rows locally does not demonstrate cluster scalability.

23.Reproduce an unresolved-column error and explain its message.

24.Explain why DataFrame rows have no guaranteed order unless explicitly sorted.

25.Show that withColumn returns a new DataFrame rather than mutating the original.

26.Design a safe inspection strategy for a billion-row orders table.

27.Compare where SparkSession objects and distributed row data live.

28.Identify driver-side Python code and distributed work in your solution.

29.Predict when a missing input path fails: during read construction or an action; verify.

30.Write a reusable session factory and a five-row smoke-check script.

    Q21 counts: 67 67 -> 2 actions ran
    

    Q23 error type: AnalysisException
    Q23 message: [UNRESOLVED_COLUMN.WITH_SUGGESTION] A column, variable, or function parameter with name `no_such_column` cannot be resolved. Did you mean one of the following? [`channel`, `order_id`, `order_ts`, `status`, `customer_id`]. SQLSTATE: 42703;
    'Project ['no_such_column]
    +- Relation [order_id#10786,customer_id#10787,store_id#10788,order_ts#10789,status#10790,channel#10791] csv
    
    
    JVM stacktrace:
    org.apac
    

    Q24 unsorted first 5: ['O0001', 'O0002', 'O0003', 'O0004', 'O0005']
    Q24 sorted first 5:   ['O0001', 'O0002', 'O0003', 'O0004', 'O0005']
    

    Q25 original columns: ['order_id', 'customer_id', 'store_id', 'order_ts', 'status', 'channel']
    Q25 new columns:      ['order_id', 'customer_id', 'store_id', 'order_ts', 'status', 'channel', 'is_s01']
    

    root
     |-- order_id: string (nullable = true)
     |-- customer_id: string (nullable = true)
     |-- store_id: string (nullable = true)
     |-- order_ts: string (nullable = true)
     |-- status: string (nullable = true)
     |-- channel: string (nullable = true)
    
    +--------+-----------+--------+--------------------+---------+-------+
    |order_id|customer_id|store_id|            order_ts|   status|channel|
    +--------+-----------+--------+--------------------+---------+-------+
    |   O0001|       C015|     S01|2026-07-01T09:00:00Z|completed|  store|
    |   O0002|       C004|     S01|2026-07-02T10:00:00Z|completed|  store|
    |   O0003|       C070|     S04|2026-07-03T11:00:00Z|completed| online|
    |   O0004|       C055|     S03|2026-07-04T12:00:00Z|completed|  store|
    |   O0005|       C078|     S03|2026-07-05T13:00:00Z|completed|  store|
    +--------+-----------+--------+--------------------+---------+-------+
    
    +--------+-----------+--------+--------------------+---------+-------+
    |order_id|customer_id|store_id|            order_ts|   status|channel|
    +--------+-----------+--------+--------------------+---------+-------+
    |   O0120|       C046|     S01|2026-07-30T08:00:00Z|cancelled| online|
    +--------+-----------+--------+--------------------+---------+-------+
    
    Q26 rows for one store: 67
    

    Q29 failed during: action (.count) | error type: AnalysisException
    Q29 message: [PATH_NOT_FOUND] Path does not exist: dbfs:/Volumes/pyspark_assignment1/default/retail_course/data/raw/does_not_exist.csv. SQLSTATE: 42K03
    
    JVM stacktrace:
    org.apache.spark.sql.AnalysisException
    	at o
    

Completion checks

1.The raw orders count equals data/manifest.json;
2.explain why collect() is unsafe for large data. 
3.Complete all 30 numbered daily questions, retaining expected-versus-actual evidence for coding exercises and written reasoning for conceptual/design questions.
4.Compare values and business keys, not only row counts.
5.Save the input fixture and expected rows for at least one example.
6.Sort only when presentation or a deterministic comparison needs it.

    rows: 300 | distinct order_id: 300 | null/blank keys: 0 | manifest: 300
    

    completed: 270 | manifest: 270
    

    orders with unknown customer: 0
    orders with unknown store:    0
    

    fixture S01 rows match expected: [('O1', 'C1', 'S01', 'web', 'completed'), ('O2', 'C2', 'S01', 'store', 'cancelled'), ('O6', 'C1', 'S01', 'app', 'completed')]
    saved: ['fixture_orders.csv', 'expected_s01.json']
    

REVIEW QUESTIONS 
1. What is the input and output grain, and which operation can change the row count?

The input grain is one row per order, and order_id is the key. I checked this in Cell 3: 300 rows and 300 distinct order_id values. The output grain depends onselect, withColumnRenamed and withColumn keep it at one row per order, so the count stays 300.
filter can reduce the row count, for example S01 orders only.
distinct reduces it to one row per unique value, which gives the small channel list.
groupBy(...).count() changes the grain completely, to one row per status or per channel.
limit and sample cut the row count to a fixed or random number.

2. Which null, duplicate, time, or retry case could make today's result wrong?

Null: blank CSV cells read as null. A null status would drop out of my completed and cancelled counts without any error. A null channel forms its own group in groupBy, which is why my edge-case example (Ex5) counts it, and why dropping nulls makes the totals disagree.

Duplicate: if the same order_id appeared twice, my counts would be too high. I checked for this in Cell 3, and the result was 0 duplicates. Repeated order_id is expected only in order lines, not in orders.

Time: order_ts arrives as a text string, not a timestamp. Sorting or comparing it as text could give wrong answers, and any later conversion depends on the session timezone, which is why I set it to UTC.

Retry: running the notebook again is safe today because it only reads data. But uploading the files twice or rerunning the generator could create extra copies, like the misplaced data/data/ folder I had. A wrong layout would double-count or break the paths.

3. Which action executes your work, and where could a shuffle or state growth occur?

The actions are show(), count(), take() and collect(). select, filter and withColumn are lazy and run nothing until an action needs a result.

Shuffles happen when rows with the same key have to be brought together across partitions:

groupBy(...).count(), as in my status and channel counts.
distinct(), which needs to compare rows across partitions.
orderBy(), which sorts across all the data.

filter, select and withColumn need no shuffle. I set shuffle partitions to 4 where Databricks allowed it, and it was set to 4. State growth does not apply because this is batch work, and nothing stays in memory between runs. It matters in streaming days, where state grows as Spark remembers events.

STRETCH CHALLENGE

Turn today's logic into a reusable function with explicit inputs and document one scale limitation. For streaming days, include a saved lastProgress record and explain state and checkpoint behavior.

    limit fired as intended: order_id has more than 3 groups; refusing to collect it to the driver
    {'total_rows': 300, 'distinct_order_ids': 300, 'by_group': {'online': 100, 'store': 200}, 'by_status': {'completed': 270, 'cancelled': 30}}
    

    Saved full notebook code to /Workspace/Shared/answer.md
    
