import datetime
import json
import time
import traceback
import os

import numpy as np
import requests
import requests_oauthlib

"""
Download tweets from 2021/1/16 to 2021/4/16 and store in json format.
"""

# Replace the values below with yours
ACCESS_TOKEN = ''
ACCESS_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
my_auth = requests_oauthlib.OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
url = 'https://api.twitter.com/1.1/tweets/search/fullarchive/dev.json'
query = 'bitcoin price'
maxResults = 100
years = np.array([2021])
months = np.array([1, 2, 3, 4])
days = np.arange(1, 32)
hours = np.array([9, 16])
dir_prefix = "../data/historical/cryptocurrency/raw"

for year in years:
    for month in months:
        for day in days:
            for hour in hours:
                try:
                    # check the date is valid
                    dt = datetime.datetime(year=year, month=month, day=day, hour=hour)
                    # check the date is within the time interval of interest
                    if datetime.datetime(year=2021, month=1, day=16) < dt < datetime.datetime(year=2021, month=4, day=17):
                        if hour == 9:  # 16 - 9
                            fromDate = (dt - datetime.timedelta(hours=17)).strftime('%Y%m%d%H%M')
                        else:  # 9 - 16
                            fromDate = (dt - datetime.timedelta(hours=7)).strftime('%Y%m%d%H%M')
                        toDate = dt.strftime('%Y%m%d%H%M')
                        # check whether file exists to prevent duplicate requests
                        if not os.path.isfile("../data/historical/" + fromDate + "_" + toDate + ".json"):
                            query_data = [('query', query), ('fromDate', fromDate), ('toDate', toDate),
                                          ('maxResults', maxResults)]
                            query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
                            print("Downloading Twitter from " + fromDate + " to " + toDate + "...")
                            response = requests.get(query_url, auth=my_auth)
                            print(response)
                            tweets = response.json()['results']
                            # save
                            with open(dir_prefix + "/" + fromDate + "_" + toDate + ".json", 'w') as f:
                                # set ensure_ascii to False to allow unicode characters!!!
                                json.dump(tweets, f, ensure_ascii=False, indent=4)
                            # sleep for 2s
                            time.sleep(2)
                except Exception as e:
                    traceback.print_exc()
