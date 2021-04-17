This is a note after playing with 10 news API recommended from https://rapidapi.com/blog/rapidapi-featured-news-apis/

**What we want:** Simplicity and user-friendly (with Python client), Support key-word search (for stock-related news), Provide news date (for integration with time series stock price data), Free (at least for several hundred requests per day), Great if provide full text/short excerpt (for accurate sentiment analysis).

**Conclusion:**

#### 1. Bing News Search
See `BingNewsAPI.ipynb`. One fatal defect is, this API does not support search by explicit date range, only freshness. Otherwise, it has good info structure with a short description text. 

Free plan: 1000/month

#### 2. Contextual Web Search
See `ContextualWebSearchAPI.ipynb`. This API provides everything we want: search by keyword and date range, accurate publish date, url and provider, even good excerpt and full body text.  Latency ~ 1700ms

Free plan: 100/day

#### 3. Newslit

Free plan: 25/month; Not acceptable...

#### 4. Newscatcher
See `NewsCather.ipynb`  

Super low latency (In fact I personally can't feel the difference...) ~ 358ms. It has specific search for publicly traded company (search by ticker); Can specify the source during search;  

Results are good, with clear date and good summary words.

Free plan: 21 request/hour; One request return at most 5 articles back

#### 5. Google News API: 
See `GoogleNewsPackage.ipynb`. There is a free python package at https://github.com/Iceloof/GoogleNews, but the output is problematic (for example, the search date doesn't make sense).

Free plan: 3 request/hour on Rapid API. 


#### 6. Hacker News API:

This is not for general search usage. Only support search by item id and user (specific for a database?)

#### 7. NewsAPI:

Not on Rapid API anymore. But the company itself provide a user-friendly API. But the search results(including the description and content texts) are not very satisfying.

Free plan: 100 requests per day


