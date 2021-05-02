import datetime
import json
import time
import traceback

import numpy as np
import requests
import requests_oauthlib

# Replace the values below with yours
# BEARER_TOKEN = AAAAAAAAAAAAAAAAAAAAABG%2FOAEAAAAA7VEry%2Fq75Pgh7kIjeoJ7UeNRv%2Bw%3DhhSXwENXhvplemfWeHPwTi5LRyQIMopfW85Xh6EWGm9eGOBzLR
ACCESS_TOKEN = '1377470029000810496-yWBWWkBy8tIVutGwPqrOiItSvjMuYt'
ACCESS_SECRET = 'rGrBEIvOD11s1sCCbuixIUnv4FcC5LysCVEvgOEfTtq36'
CONSUMER_KEY = 'DuOfmIfUTq18t9FYb2KMpAnkN'
CONSUMER_SECRET = 'C2Vq7vyqJXgumNOVuFj8HCDtqijc8Vdgf5kw8mmxrbX6UJBtJL'
my_auth = requests_oauthlib.OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
# sandbox dev
url = 'https://api.twitter.com/1.1/tweets/search/fullarchive/dev.json'
query = 'bitcoin stock'  # TODO: rethink about the keyword
maxResults = 100
# years = np.arange(2016, 2022)
years = np.array([2021])
months = np.arange(1, 13)
days = np.arange(1, 32)

for year in years:
    for month in months:
        for day in days:
            try:
                # check date is valid
                dt = datetime.datetime(year=year, month=month, day=day)
                if dt <= datetime.datetime.utcnow():
                    fromDate = (dt - datetime.timedelta(days=1)).strftime('%Y%m%d%H%M')
                    toDate = dt.strftime('%Y%m%d%H%M')
                    query_data = [('query', query), ('fromDate', fromDate), ('toDate', toDate),
                                  ('maxResults', maxResults)]
                    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
                    print("Downloading Twitter from " + fromDate + " to " + toDate + "...")
                    response = requests.get(query_url, auth=my_auth, stream=True)
                    print(response)
                    tweets = response.json()['results']
                    # save
                    with open("../data/" + fromDate[:8] + ".json", 'w') as f:
                        json.dump(tweets, f, ensure_ascii=False, indent=4)
                    # sleep for 2s
                    time.sleep(2)
            except Exception as e:
                traceback.print_exc()

# for tweet in tweets:
#     if tweet['truncated']:
#         print(tweet['created_at'], repr(tweet['extended_tweet']['full_text']))
#     else:
#         print(tweet['created_at'], repr(tweet['text']))

# # standard
# keyword = 'bitcoin'
# lang = 'en'  # language
# result_type = 'mixed'
# count = 100  # maximum number of tweets returned
# until = '2021-04-25'
#
# url = 'https://api.twitter.com/1.1/tweets/search/fullarchive/dev.json'
# query_data = [('q', keyword), ('lang', lang), ('result_type', result_type), ('count', count), ('until', until)]
# query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
# response = requests.get(query_url, auth=my_auth, stream=True)
# tweets = response.json()['statuses']
#
# for tweet in tweets:
#     print(tweet['created_at'], repr(tweet['text']))
