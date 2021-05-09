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


##########################################  1. For StockPrice Data ###################################################

def preprocess_price(price_name, price_path, spark, startdate, enddate):
    window_duration = '11 day'
    slide_duration = '1 day'
    num_datapoints = 22

    # read csv
    df = spark.read.csv(price_path, header=True)
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
                                           .otherwise((f.col('readvalue_bf') - f.col('readvalue_ff')) / (
                                                       f.col('readtime_bf').cast("long") - f.col('readtime_ff').cast(
                                                   "long") - 43200) * (f.col('TrueDate').cast("long") - f.col(
                                               'readtime_ff').cast("long") - 43200 * f.col('if_open')) + f.col(
                                               'readvalue_ff')))
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
        x_min = np.min(x)
        x_max = np.max(x)
        x_normalized = ((x - x_min) / (x_max - x_min)).tolist()
        # append the min and max price in the time window for de-normalization
        x_normalized.extend([float(x_min), float(x_max)])
        return x_normalized

    # kick out rows with less than num_datapoints data points
    df6 = df6.withColumn('array_length', f.size("StockPrice"))
    df6 = df6.filter((df6.array_length == num_datapoints)).select(['window', 'StockPrice'])
    df6 = df6.withColumn('StockPrice', normalize(df6['StockPrice']))
    df_price = df6.withColumnRenamed('StockPrice', 'StockPrice_{}'.format(price_name))
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
    return df_price


##########################################  2. For sentiment analysis ###################################################
def preprocess_news(news_path, spark, startdate, enddate):
    window_duration = '11 day'
    slide_duration = '1 day'
    num_datapoints = 22

    df = spark.read.csv(news_path, header=True, escape='"')
    df = df.withColumn('time', f.to_timestamp(df['datetime'], 'yyyy-MM-dd HH:mm:ss'))
    df = df.withColumn('hour', f.hour(f.col('time')))
    df = df.withColumn('Day', f.to_date(df['time'], format='yyyy-MM-dd'))

    @f.udf
    def connect_string(a, b):
        if a == None:
            return  b
        if b == None:
            return a
        return a + ' ' + b

    df = df.withColumn('AllText', connect_string(df['title'], df['desc']))
    df1 = df.select('Day', 'hour', 'Alltext')
    df1 = df1.withColumn('TrueDate', when(df1.hour < 9, df1['Day'])
                         .when(df1.hour >= 16, f.date_add(df1['Day'], 1))
                         .otherwise(df1['Day']))
    df1 = df1.withColumn('Type', when(df1.hour < 9, 'Open')
                         .when(df1.hour >= 16, 'Open')
                         .otherwise('Close'))

    # calculate sentiment scores for title, description and content
    analyzer = SentimentIntensityAnalyzer()

    @f.udf(returnType=DoubleType())
    def calculate_sentiment_score(text):
        score = analyzer.polarity_scores(text)['compound']
        return score

    df2 = df1.withColumn('score', calculate_sentiment_score(df1['Alltext']))
    df2 = df2.groupBy(['TrueDate', 'Type']).agg(f.avg("score").alias("AverageScore"))

    # Fill the missing row with help of a full dateframe
    full_dict = {'TrueDate': [], 'Type': []}
    cdate = startdate
    while cdate <= enddate:
        full_dict['TrueDate'].extend([cdate, cdate])
        full_dict['Type'].extend(['Open', 'Close'])
        cdate += datetime.timedelta(days=1)
    df_ref_pd = pd.DataFrame(full_dict)
    df_ref = spark.createDataFrame(df_ref_pd)
    df3 = df_ref.join(df2, on=['TrueDate', 'Type'], how='left_outer')
    df3 = df3.na.fill(value=0, subset=["AverageScore"])

    # use the following to combine open and close into an array
    w = Window.partitionBy('TrueDate').orderBy(f.desc('Type'))
    df4 = df3.withColumn(
        'Open_Close', f.collect_list('AverageScore').over(w)
    ) \
        .groupBy('TrueDate').agg(f.max('Open_Close').alias('Open_Close'))

    # Create a time window, and collect to form a larger array
    df5 = df4.orderBy("TrueDate").groupBy(f.window('TrueDate', window_duration, slide_duration)) \
        .agg(f.collect_list('Open_Close')) \
        .withColumnRenamed('collect_list(Open_Close)', 'NewsScore')
    df5 = df5.withColumn('NewsScore', f.flatten(df5['NewsScore'])).sort("window")

    # Kick out rows with less than num_datapoints data points
    df5 = df5.withColumn('array_length', f.size("NewsScore"))
    df5 = df5.filter((df5.array_length == num_datapoints)).select(['window', 'NewsScore'])
    return df5


