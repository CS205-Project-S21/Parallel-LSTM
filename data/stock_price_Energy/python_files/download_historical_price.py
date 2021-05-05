'''
The Energy stocks: https://www.investopedia.com/top-energy-stocks-4582081
We choose the following 3 famous Energy stocks:
- Devon Energy Corp. (DVN)
- Cabot Oil & Gas Corp. ( COG)
- HollyFrontier Corp. (HFC)
'''


import yfinance as yf  # api yfinance to get historical price and big firm recommendation
import pandas as pd
import numpy as np


output_name = "../data/price_HFC.csv"
tickerStrings = ['HFC']

def get_dataset(name_string):
    df_list = list()
    for ticker in name_string:
        data = yf.download(ticker, group_by="Ticker", start="2016-03-31", end="2021-04-16")
        data['ticker'] = ticker  # add this column becasue the dataframe doesn't contain a column with the ticker
        df_list.append(data)
    # combine all dataframes into a single dataframe
    df = pd.concat(df_list)
    # save to csv
#     df.to_csv('ticker.csv')
    return df


def main():
    tickerStrings = ['RIOT']
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

    # df_final looks like:
    #   Date	Type	ticker	Price
    # 2016-03-31	Open	RIOT	2.310000
    # 2016-03-31	Closed	RIOT	2.700000
    # 2016-04-01	Open	RIOT	2.600000
    # 2016-04-01	Closed	RIOT	2.630000
    # 2016-04-04	Open	RIOT	2.630000
    df_final.to_csv(output_name, index=False)

if __name__ == '__main__':
    main()
