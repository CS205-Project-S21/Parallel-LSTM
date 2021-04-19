from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import ArrayType, DoubleType, StringType, IntegerType
from pyspark.sql.functions import when
from pyspark.sql import Window

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np


stockprice_rawdata_path = './stock_price/data/alldate_RIOT.csv'
news_rawdata_path = './news/data/news_large.csv'

spark = SparkSession.builder.master('local').appName('GeneralDataProcess').getOrCreate()

window_duration = '11 day'
slide_duration = '1 day'

# 1. For StockPrice Date
## read csv
df = spark.read.csv(stockprice_rawdata_path, header=True)
df = df.withColumn('Date', f.to_timestamp(df['Date'], 'yyyy-MM-dd'))

@f.udf
def combine(opening_price, closing_price):
    return [opening_price, closing_price]

df = df.withColumn('Open_Close', combine(df['Open'], df['Close']))
df = df.withColumn("Open_Close_new", f.split(f.regexp_replace("Open_Close", r"(^\[)|(\]$)", ""), ", ").cast("array<double>"))



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
df1 = df.withColumn('array_length', f.size("sliding_window"))
df1 = df1.filter((df1.array_length == 22)).select('window', 'sliding_window').withColumnRenamed("sliding_window", "StockPrice")
# df1 looks like:
# +--------------------+--------------------+
# |              window|          StockPrice|
# +--------------------+--------------------+
# |{2016-03-30 20:00...|[0.0, 0.500000152...|
# |{2016-03-31 20:00...|[0.0, 0.061224916...|
# |{2016-04-01 20:00...|[0.0, 0.0, 0.0, 0...|
# |{2016-04-02 20:00...|[0.0, 0.0, 0.0, 0...|
# |{2016-04-03 20:00...|[0.0, 0.0, 0.5434...|
# |{2016-04-04 20:00...|[0.0, 0.499999574...|


# 2. For sentiment analysis
df2 = spark.read.csv(news_rawdata_path, header=True, escape='"')
df2 = df2.withColumn('time', f.to_timestamp(df2['time'], 'yyyy-MM-dd HH:mm:ss'))
df2 = df2.withColumn('hour', f.hour(f.col('time')))
df2 = df2.withColumn('Day', f.to_date(df2['time'], format='yyyy-MM-dd'))

@f.udf
def connect_string(a, b):
    return a+' '+b

df2 = df2.withColumn('AllText', connect_string(connect_string(df2['title'], df2['description']), df2['content']))
df3 = df2.select('Day', 'hour', 'Alltext')
df3 = df3.withColumn('TrueDate', when(df3.hour < 9, df3['Day'])
                                .when(df3.hour >= 16 , f.date_add(df3['Day'], 1))
                                .otherwise(df3['Day']))
df3 = df3.withColumn('Type', when(df3.hour < 9, 'Open')
                                .when(df3.hour >= 16 , 'Open')
                                .otherwise('Close'))

# calculate sentiment scores for title, description and content
analyzer = SentimentIntensityAnalyzer()

@f.udf(returnType=DoubleType())
def calculate_sentiment_score(text):
    score = analyzer.polarity_scores(text)['compound']
    return score

df4 = df3.withColumn('score', calculate_sentiment_score(df3['Alltext']))
df4 = df4.groupBy(['TrueDate', 'Type']).agg(f.avg("score").alias("AverageScore"))
df5 = df4.orderBy("TrueDate", f.desc("Type"))
# df5 look like:
# +----------+-----+------------+
# |  TrueDate| Type|AverageScore|
# +----------+-----+------------+
# |2016-04-02| Open|     -0.1307|
# |2016-04-04| Open|      0.9878|
# |2016-04-05| Open|     -0.1027|
# |2016-04-07| Open|      0.1104|
# |2016-04-12|Close|       -0.07|
# |2016-04-14| Open|      0.2306|
# |2016-04-16| Open|     -0.7894|
# |2016-04-18|Close|      0.7964|
# |2016-04-23| Open|      0.9896|
# We need to find a way to fill in the missing rows with 0

# TODO: Snippets to fill the missing row


# Once we have the complete dateframe, use the following to combine open and close into an array
# Then we are able to use the same coding pattern in 
w = Window.partitionBy('TrueDate').orderBy(f.desc('Type'))

df6 = df5.withColumn(
            'Open_Close', f.collect_list('AverageScore').over(w)
        )\
        .groupBy('TrueDate').agg(f.max('Open_Close').alias('Open_Close'))

# df6 looks like:
# +----------+--------------------+
# |  TrueDate|          Open_Close|
# +----------+--------------------+
# |2016-04-25|           [-0.5994]|
# |2016-05-03|            [0.9928]|
# |2016-07-26|            [0.9501]|
# |2021-03-22|[-0.0702244444444...|
# |2016-10-07|[0.04814999999999...|
# |2016-05-23|            [0.9926]|
# |2016-10-23|            [0.9958]|
# |2016-05-27|             [0.999]|
# |2021-04-07|[0.57279610389610...|
# |2021-04-15|[0.39659814814814...|

df7 = df6.groupBy(f.window('TrueDate', window_duration, slide_duration)) \
    .agg(f.collect_list('Open_Close')) \
    .withColumnRenamed('collect_list(Open_Close)', 'NewsScore')

# flatten
df7 = df7.withColumn('NewsScore', f.flatten(df7['NewsScore'])).sort("window")

# df7 looks like:
# +--------------------+--------------------+
# |              window|           NewsScore|
# +--------------------+--------------------+
# |{2016-03-22 20:00...|           [-0.1307]|
# |{2016-03-23 20:00...|           [-0.1307]|
# |{2016-03-24 20:00...|   [0.9878, -0.1307]|
# |{2016-03-25 20:00...|[0.9878, -0.1307,...|
# |{2016-03-26 20:00...|[0.9878, -0.1307,...|
# |{2016-03-27 20:00...|[0.9878, -0.1307,...|
# |{2016-03-28 20:00...|[0.9878, -0.1307,...|
# |{2016-03-29 20:00...|[0.9878, -0.1307,...|
# |{2016-03-30 20:00...|[0.9878, -0.1307,...|
# |{2016-03-31 20:00...|[0.9878, -0.1307,...|
# |{2016-04-01 20:00...|[0.9878, -0.1307,...|

# TODO: Combine df1 and df7



