'''
The following function will download news from Contextual Web Search API

Minhuan Li, May 2021
'''


import requests
import json
import re
import datetime

def fetch_context_web(keywords, startdate, enddate, page=1, duplicate=True):
    # Contextual Web Search API, 100 Request per day, 50 articles every time
    RAPID_API_KEY = '67f58679fcmsh1d5d86c70be0778p1320e2jsn414d9154fae0'
    date_formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']
    results = []
    fail_flag = 0
    
    url1 = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI"
    querystring1 = {"q":keywords,"pageNumber":"{}".format(page),"pageSize":"50","autoCorrect":"true","fromPublishedDate":startdate,
                   "toPublishedDate":enddate}
    headers1 = {
        'x-rapidapi-key': RAPID_API_KEY,
        'x-rapidapi-host': "contextualwebsearch-websearch-v1.p.rapidapi.com"
        }
    response1 = requests.request("GET", url1, headers=headers1, params=querystring1)
    try: 
        body1 = json.loads(response1.text)
        articles1 = body1["value"]
        n_articles = len(articles1)
        if n_articles < 50:
            fail_flag = 1

        for i, article in enumerate(articles1):
            tmp_title = article['title']
            tmp_source = article['provider']['name']
            for date_format in date_formats:
                try:
                    tmp_datetime = datetime.datetime.strptime(article['datePublished'], date_format).date()
                    tmp_date = tmp_datetime.strftime("%b %d, %Y")
                    break
                except:
                    continue
            tmp_desc = re.sub(r'(\r|\n|<.*?>|…)+', ' ', article['description'] + ' ' + re.sub(r'(\r|\n|<.*?>|… \[\+[0-9]+ chars])+', ' ', article['body']).strip()).strip()
            tmp_link = article['url']
            if duplicate:
                AM_time = datetime.datetime(tmp_datetime.year, tmp_datetime.month,tmp_datetime.day,4,0)
                PM_time = datetime.datetime(tmp_datetime.year, tmp_datetime.month,tmp_datetime.day,12,0)
                results.append({'title': tmp_title, 'source': tmp_source,'date': tmp_date, 'datetime':AM_time,'desc': tmp_desc, 'link': tmp_link})
                results.append({'title': tmp_title, 'source': tmp_source,'date': tmp_date, 'datetime':PM_time,'desc': tmp_desc, 'link': tmp_link})
            else:
                results.append({'title': tmp_title, 'source': tmp_source,'date': tmp_date, 'datetime':tmp_datetime,'desc': tmp_desc, 'link': tmp_link})
    except Exception as e:
        print(e)
        fail_flag = 1
    return results, fail_flag