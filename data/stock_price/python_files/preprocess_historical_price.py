#!/usr/bin/env python
# coding: utf-8

import yfinance as yf  # api yfinance to get historical price and big firm recommendation
import pandas as pd
import datetime
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import ArrayType, DoubleType, StringType, IntegerType
from pyspark.sql import Window
import sys

spark = SparkSession.builder.master('local').appName('Price_analysis').getOrCreate()

window_duration = '11 day'
slide_duration = '1 day'
num_datapoints = 22

startdate = datetime.date(2016,3,31)
enddate = datetime.date(2021,4,16)

# read csv
df = spark.read.csv('../data/price_RIOT.csv', header=True)

# copy date to create a new time check colume
df = df.withColumn('Date', f.to_timestamp(df['Date'], 'yyyy-MM-dd'))
df2 = df.withColumn('TrueDate', f.to_timestamp(df['Date'], 'yyyy-MM-dd'))\
    .withColumn('TrueDate_existent', f.to_timestamp(df['Date'], 'yyyy-MM-dd'))
df2 = df2.select('TrueDate', 'Type', 'Price', 'Truedate_existent')

# df2 looks like:
# +-------------------+------+------------------+-------------------+
# |           TrueDate|  Type|             Price|  Truedate_existent|
# +-------------------+------+------------------+-------------------+
# |2016-03-31 00:00:00|  Open| 2.309999942779541|2016-03-31 00:00:00|
# |2016-03-31 00:00:00|Closed| 2.700000047683716|2016-03-31 00:00:00|
# |2016-04-01 00:00:00|  Open|2.5999999046325684|2016-04-01 00:00:00|
# |2016-04-01 00:00:00|Closed| 2.630000114440918|2016-04-01 00:00:00|
# |2016-04-04 00:00:00|  Open| 2.630000114440918|2016-04-04 00:00:00|
# |2016-04-04 00:00:00|Closed| 2.630000114440918|2016-04-04 00:00:00|

# Fill the missing row with help of a full dateframe
full_dict = {'TrueDate':[], 'Type':[]}
cdate = startdate
while cdate <= enddate:
    full_dict['TrueDate'].extend([cdate, cdate])
    full_dict['Type'].extend(['Open', 'Closed'])
    cdate += datetime.timedelta(days=1)
df_ref_pd = pd.DataFrame(full_dict)
df_ref = spark.createDataFrame(df_ref_pd)
df3 = df_ref.join(df2, on=['TrueDate', 'Type'], how='left_outer')
df3 = df3.na.fill(value=0,subset=["Price", "Truedate_existent"])
df3 = df3.withColumn('TrueDate', f.to_timestamp(df3['TrueDate'], 'yyyy-MM-dd'))

# df3 looks like:
# +-------------------+------+------------------+-------------------+
# |           TrueDate|  Type|             Price|  Truedate_existent|
# +-------------------+------+------------------+-------------------+
# |2016-03-31 00:00:00|  Open| 2.309999942779541|2016-03-31 00:00:00|
# |2016-03-31 00:00:00|Closed| 2.700000047683716|2016-03-31 00:00:00|
# |2016-04-01 00:00:00|  Open|2.5999999046325684|2016-04-01 00:00:00|
# |2016-04-01 00:00:00|Closed| 2.630000114440918|2016-04-01 00:00:00|
# |2016-04-02 00:00:00|  Open|              null|               null|
# |2016-04-02 00:00:00|Closed|              null|               null|

# Forward-filling and Backward-filling Using Window Functions
window_ff = Window.orderBy('TrueDate').rowsBetween(-sys.maxsize, 0)
window_bf = Window.orderBy('TrueDate').rowsBetween(0, sys.maxsize)

# create series containing the filled values
read_last = f.last(df3['Price'], ignorenulls=True).over(window_ff)
readtime_last = f.last(df3['Truedate_existent'],ignorenulls=True).over(window_ff)

read_next = f.first(df3['Price'], ignorenulls=True).over(window_bf)
readtime_next = f.first(df3['Truedate_existent'], ignorenulls=True).over(window_bf)

# add columns to the dataframe
df_filled = df3.withColumn('readvalue_ff', read_last)\
    .withColumn('readtime_ff', readtime_last)\
    .withColumn('readvalue_bf', read_next)\
    .withColumn('readtime_bf', readtime_next)

# Price interpolation between all empty time
df_filled_temp = df_filled.withColumn('if_open', f.when(f.col('Type') == 'Open', 1).otherwise(0))
df_filled2 = df_filled_temp.withColumn('Price_interpol', f.when(f.col('readtime_bf') == f.col('readtime_ff'), f.col('Price'))\
                                       .otherwise((f.col('readvalue_bf') - f.col('readvalue_ff'))\
                                                  / (f.col('readtime_bf').cast("long") - f.col('readtime_ff').cast("long") - 43200)\
                                                   * (f.col('TrueDate').cast("long") - f.col('readtime_ff').cast("long") - 43200 * f.col('if_open')) + f.col('readvalue_ff')))
df4 = df_filled2.select('TrueDate', 'Type', 'Price_interpol')

# df4 looks like:
# +-------------------+------+------------------+
# |           TrueDate|  Type|    Price_interpol|
# +-------------------+------+------------------+
# |2016-03-31 00:00:00|  Open| 2.309999942779541|
# |2016-03-31 00:00:00|Closed| 2.700000047683716|
# |2016-04-01 00:00:00|  Open|2.5999999046325684|
# |2016-04-01 00:00:00|Closed| 2.630000114440918|
# |2016-04-02 00:00:00|  Open| 2.630000114440918|
# |2016-04-02 00:00:00|Closed| 2.630000114440918|


# use the following to combine open and close into an array
w = Window.partitionBy('TrueDate').orderBy(f.desc('Type'))
df5 = df4.withColumn(
    'Open_Close', f.collect_list('Price_interpol').over(w))\
    .groupBy('TrueDate').agg(f.max('Open_Close').alias('Open_Close'))

# Create a time window, and collect to form a larger array
df6 = df5.orderBy("TrueDate").groupBy(f.window('TrueDate', window_duration, slide_duration))\
    .agg(f.collect_list('Open_Close'))\
    .withColumnRenamed('collect_list(Open_Close)', 'StockPrice')
df6 = df6.withColumn('StockPrice', f.flatten(df6['StockPrice']).cast("array<double>")).sort("window")

@f.udf(ArrayType(DoubleType()))
def normalize(x):
    """
    Normalize the input to the range between 0 and 1
    """
    x = np.array(x)
    x_normalized = ((x - np.min(x)) / (np.max(x) - np.min(x))).tolist()
    return x_normalized

df6 = df6.withColumn('StockPrice', normalize(df6['StockPrice']))

# Kick out rows with less than num_datapoints data points
df6 = df6.withColumn('array_length', f.size("StockPrice"))
df6 = df6.filter((df6.array_length == num_datapoints)).select(['window', 'StockPrice'])

# df6 looks like:
# +--------------------+--------------------+
# |              window|          StockPrice|
# +--------------------+--------------------+
# |{2016-03-30 20:00...|[0.0, 0.500000152...|
# |{2016-03-31 20:00...|[0.0, 0.061224916...|
# |{2016-04-01 20:00...|[0.0, 0.0, 0.0, 0...|
# |{2016-04-02 20:00...|[0.0, 0.0, 0.0, 0...|
# |{2016-04-03 20:00...|[0.0, 0.0, 0.5434...|
# |{2016-04-04 20:00...|[0.0, 0.499999574...|
