from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType, IntegerType
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

spark = SparkSession.builder.master('local').appName('NewsSentimentAnalysis').getOrCreate()

# read csv
df = spark.read.csv('../data/news_small.csv', header=True)

# extract hour from time
df = df.withColumn('hour', df['time'].substr(12, 2))  # start position and length


# map to time slots
@udf(returnType=IntegerType())
def get_time_slot(hour):
    hour = int(hour)
    if hour < 9:
        return 1
    elif 9 <= hour < 10:
        return 2
    elif 10 <= hour < 11:
        return 3
    elif 11 <= hour < 12:
        return 4
    elif 12 <= hour < 13:
        return 5
    elif 13 <= hour < 14:
        return 6
    elif 14 <= hour < 15:
        return 7
    elif 15 <= hour < 16:
        return 8
    else:
        return 0


df = df.withColumn('time_slot', get_time_slot(df['hour']))


# calculate sentiment scores for title, description and content
analyzer = SentimentIntensityAnalyzer()


@udf(returnType=DoubleType())
def calculate_sentiment_score(text):
    score = analyzer.polarity_scores(text)['compound']
    return score


df = df.withColumn('title_score', calculate_sentiment_score(df['title']))
df = df.withColumn('content_score', calculate_sentiment_score(df['content']))
df = df.withColumn('score', (df['title_score'] + df['content_score']) / 2)

# group by time slot
df_by_time_slot = df.groupBy('time_slot').avg('score')

print([(row['time_slot'], row['avg(score)']) for row in sorted(df_by_time_slot.collect())])
