import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = SparkSession.builder \
    .appName("TeamPairs") \
    .master("local[2]") \
    .getOrCreate()

teams = ["RCB", "CSK", "MI", "PBKS"]

indexed_teams = list(enumerate(teams))

df = spark.createDataFrame(indexed_teams, ["id", "team"])

team_a = df.select(F.col("id").alias("id_a"), F.col("team").alias("team_1"))
team_b = df.select(F.col("id").alias("id_b"), F.col("team").alias("team_2"))

matches = team_a.join(team_b, F.col("id_a") < F.col("id_b")) \
                .select("team_1", "team_2") \
                .orderBy("id_a", "id_b")

matches.show()

