import argparse
import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from keras.models import load_model
from plotly.subplots import make_subplots
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from fetch_data import get_stock_price, get_news


def preprocess_stock_price(df, startdate, enddate):
    def generate_full(sdate, edate):
        full_dates = []
        while sdate <= edate:
            open_time = datetime.datetime.combine(sdate, datetime.time(hour=9, minute=30))
            close_time = datetime.datetime.combine(sdate, datetime.time(hour=16))
            full_dates.extend([open_time, close_time])
            sdate += datetime.timedelta(days=1)
        return full_dates

    def normalize(x):
        """
        Normalize the input to the range between 0 and 1
        """
        x = np.array(x)
        x_min = np.min(x)
        x_max = np.max(x)
        x_normalized = ((x - x_min) / (x_max - x_min)).tolist()
        return x_normalized, x_min, x_max

    dates = [None] * len(df)
    for i in range(len(df)):
        row = df.iloc[i]
        if row['Type'] == 'Open':
            dates[i] = datetime.datetime.strptime(row['Date'], '%Y-%m-%d') + datetime.timedelta(hours=9, minutes=30)
        else:
            dates[i] = datetime.datetime.strptime(row['Date'], '%Y-%m-%d') + datetime.timedelta(hours=16)
    df['Date'] = dates

    full_dates = generate_full(startdate, enddate)

    df_all_dates = pd.DataFrame({'Date': full_dates})
    df_merge = df_all_dates.merge(df, how='outer', left_on='Date', right_on='Date')
    # interpolation
    df_merge['Price_interpol'] = df_merge['Price'].interpolate(method='linear')
    # remove extra rows (this may be necessary for BTC-USD)
    if len(df_merge) != len(df_all_dates):
        df_merge.drop(index=df_merge.tail(int(len(df_merge) - len(df_all_dates))).index, inplace=True)
    # normalization
    price_normalized, price_min, price_max = normalize(df_merge['Price_interpol'].values)
    return price_normalized[:-1], price_min, price_max  # exclude the price at today's close time


def preprocess_news(df):
    # add to the next day if later than 16 pm
    df['true_date'] = [(dt + datetime.timedelta(days=1)).date() if dt.hour >= 16 else dt.date() for dt in
                       df['datetime']]
    # open: prev day >= 16 - curr day < 9; close: curr day 9 - 16
    df['type'] = ['Close' if 9 <= true_dt.hour < 16 else 'Open' for true_dt in df['datetime']]
    # calculate sentiment intensity
    analyzer = SentimentIntensityAnalyzer()
    all_texts = [''] * len(df)
    for i in range(len(df)):
        news = df.iloc[i]
        all_texts[i] = news['title'] + ' ' + news['desc']
    df['all_text'] = all_texts
    df['score'] = [analyzer.polarity_scores(all_text)['compound'] for all_text in all_texts]
    # group by date and type and calculate average sentiment intensity
    df = df.groupby(by=['true_date', 'type'], as_index=False)['score'].mean()
    # sort by date and then by type
    df = df.sort_values(by=['true_date', 'type'], ascending=[True, False])
    scores = df['score'].values
    return scores[:-1]  # exclude the score at today's close time


def predict_price(startdate, enddate, model, x, p_min, p_max, plot=True):
    def generate_full(sdate, edate):
        full_dates = []
        while sdate <= edate:
            full_dates.extend([sdate])
            sdate += datetime.timedelta(days=1)
        return full_dates

    dates = generate_full(startdate, enddate + datetime.timedelta(days=4))

    # predict
    y_pred = model.predict(x)[0]

    # denormalize
    price = np.hstack((x[0, :, 0], y_pred)) * (p_max - p_min) + p_min

    # store data in a DataFrame for visualization
    df = pd.DataFrame()
    df['Date'] = dates
    df['Open'] = price[0::2]  # even entry is open
    df['High'] = np.max(np.column_stack((price[0::2], price[1::2])), axis=1)
    df['Low'] = np.min(np.column_stack((price[0::2], price[1::2])), axis=1)
    df['Close'] = price[1::2]  # odd entry is close
    # fill the last 4 days of sentiment intensity with nan
    placeholder = np.empty(4)
    placeholder[:] = np.nan
    df['SentimentIntensity'] = np.hstack((x[0, :, 1][0::2], placeholder))  # choose either open or close
    # # map to different colors based on sentiment intensity
    # colors = [''] * len(df)
    # for i, sentiment_intensity in enumerate(df['SentimentIntensity'].values):
    #     if sentiment_intensity <= -0.05:
    #         colors[i] = 'red'
    #     elif sentiment_intensity >= 0.05:
    #         colors[i] = 'green'
    #     else:
    #         colors[i] = 'blue'
    # df['Color'] = colors

    # plot
    fig = make_subplots(rows=1, cols=2)

    fig.add_trace(
        go.Candlestick(x=df['Date'],
                       open=df['Open'],
                       high=df['High'],
                       low=df['Low'],
                       close=df['Close']),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['SentimentIntensity']),
        row=1, col=2
    )

    fig['layout']['xaxis']['rangeslider_visible'] = False
    fig['layout']['yaxis']['title'] = 'Price'
    fig['layout']['yaxis2']['title'] = 'News sentiment intensity'
    fig.update_layout(height=600, width=1500)
    fig.show()


def main():
    parser = argparse.ArgumentParser(description="Stock Price Predictor")
    help = "Any ticker from the following: BTC-USD, MARA, RIOT, COG, DVN, HFC"
    parser.add_argument("-t", "--ticker", type=str, help=help, nargs=1)
    args = vars(parser.parse_args())
    ticker = args['ticker'][0]
    # ticker = 'COG'
    tickers = ['BTC-USD', 'MARA', 'RIOT', 'COG', 'DVN', 'HFC']

    if ticker in tickers:
        enddate = datetime.datetime.now()
        day_of_week = enddate.weekday()
        if ticker != 'BTC-USD' and day_of_week > 4:  # Saturday or Sunday
            enddate -= datetime.timedelta(days=1) if day_of_week == 5 else datetime.timedelta(days=2)
        elif enddate.hour < 9:  # before opening
            enddate -= datetime.timedelta(days=1)
        enddate = enddate.date()
        startdate = (enddate - datetime.timedelta(days=10))
        startdate_str, enddate_str = startdate.strftime('%Y-%m-%d'), enddate.strftime('%Y-%m-%d')

        print("Prepare data...")
        df_price = get_stock_price(ticker, startdate_str, enddate_str)
        df_news = get_news('bitcoin', startdate_str, enddate_str, length=1)
        # df_news = pd.read_csv("news_raw.csv", parse_dates=['datetime'])
        print("\nPreprocess data...")
        price, price_min, price_max = preprocess_stock_price(df_price, startdate, enddate)
        scores = preprocess_news(df_news)
        print("\nLoad model...")
        model = load_model('../model/models_for_prediction/' + ticker + '.h5')
        x_input = np.column_stack((price, scores))[np.newaxis, :, :]  # reshape to (1, 21, 2)
        predict_price(startdate, enddate, model, x_input, price_min, price_max)
    else:
        print("Select from the following tickers: BTC-USD, MARA, RIOT, COG, DVN, HFC")


if __name__ == '__main__':
    main()
