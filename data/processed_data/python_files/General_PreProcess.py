import datetime

from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import ArrayType, DoubleType, StringType, IntegerType
from pyspark.sql.functions import when
from pyspark.sql import Window

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import pandas as pd
import sys


def main():
    stockprice_rawdata_path = '../../stock_price_Energy/data/price_COG.csv'
    news_rawdata_path = '../../news_Energy/data/GoogleNews_Energy_large_all.csv'

    spark = SparkSession.builder.master('local[2]').appName('GeneralDataProcess').getOrCreate()

    window_duration = '11 day'
    slide_duration = '1 day'
    num_datapoints = 22

    startdate = datetime.date(2016, 3, 31)
    enddate = datetime.date(2021, 4, 16)

    ##########################################  1. For StockPrice Data ###################################################
    ## read csv
    df = spark.read.csv(stockprice_rawdata_path, header=True)

    # copy date to create a new time check colume
    df = df.withColumn('Date', f.to_timestamp(df['Date'], 'yyyy-MM-dd'))
    df2 = df.withColumn('TrueDate', f.to_timestamp(df['Date'], 'yyyy-MM-dd')) \
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
    full_dict = {'TrueDate': [], 'Type': []}
    cdate = startdate
    while cdate <= enddate:
        full_dict['TrueDate'].extend([cdate, cdate])
        full_dict['Type'].extend(['Open', 'Closed'])
        cdate += datetime.timedelta(days=1)
    df_ref_pd = pd.DataFrame(full_dict)
    df_ref = spark.createDataFrame(df_ref_pd)
    df3 = df_ref.join(df2, on=['TrueDate', 'Type'], how='left_outer')
    df3 = df3.na.fill(value=0, subset=["Price", "Truedate_existent"])
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
    readtime_last = f.last(df3['Truedate_existent'], ignorenulls=True).over(window_ff)

    read_next = f.first(df3['Price'], ignorenulls=True).over(window_bf)
    readtime_next = f.first(df3['Truedate_existent'], ignorenulls=True).over(window_bf)

    # add columns to the dataframe
    df_filled = df3.withColumn('readvalue_ff', read_last) \
        .withColumn('readtime_ff', readtime_last) \
        .withColumn('readvalue_bf', read_next) \
        .withColumn('readtime_bf', readtime_next)

    # Price interpolation between all empty time
    df_filled_temp = df_filled.withColumn('if_open', f.when(f.col('Type') == 'Open', 1).otherwise(0))
    df_filled2 = df_filled_temp.withColumn('Price_interpol',
                                           f.when(f.col('readtime_bf') == f.col('readtime_ff'), f.col('Price')) \
                                           .otherwise((f.col('readvalue_bf') - f.col('readvalue_ff')) / (f.col('readtime_bf').cast("long") - f.col('readtime_ff').cast("long") - 43200) * (f.col('TrueDate').cast("long") - f.col('readtime_ff').cast("long") - 43200 * f.col('if_open')) + f.col('readvalue_ff')))
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
        'Open_Close', f.collect_list('Price_interpol').over(w)) \
        .groupBy('TrueDate').agg(f.max('Open_Close').alias('Open_Close'))

    # Create a time window, and collect to form a larger array
    df6 = df5.orderBy("TrueDate").groupBy(f.window('TrueDate', window_duration, slide_duration)) \
        .agg(f.collect_list('Open_Close')) \
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

    # Kick out rows with less than num_datapoints data points
    df6 = df6.withColumn('array_length', f.size("StockPrice"))
    df6 = df6.filter((df6.array_length == num_datapoints)).select(['window', 'StockPrice'])
    df6 = df6.withColumn('StockPrice', normalize(df6['StockPrice']))
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

    ##########################################  2. For sentiment analysis ###################################################
    df7 = spark.read.csv(news_rawdata_path, header=True, escape='"')
    df7 = df7.withColumn('time', f.to_timestamp(df7['datetime'], 'yyyy-MM-dd HH:mm:ss'))
    df7 = df7.withColumn('hour', f.hour(f.col('time')))
    df7 = df7.withColumn('Day', f.to_date(df7['time'], format='yyyy-MM-dd'))

    @f.udf
    def connect_string(a, b):
        return a + ' ' + b

    df7 = df7.withColumn('AllText', connect_string(df7['title'], df7['desc']))
    df8 = df7.select('Day', 'hour', 'Alltext')
    df8 = df8.withColumn('TrueDate', when(df8.hour < 9, df8['Day'])
                         .when(df8.hour >= 16, f.date_add(df8['Day'], 1))
                         .otherwise(df8['Day']))
    df8 = df8.withColumn('Type', when(df8.hour < 9, 'Open')
                         .when(df8.hour >= 16, 'Open')
                         .otherwise('Close'))

    # calculate sentiment scores for title, description and content
    analyzer = SentimentIntensityAnalyzer()

    @f.udf(returnType=DoubleType())
    def calculate_sentiment_score(text):
        score = analyzer.polarity_scores(text)['compound']
        return score

    df9 = df8.withColumn('score', calculate_sentiment_score(df8['Alltext']))
    df9 = df9.groupBy(['TrueDate', 'Type']).agg(f.avg("score").alias("AverageScore"))

    # Fill the missing row with help of a full dateframe
    full_dict = {'TrueDate': [], 'Type': []}
    cdate = startdate
    while cdate <= enddate:
        full_dict['TrueDate'].extend([cdate, cdate])
        full_dict['Type'].extend(['Open', 'Close'])
        cdate += datetime.timedelta(days=1)
    df_ref_pd = pd.DataFrame(full_dict)
    df_ref = spark.createDataFrame(df_ref_pd)
    df10 = df_ref.join(df9, on=['TrueDate', 'Type'], how='left_outer')
    df10 = df10.na.fill(value=0, subset=["AverageScore"])

    # use the following to combine open and close into an array
    w = Window.partitionBy('TrueDate').orderBy(f.desc('Type'))
    df11 = df10.withColumn(
        'Open_Close', f.collect_list('AverageScore').over(w)
    ) \
        .groupBy('TrueDate').agg(f.max('Open_Close').alias('Open_Close'))

    # Create a time window, and collect to form a larger array
    df12 = df11.orderBy("TrueDate").groupBy(f.window('TrueDate', window_duration, slide_duration)) \
        .agg(f.collect_list('Open_Close')) \
        .withColumnRenamed('collect_list(Open_Close)', 'NewsScore')
    df12 = df12.withColumn('NewsScore', f.flatten(df12['NewsScore'])).sort("window")

    # Kick out rows with less than num_datapoints data points
    df12 = df12.withColumn('array_length', f.size("NewsScore"))
    df12 = df12.filter((df12.array_length == num_datapoints)).select(['window', 'NewsScore'])

    ##########################################  3. Combine df6 and df12 ################################################
    df_final = df6.join(df12, on=['window'], how='left_outer')

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
    df_final.orderBy('window').toPandas().to_csv('processed_data_energy_COG.csv', index=False)

if __name__ == '__main__':
    main()





















