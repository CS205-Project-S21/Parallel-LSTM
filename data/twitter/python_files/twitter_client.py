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
keywords = 'bitcoin,coinbase'  # a string that contains keywords separated by comma without space


def send_tweets_to_spark(http_resp, tcp_connection):
    for line in http_resp.iter_lines():
        try:
            if not '':
                full_tweet = json.loads(line)
                tweet_text = full_tweet['text']
                print("Tweet Text: " + tweet_text)
                print("------------------------------------------")
                tcp_connection.send((tweet_text + '\n').encode())
        except:
            # e = sys.exc_info()[0]
            # print("Error: %s" % e)
            traceback.print_exc()


def get_tweets():
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    query_data = [('language', 'en'), ('track', keywords)]
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    print(query_url, response)
    return response


TCP_IP = "localhost"
TCP_PORT = 9009
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")
conn, _ = s.accept()
print("Connected... Starting getting tweets.")
resp = get_tweets()
send_tweets_to_spark(resp, conn)
