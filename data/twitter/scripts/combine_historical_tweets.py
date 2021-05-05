import datetime
import json
import re
import traceback

import numpy as np
import pandas as pd
import pytz

"""
Combine historical tweets in json format into a single DataFrame
"""

years = np.array([2021])
months = np.array([1, 2, 3, 4])
days = np.arange(1, 32)
hours = np.array([9, 16])
dir_prefix = "../data/historical/cryptocurrency/raw"

historical_tweets = {'created_at': [], 'text': []}

for year in years:
    for month in months:
        for day in days:
            for hour in hours:
                try:
                    # check the date is valid
                    dt = datetime.datetime(year=year, month=month, day=day, hour=hour)
                    # check the date is within the time interval of interest
                    if datetime.datetime(year=2021, month=1, day=16) < dt < datetime.datetime(year=2021, month=4,
                                                                                              day=17):
                        if hour == 9:  # 16 - 9
                            fromDate = (dt - datetime.timedelta(hours=17)).strftime('%Y%m%d%H%M')
                        else:  # 9 - 16
                            fromDate = (dt - datetime.timedelta(hours=7)).strftime('%Y%m%d%H%M')
                        toDate = dt.strftime('%Y%m%d%H%M')

                        # load json
                        with open(dir_prefix + "/" + fromDate + "_" + toDate + ".json", 'r') as f:
                            tweets = json.load(f)

                            for tweet in tweets:
                                if tweet['truncated']:
                                    text = re.sub(r'(\n)+', ' ', tweet['extended_tweet']['full_text'])
                                else:
                                    text = re.sub(r'(\n)+', ' ', tweet['text'])
                                created_at = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
                                # convert to US/Eastern time
                                created_at = created_at.replace(tzinfo=pytz.utc).astimezone(
                                    pytz.timezone('US/Eastern')).replace(tzinfo=None)
                                historical_tweets['created_at'].append(created_at)
                                historical_tweets['text'].append(text)
                except Exception as e:
                    traceback.print_exc()

df_historical_tweets = pd.DataFrame(historical_tweets)
df_historical_tweets.to_csv("../data/historical/cryptocurrency/bitcoin_tweets.csv", index=False)
