
import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("PWC_Employee_Analytics")
    .master("local[2]")
    .getOrCreate()
)

print("=" * 60)
print("Q5: PWC Employee & Sales Analytics")
print("=" * 60)

# Raw Data & Date Conversion

emp_data = [
    (1, "Alice", "Sales", 101, "1/1/2020", 90000, 150000, "1/1/2025"),
    (1, "Alice", "Sales", 101, "1/1/2020", 90000, 200000, "2/1/2025"),
    (2, "Bob",   "Sales", 101, "3/15/2021", 85000, 100000, "1/1/2025"),
    (2, "Bob",   "Sales", 101, "3/15/2021", 85000, 120000, "2/1/2025"),
    (3, "Carol", "HR",    102, "7/10/2019", 95000,      0, "1/1/2025"),
    (4, "David", "HR",    102, "6/25/2020", 87000,      0, "2/1/2025"),
    (5, "Evan",  "IT",    103, "5/5/2022",  80000,  60000, "1/1/2025"),
    (5, "Evan",  "IT",    103, "5/5/2022",  80000,  75000, "2/1/2025"),
]
columns = [
    "EmployeeID", "EmployeeName", "Department", "ManagerID",
    "HireDate", "MonthlySalary", "SalesAmount", "Month",
]

emp = spark.createDataFrame(emp_data, columns)

# Convert strings into Date objects
emp = (
    emp
    .withColumn("Month", F.to_date("Month", "M/d/yyyy"))
    .withColumn("HireDate", F.to_date("HireDate", "M/d/yyyy"))
)

# Part 1: Total & Average Monthly Sales Per Person

emp_totals = emp.groupBy("EmployeeID", "EmployeeName", "Department").agg(
    F.sum("SalesAmount").alias("total_sales"),
    F.avg("SalesAmount").alias("avg_monthly_sales"),
)

print("\n--- 1) Total & Average Sales Per Employee ---")
emp_totals.show()

# Rank Employees Within Their Department

dept_window = Window.partitionBy("Department").orderBy(F.col("total_sales").desc())

emp_ranked = emp_totals.withColumn("dept_rank", F.rank().over(dept_window))

print("\n--- 2) Rank Within Department by Sales ---")
emp_ranked.show()

# Running Total of Sales Inside Each Department

running_window = (
    Window.partitionBy("Department")
    .orderBy(F.col("total_sales").desc())
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
)

emp_running = emp_ranked.withColumn(
    "running_dept_sales", F.sum("total_sales").over(running_window)
)

print("\n--- 3) Running Total by Department ---")
emp_running.show()

#  Growth (Lag)

employee_timeline = Window.partitionBy("EmployeeID").orderBy("Month")

emp_mom = (
    emp
    .withColumn("last_month_sales", F.lag("SalesAmount", 1).over(employee_timeline))
    .withColumn("growth", F.col("SalesAmount") - F.col("last_month_sales"))
)

print("\n--- 4) Month-over-Month Comparison ---")
emp_mom.select(
    "EmployeeID", "EmployeeName", "Month",
    "SalesAmount", "last_month_sales", "growth"
).orderBy("EmployeeID", "Month").show()

# Classify Performers in Big Departments (>100k)

dept_summary = (
    emp_totals
    .groupBy("Department")
    .agg(
        F.sum("total_sales").alias("dept_total_sales"),
        F.avg("total_sales").alias("dept_avg_sales"),
    )
    .filter(F.col("dept_total_sales") > 100000)
)

classified = (
    emp_totals
    .join(dept_summary, on="Department", how="inner")
    .withColumn(
        "performance",
        F.when(F.col("total_sales") > F.col("dept_avg_sales"), "Top Performer")
        .otherwise("Below Average")
    )
    .select(
        "Department", "EmployeeID", "EmployeeName",
        "total_sales", "dept_avg_sales", "performance"
    )
)

print("\n--- 5) Performance Classification (Depts > 100k) ---")
classified.show()