#!/usr/bin/env python
# coding: utf-8


import yfinance as yf  # api yfinance to get historical price and big firm recommendation
import pandas as pd
import numpy as np

output_name = "../data/price_RIOT.csv"
tickerStrings = ['RIOT']

def get_dataset(name_string):
    df_list = list()
    for ticker in name_string:
        data = yf.download(ticker, group_by="Ticker", period='10y')
        data['ticker'] = ticker  # add this column becasue the dataframe doesn't contain a column with the ticker     
        df_list.append(data) 
    # combine all dataframes into a single dataframe
    df = pd.concat(df_list)
    return df


def main():
    df = get_dataset(tickerStrings)
    date_index = df.index.strftime('%Y-%m-%d').tolist()
    df = df[['Open', 'Close', 'ticker']]
    df_date = pd.DataFrame(date_index, columns=['Date'])
    df_date['key1'] = 1
    df_ticker = df[['ticker']]
    df_ticker['key1'] = 1
    df_type = pd.DataFrame([['Open'], ['Closed']], columns=['Type'])
    df_type['key2'] = 1
    df_merge = df_date.merge(df_type, left_on='key1', right_on='key2')
    df_merge = df_merge.drop(columns=['key1', 'key2'])
    df_merge2 = df_ticker.merge(df_type, left_on='key1', right_on='key2')
    df_merge2 = df_merge2.drop(columns=['key1', 'key2', 'Type'])
    df_price = pd.DataFrame(df.drop(columns=['ticker']).values.reshape(2 * df.drop(columns=['ticker']).values.shape[0], 1), columns=['Price'])

    df_final = pd.concat([df_merge, df_merge2, df_price], axis=1)
    df_final.to_csv(output_name, index=False)


if __name__ == '__main__':
    main()

