import datetime

import pytz
from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

category = 'cryptocurrency'
# category = 'test_for_fun'

# create spark configuration
conf = SparkConf()
conf.setAppName("TwitterStreamApp")
# create spark instance with the above configuration
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
# creat the Streaming Context from the above spark context with window size n seconds
ssc = StreamingContext(sc, 30)
# # setting a checkpoint to allow RDD recovery
# ssc.checkpoint("checkpoint_TwitterApp")
# read data from port 9009
dataStream = ssc.socketTextStream("localhost", 9009)

# calculate sentiment scores for title, description and content
analyzer = SentimentIntensityAnalyzer()

scores = dataStream.map(lambda text: (analyzer.polarity_scores(text)['compound'], 1))
avg_score = scores.reduce(lambda x, y: (x[0] + y[0], x[1] + y[1])).map(lambda z: z[0] / z[1])


def save(rdd):
    with open("../data/streaming/twitter_sentiment_scores_" + category + ".txt", 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now(tz=pytz.timezone('US/Eastern')).strftime('%Y%m%d%H%M%S') + '\t' + str(
            rdd.collect()[0]) + "\n")
    return


avg_score.foreachRDD(save)

# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()
