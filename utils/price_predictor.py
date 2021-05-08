import argparse
import datetime

from fetchdata import get_stock_price, get_news
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd


def preprocess_stock_price(df):
    # interpolation
    # normalization
    # return normalized price, min and max
    pass


def preprocess_news(df, enddate):
    # add to the next day if later than 16 pm
    df['true_date'] = [(dt + datetime.timedelta(days=1)).date() if dt.hour >= 16 else dt.date() for dt in df['datetime']]
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
    # select time of interest
    df = df[df['true_date'] <= enddate]
    # df.to_csv("news_score.csv", index=False)
    pass


def predict_price(model, x, min, max):
    # predict
    # denormalize prediction
    pass


def plot_prediction():
    # plot prediction
    pass


def main():
    # parser = argparse.ArgumentParser(description="Stock Price Predictor")
    # help = "Any ticker from the following: BTC-USD, MARA, RIOT, COG, DVN, HFC"
    # parser.add_argument("-t", "--ticker", type=str, help=help, nargs=1)
    # arg = vars(parser.parse_args())
    arg = 'BTC-USD'
    tickers = ['BTC-USD', 'MARA', 'RIOT', 'COG', 'DVN', 'HFC']

    if arg in tickers:
        enddate = datetime.datetime.now().date()
        # startdate = (enddate - datetime.timedelta(days=10))
        startdate = (enddate - datetime.timedelta(days=1))
        startdate, enddate = startdate.strftime('%Y-%m-%d'), enddate.strftime('%Y-%m-%d')

        # df_price = get_stock_price('BTC-USD', startdate, enddate)
        # df_news = get_news('bitcoin', startdate, enddate)
        df_news = pd.read_csv("news_raw.csv", parse_dates=['datetime'])
        preprocess_news(df_news, enddate)
    else:
        print("Select from the following tickers: BTC-USD, MARA, RIOT, COG, DVN, HFC")


if __name__ == '__main__':
    main()
