import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder
    .appName("EmpJoinedBeforeManager")
    .master("local[2]")
    .getOrCreate()
)

print("=" * 60)
print("Employees who joined before their managers")
print("=" * 60)

# employee dataset
emp_data = [
    (1, "Alice", 3, "2020-01-15"),
    (2, "Bob", 3, "2022-06-01"),
    (3, "Charlie", None, "2021-03-10"),
    (4, "David", 2, "2021-11-20"),
    (5, "Eva", 2, "2023-01-05"),
]

columns = ["emp_id", "emp_name", "manager_id", "join_date"]
emp = spark.createDataFrame(emp_data, columns)

# join_date to real Date type
emp = emp.withColumn("join_date", F.to_date("join_date"))

# views
employees = emp.select(
    F.col("emp_id"),
    F.col("emp_name"),
    F.col("manager_id"),
    F.col("join_date").alias("emp_join_date")
)

managers = emp.select(
    F.col("emp_id").alias("mgr_id"),
    F.col("emp_name").alias("mgr_name"),
    F.col("join_date").alias("mgr_join_date")
)

# Join'
(((employees
 .join(managers, employees.manager_id == managers.mgr_id, how="inner"))
 .filter(F.col("emp_join_date") < F.col("mgr_join_date")))
.select(
        "emp_id",
        "emp_name",
        "emp_join_date",
        "mgr_name",
        "mgr_join_date"
    ))
.orderBy("emp_id")
)

result.show(truncate=False)