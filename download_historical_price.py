#!/usr/bin/env python
# coding: utf-8

import yfinance as yf  # api yfinance to get historical price and big firm recommendation
import pandas as pd


def get_dataset(name_string):
    df_list = list()
    for ticker in name_string:
        data = yf.download(ticker, group_by="Ticker", period='20d')
        data['ticker'] = ticker  # add this column becasue the dataframe doesn't contain a column with the ticker
        data.to_csv(f'ticker_{ticker}.csv')  # ticker_AAPL.csv for example
        
        df_list.append(data)
    # combine all dataframes into a single dataframe
    df = pd.concat(df_list)
    # save to csv
    df.to_csv('ticker.csv')
    return df

tickerStrings = ['BTC-USD','^IXIC','RIOT']
df_riot = get_dataset(tickerStrings)
