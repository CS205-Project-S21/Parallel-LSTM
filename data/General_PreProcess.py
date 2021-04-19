import datetime

from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import ArrayType, DoubleType, StringType, IntegerType
from pyspark.sql.functions import when
from pyspark.sql import Window

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import pandas as pd


stockprice_rawdata_path = './stock_price/data/alldate_RIOT.csv'
news_rawdata_path = './news/data/news_large.csv'

spark = SparkSession.builder.master('local').appName('GeneralDataProcess').getOrCreate()

window_duration = '11 day'
slide_duration = '1 day'
num_datapoints = 22

startdate = datetime.date(2016,3,31)
enddate = datetime.date(2021,4,16)

##########################################  1. For StockPrice Data ###################################################
## read csv
df = spark.read.csv(stockprice_rawdata_path, header=True)
df = df.withColumn('Date', f.to_timestamp(df['Date'], 'yyyy-MM-dd'))

@f.udf
def combine(opening_price, closing_price):
    return [opening_price, closing_price]

df = df.withColumn('Open_Close', combine(df['Open'], df['Close']))
df = df.withColumn("Open_Close_new", f.split(f.regexp_replace("Open_Close", r"(^\[)|(\]$)", ""), ", ").cast("array<double>"))



df = df.orderBy('Date').groupBy(f.window('Date', window_duration, slide_duration)) \
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


##########################################  2. For sentiment analysis ###################################################
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
# df5 = df4.orderBy("TrueDate", f.desc("Type")) # We should avoid any unnecessary sort or orderBy in pipeline
# df4 look like:
# +----------+-----+-------------------+
# |  TrueDate| Type|       AverageScore|
# +----------+-----+-------------------+
# |2021-03-31| Open| 0.6719461538461545|
# |2021-04-03| Open| 0.2891708333333335|
# |2016-07-05| Open|             0.9879|
# |2021-03-29|Close| 0.3657036496350363|
# |2021-04-06| Open|  0.646568817204301|
# |2016-10-05| Open|             0.9509|
# |2016-05-27| Open|              0.999|
# |2021-04-14|Close|-0.3307480769230771|
# We need to find a way to fill in the missing rows with 0

# Fill the missing row with help of a full dateframe
full_dict = {'TrueDate':[], 'Type':[]}
cdate = startdate
while cdate <= enddate:
    full_dict['TrueDate'].extend([cdate, cdate])
    full_dict['Type'].extend(['Open', 'Close'])
    cdate += datetime.timedelta(days=1)
df_ref_pd = pd.DataFrame(full_dict)
df_ref = spark.createDataFrame(df_ref_pd)
df5 = df_ref.join(df4, on=['TrueDate', 'Type'], how='left_outer')
df5 = df5.na.fill(value=0,subset=["AverageScore"])
# df5 looks like:
# +----------+-----+------------+
# |  TrueDate| Type|AverageScore|
# +----------+-----+------------+
# |2016-03-31| Open|         0.0|
# |2016-03-31|Close|         0.0|
# |2016-04-01| Open|         0.0|
# |2016-04-01|Close|         0.0|
# |2016-04-02| Open|     -0.1307|
# |2016-04-02|Close|         0.0|
# |2016-04-03| Open|         0.0|
# |2016-04-03|Close|         0.0|
# |2016-04-04| Open|      0.9878|
# |2016-04-04|Close|         0.0|
# |2016-04-05| Open|     -0.1027|

# use the following to combine open and close into an array
w = Window.partitionBy('TrueDate').orderBy(f.desc('Type'))
df6 = df5.withColumn(
            'Open_Close', f.collect_list('AverageScore').over(w)
        )\
        .groupBy('TrueDate').agg(f.max('Open_Close').alias('Open_Close'))

# Create a time window, and collect to form a larger array
df7 = df6.orderBy("TrueDate").groupBy(f.window('TrueDate', window_duration, slide_duration)) \
    .agg(f.collect_list('Open_Close')) \
    .withColumnRenamed('collect_list(Open_Close)', 'NewsScore')
df7 = df7.withColumn('NewsScore', f.flatten(df7['NewsScore'])).sort("window")

# Kick out rows with less than num_datapoints data points 
df7 = df7.withColumn('array_length', f.size("NewsScore")).filter((df7.array_length == 22))
# df7.sort(window) looks like:
# +--------------------+--------------------+
# |              window|           NewsScore|
# +--------------------+--------------------+
# |{2016-03-30 20:00...|[0.0, 0.0, 0.0, 0...|
# |{2016-03-31 20:00...|[0.0, 0.0, -0.130...|
# |{2016-04-01 20:00...|[-0.1307, 0.0, 0....|
# |{2016-04-02 20:00...|[0.0, 0.0, 0.9878...|
# |{2016-04-03 20:00...|[0.9878, 0.0, -0....|
# |{2016-04-04 20:00...|[-0.1027, 0.0, 0....|
# |{2016-04-05 20:00...|[0.0, 0.0, 0.1104...|
# |{2016-04-06 20:00...|[0.1104, 0.0, 0.0...|


##########################################  3. Combine df1 and df7 ################################################
df_final = df1.join(df7, on=['window'], how='left_outer')

# df_final.orderBy('window') looks like:
# +--------------------+--------------------+--------------------+
# |              window|          StockPrice|           NewsScore|
# +--------------------+--------------------+--------------------+
# |{2016-03-30 20:00...|[0.0, 0.500000152...|[0.0, 0.0, 0.0, 0...|
# |{2016-03-31 20:00...|[0.0, 0.061224916...|[0.0, 0.0, -0.130...|
# |{2016-04-01 20:00...|[0.0, 0.0, 0.0, 0...|[-0.1307, 0.0, 0....|
# |{2016-04-02 20:00...|[0.0, 0.0, 0.0, 0...|[0.0, 0.0, 0.9878...|
# |{2016-04-03 20:00...|[0.0, 0.0, 0.5434...|[0.9878, 0.0, -0....|
# |{2016-04-04 20:00...|[0.0, 0.499999574...|[-0.1027, 0.0, 0....|
# |{2016-04-05 20:00...|[0.63157815484152...|[0.0, 0.0, 0.1104...|
# |{2016-04-06 20:00...|[0.05263151290346...|[0.1104, 0.0, 0.0...|
# |{2016-04-07 20:00...|[0.21052605161384...|[0.0, 0.0, 0.0, 0...|























