import re

from pyspark import SparkConf, SparkContext
from pyspark.sql import functions as f
from pyspark.sql.types import DoubleType
from pyspark.streaming import StreamingContext
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# create spark configuration
conf = SparkConf()
conf.setAppName("TwitterStreamApp")
# create spark instance with the above configuration
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
# creat the Streaming Context from the above spark context with window size n seconds
ssc = StreamingContext(sc, 20)
# setting a checkpoint to allow RDD recovery
ssc.checkpoint("checkpoint_TwitterApp")
# read data from port 9009
dataStream = ssc.socketTextStream("localhost", 9009)

# calculate sentiment scores for title, description and content
analyzer = SentimentIntensityAnalyzer()


def preprocess_text(text):
    return text


@f.udf(returnType=DoubleType())
def calculate_sentiment_score(text):
    score = analyzer.polarity_scores(text)['compound']
    return score


text = dataStream.map(calculate_sentiment_score)
text.pprint(100)

# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()
