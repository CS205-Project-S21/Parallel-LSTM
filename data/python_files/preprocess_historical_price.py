from pyspark.sql import SparkSession
from pyspark.sql import functions as f
import numpy as np

spark = SparkSession.builder.master('local').appName('NewsSentimentAnalysis').getOrCreate()

# read csv
df = spark.read.csv('alldate_RIOT.csv', header=True)

df = df.withColumn('Date', f.to_timestamp(df['Date'], 'yyyy-MM-dd'))


@f.udf
def combine(opening_price, closing_price):
    return [opening_price, closing_price]

df = df.withColumn('Open_Close', combine(df['Open'], df['Close']))
df = df.withColumn("Open_Close_new", f.split(f.regexp_replace("Open_Close", r"(^\[)|(\]$)", ""), ", ").cast("array<float>"))
# df.show()
# df.printSchema()

# print([row['Open_Close_new'] for row in df.collect()])

window_duration = '10 day'
slide_duration = '1 day'

df = df.groupBy(f.window('Date', window_duration, slide_duration)) \
    .agg(f.collect_list('Open_Close_new')) \
    .withColumnRenamed('collect_list(Open_Close_new)', 'sliding_window')

print([(row['window'],np.array(row['sliding_window']).reshape([-1]).tolist()) for row in df.collect()])

