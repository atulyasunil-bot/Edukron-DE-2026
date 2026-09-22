
import os
import sys


os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("AmexConsecutiveElements")
    .master("local[2]")
    .getOrCreate()
)

print("=" * 60)
print(" Elements appearing 3+ times consecutively")
print("=" * 60)

#  Input raw sequence
elements_data = [
    ("A",), ("B",), ("B",), ("A",), ("A",), ("A",), ("B",),
    ("C",), ("D",), ("C",), ("C",), ("C",), ("C",)
]

# Using enumerate to kep it intact
indexed_data = list(enumerate(elements_data))
df = spark.createDataFrame([(idx, val[0]) for idx, val in indexed_data], ["row_id", "element"])

# row order
timeline = Window.orderBy("row_id")

#  behind (lag) and ahead (lead)
neighbors_df = (
    df
    .withColumn("prev_elem", F.lag("element", 1).over(timeline))
    .withColumn("next_elem", F.lead("element", 1).over(timeline))
)

# Step 4: If element == prev_elem AND element == next_elem, it's in a run of >= 3
result = (
    neighbors_df
    .filter((F.col("element") == F.col("prev_elem")) & (F.col("element") == F.col("next_elem")))
    .select(F.col("element").alias("appeared_three_times"))
    .distinct()
    .orderBy("appeared_three_times")
)

result.show()