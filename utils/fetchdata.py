'''
This is a wrap-up script for users to download raw news and raw price datas.

Minhuan Li, minhuanli@g.harvard.edu, May 7 2021
'''

__all__ = ['get_news', 'get_stock_price']

import datetime
import math
import time

import pandas as pd
import yfinance as yf
import numpy as np
from fetchgooglenews import GoogleNews
from fetchcontextweb import fetch_context_web



def generate_periods(startdate, enddate, length=30, shift=-1):
    '''
    Generate time windows from startdate to enddate with fixed day length, for piecewise news downloading
    
    Parameters
    ----------
    startdate: datetime.date
        Left date point for the windows (included)

    enddate: datetime.date
        Right date point for the windows (included)
    
    length: int, default 30
        Size of each time window in days

    shift: 0 or -1, default -1
        Include the right date point or not. For GoolgeNews, set shift=-1; For fetch_context_web, set shift=0
    
    Returns
    -------
    A list of time window tuples

    Examples
    --------
    >>> startdate = datetime.date(2010,1,1)
    >>> enddate = datetime.date(2010,2,5)
    >>> timeperiods = generate_periods(startdate, enddate, length=30, shift=-1)
    >>> print(timeperiods)
    [('01/01/2010', '01/30/2010'), ('01/31/2010', '02/05/2010')]

    >>> timeperiods = generate_periods(startdate, enddate, length=10, shift=0)
    >>> print(timeperiods)
    [('01/01/2010', '01/11/2010'), ('01/11/2010', '01/21/2010'), ('01/21/2010', '01/31/2010'), ('01/31/2010', '02/05/2010')]
    '''
    totaldays = (enddate - startdate).days + 1
    num_periods = math.ceil(totaldays/length)
    output_dates = []
    for i in range(0, num_periods):
        if i < num_periods-1:
            leftdate = startdate + datetime.timedelta(days=i*length)
            rightdate = startdate + datetime.timedelta(days=((i+1)*length+shift))
        else:
            leftdate = startdate + datetime.timedelta(days=i*length)
            rightdate = enddate
        leftdate_str = datetime.date.strftime(leftdate, "%m/%d/%Y")
        rightdate_str = datetime.date.strftime(rightdate, "%m/%d/%Y")
        output_dates.append((leftdate_str, rightdate_str))
    return output_dates

def get_Googlenews(keywords, time_periods, outname=None, MAX_PAGE=5, duplicate=True, pause=1):
    '''
    Download news by scrapping google search news section with specified keywords and time windows
    This is good for getting historical news (older than 2 months), as latest news in Google search have ambiguous dates info.
    Warning: Too frequent scrapping will cause google to block your IP
    Here I set it to be the optimal strategy I discovered: fetch for 10 time periods then sleep for about 30 minutes, if you have multiple time windows
    
    Parameters
    ----------
    keywords: str
        The words you want to search
    
    time_periods: List of tuples
        List of time windows you want to search, usually the output of generate_periods, with shift=-1
    
    outname: None or str, default None
        The file path you want to save the downloaded news data in progress (good for long time downloading). If None, no file will be written.
    
    MAX_PAGE: int, default 5
        Maximum page number when fetching google news search results. I set the scrapping tool to get 50 articles per page. 
        It will automatically stop when reaches the last page of google results no matter how large is your MAX_PAGE.
    
    duplicate: False or True, default True
        This is a specific parameter for our stock price app. We need news for open and close time at each day, but the articles from google
        news only have date without hour time. So we decide to duplicate the articles and set 1 at 4am (for open) and another at 12pm (for close).
    
    pause: int or float, default 1
        Time to sleep between each scrap request in seconds. To aviod being blocked by google.
    
    Returns
    -------
    A Pandas dataframe of all fetched news, with column ['title', 'source', 'date', 'datetime', 'desc', 'link']

    Examples
    --------
    >>> startdate = datetime.date(2010,1,1)
    >>> enddate = datetime.date(2016,3,30)
    >>> timeperiods = generate_periods(startdate, enddate, length=30, shift=-1)
    >>> Energy_news = get_Googlenews("energy",timeperiods, outname=None, MAX_PAGE=5, duplicate=True)
    '''
    results_all = []
    count = 0
    for T, ranges in enumerate(time_periods):
        leftdate, rightdate = ranges
        # Duplicate will copy same article twice, and set one at 4am one at 12pm
        googlenews = GoogleNews(lang='en', start=leftdate,end=rightdate, numperpage=50, duplicate=duplicate)
        googlenews.search(keywords)
        for i in range(2,MAX_PAGE+1):
            time.sleep(1)
            googlenews.get_page(i)
            if googlenews.failflag() == 1:
                break
        results_all.extend(googlenews.results())
        print("Finish Request from {} to {}, Get {} articles".format(leftdate, rightdate, len(googlenews.results())))
        time.sleep(10)
        count += 1
        if count % 10 == 0:
            if outname:
                pd.DataFrame(results_all).to_csv(outname, index=False)
                print("Reach 10 requests capacity, will sleep for 2000s. Up to date batch has been saved in {}".format(outname))
            else:
                print("Reach 10 requests capacity, will sleep for 2000s.")
            if T<len(time_periods)-1: time.sleep(2000)
    return pd.DataFrame(results_all)

