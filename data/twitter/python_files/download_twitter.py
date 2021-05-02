import socket
import requests
import requests_oauthlib
import json
import traceback

# Replace the values below with yours
# BEARER_TOKEN = AAAAAAAAAAAAAAAAAAAAABG%2FOAEAAAAA7VEry%2Fq75Pgh7kIjeoJ7UeNRv%2Bw%3DhhSXwENXhvplemfWeHPwTi5LRyQIMopfW85Xh6EWGm9eGOBzLR
ACCESS_TOKEN = '1377470029000810496-yWBWWkBy8tIVutGwPqrOiItSvjMuYt'
ACCESS_SECRET = 'rGrBEIvOD11s1sCCbuixIUnv4FcC5LysCVEvgOEfTtq36'
CONSUMER_KEY = 'DuOfmIfUTq18t9FYb2KMpAnkN'
CONSUMER_SECRET = 'C2Vq7vyqJXgumNOVuFj8HCDtqijc8Vdgf5kw8mmxrbX6UJBtJL'
my_auth = requests_oauthlib.OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

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

# sandbox dev
query = 'bitcoin stock'  # TODO: rethink about the keyword
fromDate = '202101300830'
toDate = '202101300930'
maxResults = 100

url = 'https://api.twitter.com/1.1/tweets/search/fullarchive/dev.json'
query_data = [('query', query), ('fromDate', fromDate), ('toDate', toDate), ('maxResults', maxResults)]
query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
response = requests.get(query_url, auth=my_auth, stream=True)
print(response)
tweets = response.json()['results']

# save
with open("../data/" + toDate + ".json", 'w') as f:
    json.dump(tweets, f, ensure_ascii=False, indent=4)

# for tweet in tweets:
#     if tweet['truncated']:
#         print(tweet['created_at'], repr(tweet['extended_tweet']['full_text']))
#     else:
#         print(tweet['created_at'], repr(tweet['text']))
