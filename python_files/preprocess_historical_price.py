from pyspark.sql import SparkSession
from pyspark.sql import functions as f

spark = SparkSession.builder.master('local').appName('NewsSentimentAnalysis').getOrCreate()

# read csv
df = spark.read.csv('ticker_RIOT.csv', header=True)

df = df.withColumn('Date', f.to_timestamp(df['Date'], 'yyyy-MM-dd'))


@f.udf
def combine(opening_price, closing_price):
    return [opening_price, closing_price]


df = df.withColumn('Open_Close', combine(df['Open'], df['Close']))
# print(df.show())

window_duration = '10 day'
slide_duration = '1 day'

df = df.groupBy(f.window('Date', window_duration, slide_duration)) \
    .agg(f.collect_list('Open')) \
    .withColumnRenamed('collect_list(Open)', 'sliding_window')

print(df.show())
