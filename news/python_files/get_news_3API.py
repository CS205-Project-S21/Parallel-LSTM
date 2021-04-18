import datetime
import re
import requests
import json
import warnings

import pandas as pd

RAPID_API_KEY = '67f58679fcmsh1d5d86c70be0778p1320e2jsn414d9154fae0'
NEWS_API_KEY = '7b294a567b694de5b23397387713d7f6' 

keyword = "Bitcoin"
ticker = "TSLA" 
startdate = "2021-04-15T00:00:00"
enddate = "2021-04-15T23:59:59"
date_formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']
output_file_name= "../data/news_small.csv"

# Data Structure for final output
news = {'source': [], 'author': [], 'time': [], 'title': [],
        'description': [], 'content': [], 'url': []}

# 1. Contextual Web Search API, 100 Request per day, 100 articles every time
url1 = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI"
querystring1 = {"q":keyword,"pageNumber":"1","pageSize":"50","autoCorrect":"true","fromPublishedDate":startdate,
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

    for i, article in enumerate(articles1):
        news['source'].append(article['provider']['name'])
        news['author'].append("NotProvided")
        for date_format in date_formats:
            try:
                news['time'].append(datetime.datetime.strptime(article['datePublished'], date_format))
                break
            except:
                continue
        news['title'].append(article['title'])
        news['description'].append(re.sub(r'(\r|\n|<.*?>|…)+', ' ', article['description']).strip())
        news['content'].append(re.sub(r'(\r|\n|<.*?>|… \[\+[0-9]+ chars])+', ' ', article['body']).strip())
        news['url'].append(article['url'])
except:
    warnings.warn("Fail to get news from Contextual Web Search API!")


# 2. Newscatche API, 25 Request per hour, only five articles every time
url21 = "https://newscatcher.p.rapidapi.com/v1/stocks"
querystring21 = {"ticker":ticker,"from":startdate,"to":enddate,"lang":"en","stock":"NASDAQ","media":"True","sort_by":"relevancy"}

headers21 = {
    'x-rapidapi-key': RAPID_API_KEY,
    'x-rapidapi-host': "newscatcher.p.rapidapi.com"
    }

response21 = requests.request("GET", url21, headers=headers21, params=querystring21)

try: 
    body21 = json.loads(response21.text)
    articles21 = body21["articles"]
    n_articles21 = len(articles21)

    for i, article in enumerate(articles21):
        news['source'].append("NotProvided")
        news['author'].append(re.sub(r'(\r|\n|<.*?>|…)+', ' ', str(article['author'])).strip())
        for date_format in date_formats:
            try:
                news['time'].append(datetime.datetime.strptime(article['published_date'], date_format))
                break
            except:
                continue
        news['title'].append(article['title'])
        news['description'].append(re.sub(r'(\r|\n|<.*?>|…)+', ' ', article['summary']).strip())
        news['content'].append("NotProvided")
        news['url'].append(article['link'])
except Exception as e:
    print(e)
    warnings.warn("Fail to get news from Newscatcher API Stock Search!")


url22 = "https://newscatcher.p.rapidapi.com/v1/search"
querystring22 = {"q":keyword,"from":startdate,"to":enddate,"lang":"en","media":"True","sort_by":"relevancy"}

headers22 = {
    'x-rapidapi-key': RAPID_API_KEY,
    'x-rapidapi-host': "newscatcher.p.rapidapi.com"
    }

response22 = requests.request("GET", url22, headers=headers22, params=querystring22)

try: 
    body22 = json.loads(response22.text)
    articles22 = body22["articles"]
    n_articles22 = len(articles22)

    for i, article in enumerate(articles22):
        news['source'].append("NotProvided")
        news['author'].append(re.sub(r'(\r|\n|<.*?>|…)+', ' ', str(article['author'])).strip())
        for date_format in date_formats:
            try:
                news['time'].append(datetime.datetime.strptime(article['published_date'], date_format))
                break
            except:
                continue
        news['title'].append(article['title'])
        news['description'].append(re.sub(r'(\r|\n|<.*?>|…)+', ' ', article['summary']).strip())
        news['content'].append("NotProvided")
        news['url'].append(article['link'])
except Exception as e:
    print(e)
    warnings.warn("Fail to get news from Newscatcher API Keyword Search!")


# 3. NewsAPI search, 100 requests per day
url3 = ('https://newsapi.org/v2/everything?'
       'q='+keyword+'&'
       'from='+startdate+'&'
       'to='+enddate+'&'
       'sortBy=relevancy&'
       'pageSize=100&'
       'apiKey='+NEWS_API_KEY)

try: 
    articles3 = requests.get(url3).json()['articles']

    for i, article in enumerate(articles3):
        news['source'].append(article['source']['name'])
        news['author'].append(re.sub(r'(\r|\n|<.*?>|…)+', ' ', str(article['author'])).strip())
        for date_format in date_formats:
            try:
                news['time'].append(datetime.datetime.strptime(article['publishedAt'], date_format))
                break
            except:
                continue
        news['title'].append(article['title'])
        news['description'].append(re.sub(r'(\r|\n|<.*?>|…)+', ' ', article['description']).strip())
        news['content'].append(re.sub(r'(\r|\n|<.*?>|… \[\+[0-9]+ chars])+', ' ', article['content']).strip())
        news['url'].append(article['url'])
except:
    warnings.warn("Fail to get news from NewsAPI Search!")

df_news = pd.DataFrame(news)
df_news.to_csv(output_file_name, index=False)
