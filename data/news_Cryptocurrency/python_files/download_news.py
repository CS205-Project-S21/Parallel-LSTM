import re

import pandas as pd
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='8da77fe9e98040aca8510d665750cb70')

all_articles = newsapi.get_everything(qintitle='bitcoin',
                                      from_param='2021-04-15T00:00:00', to='2021-04-15T23:59:59',
                                      language='en', sort_by='relevancy', page=1, page_size=100)

n_articles = min([all_articles['totalResults'], 100])

news = {'source': ['']*n_articles, 'author': ['']*n_articles, 'time': ['']*n_articles, 'title': ['']*n_articles,
        'description': ['']*n_articles, 'content': ['']*n_articles, 'url': ['']*n_articles}

for i, article in enumerate(all_articles['articles']):
    news['source'][i] = article['source']['name']
    news['author'][i] = article['author']
    news['time'][i] = article['publishedAt']
    news['title'][i] = article['title']
    news['description'][i] = re.sub(r'(\r|\n|<.*?>|…)+', ' ', article['description']).strip()
    news['content'][i] = re.sub(r'(\r|\n|<.*?>|… \[\+[0-9]+ chars])+', ' ', article['content']).strip()
    news['url'][i] = article['url']

df_news = pd.DataFrame(news)
df_news.to_csv("../data/news_small.csv", index=False)