def get_cw_news(keywords, time_periods, MAX_PAGE=5):
    '''
    Download news by context web search API with specified keywords and time windows
    With accurate timestamp
    Warning: Maximum 100 requests per day.
    Note: I am a little concerned about this function, as I don't want to attach my Rapid API secret for arbitary users to use. Maybe deprecate this function later.
    Parameters
    ----------
    keywords: str
        The words you want to search
    
    time_periods: List of tuples
        List of time windows you want to search, usually the output of generate_periods, with shift=0
    
    MAX_PAGE: int, default 5
        Maximum page number when fetching google news search results. I set the scrapping tool to get 50 articles per page. 
        It will automatically stop when reaches the last page of google results no matter how large is your MAX_PAGE.
    
    Returns
    -------
    A Pandas dataframe of all fetched news, with column ['title', 'source', 'date', 'datetime', 'desc', 'link']

    Examples
    --------
    >>> startdate = datetime.date(2021,1,1)
    >>> enddate = datetime.date(2021,3,30)
    >>> timeperiods = generate_periods(startdate, enddate, length=30, shift=0)
    >>> Energy_news = get_cw_news("energy",timeperiods, MAX_PAGE=5)
    '''
    results_all = []
    for leftdate, rightdate in time_periods:
        results_period = []
        for i in range(1,MAX_PAGE+1):
            tmp_results, fail_flag = fetch_context_web(keywords, leftdate, rightdate, page=i)
            results_period.extend(tmp_results)
            if fail_flag == 1:
                break
        results_all.extend(results_period)
        print("Finish Request from {} to {}, Get {} articles".format(leftdate, rightdate, len(results_period)))
    return pd.DataFrame(results_all)

def get_news(keywords, startdate, enddate, length=10, mode="ContextWeb"):
    '''
    Get News from Google News Search or Context Web Seatch, from startdate to enddate (closed set)

    Parameters
    ----------
    keywords: str
        The words you want to search
    startdate: str, "YYYY-MM-DD"
        Start date of the interest range, in format "YYYY-MM-DD"
    enddate: str, "YYYY-MM-DD"
        End date of the interest range, in format "YYYY-MM-DD"
    length: int,
        Window size to split the time from startdate to enddate
    mode: str, "ContextWeb" or "Google"
        Use ContextWeb API or Google News Search as News Source
        ContextWeb has smaller latency, maximum 100 requests per day; Google News has larger latency

    Returns
    -------
    A Pandas dataframe of all fetched news, with column ['title', 'source', 'date', 'datetime', 'desc', 'link']

    Examples
    --------
    >>> df = get_stock_price("RIOT", "2016-03-31", "2016-04-16")
    '''
    startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")
    enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d")
    if mode == "ContextWeb":
        timeperiods = generate_periods(startdate, enddate+datetime.timedelta(days=1), length=length, shift=0)
        df = get_cw_news(keywords, timeperiods, MAX_PAGE=5)
    elif mode == "Google":
        timeperiods = generate_periods(startdate, enddate, length=length, shift=-1)
        df = get_Googlenews(keywords, timeperiods, outname=None, MAX_PAGE=5, duplicate=True, pause=1)
    else:
        raise ValueError("Mode Only Supports 'ContextWeb' or 'Google'.")
    
    df = df[df.datetime < enddate+datetime.timedelta(days=1)].copy()
    df.drop_duplicates(inplace=True)

    return df


def get_stock_price(ticker, startdate, enddate):
    '''
    Get Historical Stock Price by Ticker from yfinance API, from startdate to enddate (closed set), with Open and Close Each Day

    Parameters
    ----------
    ticker: str
        The ticker name of the stock
    startdate: str, "YYYY-MM-DD"
        Start date of the interest range, in format "YYYY-MM-DD"
    enddate: str, "YYYY-MM-DD"
        End date of the interest range, in format "YYYY-MM-DD"
    
    Returns
    -------
    A Pandas Dateframe

    Examples
    --------
    >>> df = get_stock_price("RIOT", "2016-03-31", "2016-04-16")
    >>> df.show()
    #   Date	Type	ticker	Price
    # 2016-03-31	Open	RIOT	2.310000
    # 2016-03-31	Closed	RIOT	2.700000
    # 2016-04-01	Open	RIOT	2.600000
    # 2016-04-01	Closed	RIOT	2.630000
    # 2016-04-04	Open	RIOT	2.630000
    '''
    enddate = (datetime.datetime.strptime(enddate, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    df = yf.download(ticker, group_by="Ticker", start=startdate, end=enddate)
    df['ticker'] = ticker  # add this column becasue the dataframe doesn't contain a column with the ticker
    date_index = df.index.strftime('%Y-%m-%d').tolist()
    df = df[['Open', 'Close', 'ticker']].copy()
    df_date = pd.DataFrame(date_index, columns=['Date'])
    df_date['key1'] = 1
    df_ticker = df[['ticker']].copy()
    df_ticker['key1'] = 1
    df_type = pd.DataFrame([['Open'], ['Closed']], columns=['Type'])
    df_type['key2'] = 1
    df_merge = df_date.merge(df_type, left_on='key1', right_on='key2')
    df_merge = df_merge.drop(columns=['key1', 'key2'])
    df_merge2 = df_ticker.merge(df_type, left_on='key1', right_on='key2')
    df_merge2 = df_merge2.drop(columns=['key1', 'key2', 'Type'])
    df_price = pd.DataFrame(df.drop(columns=['ticker']).values.reshape(2 * df.drop(columns=['ticker']).values.shape[0], 1), columns=['Price'])
    df_final = pd.concat([df_merge, df_merge2, df_price], axis=1)
    return df_final