##########################################  4. Combine all price and sentiment analysis ###################################################
def main():
    # stockprice_rawdata_path_BTC = '../../stock_price/data/cryptocurrency/price_BTC.csv'
    # stockprice_rawdata_path_MARA = '../../stock_price/data/cryptocurrency/price_MARA.csv'
    # stockprice_rawdata_path_RIOT = '../../stock_price/data/cryptocurrency/price_RIOT.csv'
    # stockprice_rawdata_path_IXIC = '../../stock_price/data/cryptocurrency/price_IXIC.csv'
    # news_rawdata_path = '../../news/data/cryptocurrency/GoogleNews_Bitcoin_large_all.csv'
    # spark = SparkSession.builder.master('local[2]').appName('GeneralDataProcess').getOrCreate()
    #
    # sdate = datetime.date(2016, 3, 31)
    # edate = datetime.date(2021, 4, 16)
    #
    # df_BTC = preprocess_price('BTC', stockprice_rawdata_path_BTC, spark, sdate, edate)
    # df_MARA = preprocess_price('MARA', stockprice_rawdata_path_MARA, spark, sdate, edate)
    # df_RIOT = preprocess_price('RIOT', stockprice_rawdata_path_RIOT, spark, sdate, edate)
    # df_IXIC = preprocess_price('IXIC', stockprice_rawdata_path_IXIC, spark, sdate, edate)
    # df_news = preprocess_news(news_rawdata_path, spark, sdate, edate)
    #
    # df1 = df_MARA.join(df_RIOT, on=['window'], how='left_outer')
    # df2 = df_BTC.join(df1, on=['window'], how='left_outer')
    # df3 = df_IXIC.join(df2, on=['window'], how='left_outer')
    # df_final = df_news.join(df3, on=['window'], how='left_outer')
    #
    # df_final.orderBy('window').toPandas().to_csv('../data/processed_data_cryptocurrency.csv', index=False)

    stockprice_rawdata_path_COG = '../../stock_price/data/energy/price_COG.csv'
    stockprice_rawdata_path_DVN = '../../stock_price/data/energy/price_DVN.csv'
    stockprice_rawdata_path_HFC = '../../stock_price/data/energy/price_HFC.csv'
    news_rawdata_path = '../../news/data/energy/GoogleNews_Energy_large_all.csv'
    spark = SparkSession.builder.master('local[2]').appName('GeneralDataProcess').getOrCreate()

    sdate = datetime.date(2016, 3, 31)
    edate = datetime.date(2021, 4, 16)

    df_COG = preprocess_price('COG', stockprice_rawdata_path_COG, spark, sdate, edate)
    df_DVN = preprocess_price('DVN', stockprice_rawdata_path_DVN, spark, sdate, edate)
    df_HFC = preprocess_price('HFC', stockprice_rawdata_path_HFC, spark, sdate, edate)
    df_news = preprocess_news(news_rawdata_path, spark, sdate, edate)

    df1 = df_DVN.join(df_HFC, on=['window'], how='left_outer')
    df2 = df_COG.join(df1, on=['window'], how='left_outer')
    df_final = df_news.join(df2, on=['window'], how='left_outer')

    df_final.orderBy('window').toPandas().to_csv('../data/processed_data_energy.csv', index=False)


if __name__ == '__main__':
    main()
