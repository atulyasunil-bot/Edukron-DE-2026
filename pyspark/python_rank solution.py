import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("RankingDemo") \
    .master("local[2]") \
    .getOrCreate()

print("=" * 60)
print("Q2: row_number() vs rank() vs dense_rank()")
print("=" * 60)

scores = [(99,), (99,), (98,), (98,), (98,), (98,), (97,), (96,), (96,), (95,)]
df = spark.createDataFrame(scores, ["marks"])

ranking_rule = Window.orderBy(F.col("marks").desc())

result = df.select(
    F.col("marks"),
    F.row_number().over(ranking_rule).alias("row_num"),
    F.rank().over(ranking_rule).alias("rank"),
    F.dense_rank().over(ranking_rule).alias("dense_rank")
)

result.show()