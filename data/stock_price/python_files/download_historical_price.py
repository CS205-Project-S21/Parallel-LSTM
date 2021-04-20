#!/usr/bin/env python
# coding: utf-8

import yfinance as yf  # api yfinance to get historical price and big firm recommendation
import pandas as pd
import datetime
import numpy as np

output_name = "../data/profile_test.csv"
ticker = "RIOT"

def get_dataset(name_string):
    df_list = list()
    for ticker in name_string:
        data = yf.download(ticker, group_by="Ticker", period='10y')
        data['ticker'] = ticker  # add this column becasue the dataframe doesn't contain a column with the ticker
        # data.to_csv(f'ticker_{ticker}.csv')  # ticker_AAPL.csv for example
        df_list.append(data)
    #         print(df_list)
    #     return df_list

    # combine all dataframes into a single dataframe
    df = pd.concat(df_list)
    # save to csv
    # df.to_csv('ticker.csv')
    return df

def generate_full_date(sdate, edate):
    dates = []
    while sdate <= edate:
        dates.append(datetime.datetime.strftime(sdate,'%Y-%m-%d'))
        sdate += datetime.timedelta(days=1)
    return dates

@profile
def main():
    sdate = datetime.date(2016, 3, 31)
    edate = datetime.date(2021, 4, 16)
    dates = generate_full_date(sdate, edate)
    count = np.array(dates).shape[0]
    tickerStrings = ['RIOT']
    df = get_dataset(tickerStrings)
    date_index = df.index.strftime('%Y-%m-%d').tolist()
    df_all_date = {'Date': ['']*count, 'Open': ['']*count, 'Close': ['']*count, 'Ticker': ['']*count}
    
    for i, date in enumerate(dates):
        df_all_date['Date'][i] = date
        df_all_date['Ticker'][i] = df['ticker'][0]
        if date in date_index:
            df_all_date['Open'][i] = df['Open'][date]
            df_all_date['Close'][i] = df['Close'][date]
        else:
            df_all_date['Open'][i] = 0
            df_all_date['Close'][i] = 0
    
    for i, date in enumerate(dates):
        if df_all_date['Open'][i] == 0:
            k = 0
            while df_all_date['Open'][i + k] == 0:
                k += 1
            s = df_all_date['Close'][i - 1]
            t = df_all_date['Open'][i + k] - s
            for j in range(k):
                df_all_date['Open'][i + j] = s + t/(2*k+1)*(2*j+1)
                df_all_date['Close'][i + j] = s + t/(2*k+1)*(2*j+2)
    
    df_all_date = pd.DataFrame(df_all_date)
    df_all_date.to_csv("alldate_RIOT.csv", index=False)

if __name__ == '__main__':
    main()
