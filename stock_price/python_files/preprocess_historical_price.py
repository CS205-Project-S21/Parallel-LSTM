from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import ArrayType, DoubleType
import numpy as np

spark = SparkSession.builder.master('local').appName('NewsSentimentAnalysis').getOrCreate()

# read csv
df = spark.read.csv('../data/alldate_RIOT.csv', header=True)

df = df.withColumn('Date', f.to_timestamp(df['Date'], 'yyyy-MM-dd'))


@f.udf
def combine(opening_price, closing_price):
    return [opening_price, closing_price]


df = df.withColumn('Open_Close', combine(df['Open'], df['Close']))
df = df.withColumn("Open_Close_new", f.split(f.regexp_replace("Open_Close", r"(^\[)|(\]$)", ""), ", ").cast("array<double>"))
# df.show()
# df.printSchema()

# print([row['Open_Close_new'] for row in df.collect()])

window_duration = '11 day'
slide_duration = '1 day'

df = df.groupBy(f.window('Date', window_duration, slide_duration)) \
    .agg(f.collect_list('Open_Close_new')) \
    .withColumnRenamed('collect_list(Open_Close_new)', 'sliding_window')

# flatten
df = df.withColumn('sliding_window', f.flatten(df['sliding_window']))


@f.udf(ArrayType(DoubleType()))
def normalize(x):
    """
    Normalize the input to the range between 0 and 1
    """
    x = np.array(x)
    x_normalized = ((x - np.min(x)) / (np.max(x) - np.min(x))).tolist()
    return x_normalized


df = df.withColumn('sliding_window', normalize(df['sliding_window']))

print([(row['window'], np.array(row['sliding_window']).tolist()) for row in df.collect()])
