# The Application of Big Data and Big Compute in Stock Price Predictions
Team Members: Minhuan Li, Yichen Geng, Tianlei He, Lihong Zhang

## 1. Workflow
![](./docs/pictures/workflow.png)
## 2. Directory structure

```
├.
├── .gitignore
├── data
│   ├── news
│   │   ├── data
│   │   │   ├── cryptocurrency
│   │   │   │   └── GoogleNews_Bitcoin_large_all.csv
│   │   │   └── energy
│   │   │       └── GoogleNews_Energy_large_all.csv
│   │   └── scripts
│   │       ├── GetGoogleNews_Bitcoin_large.ipynb
│   │       └── GetGoogleNews_Energy_large.ipynb
│   ├── processed_data
│   │   ├── data
│   │   │   └── processed_data_energy.csv
│   │   └── scripts
│   │       └── General_PreProcess.py
│   ├── stock_price
│   │   ├── data
│   │   │   ├── cryptocurrency
│   │   │   │   ├── price_BTC.csv
│   │   │   │   ├── price_IXIC.csv
│   │   │   │   ├── price_MARA.csv
│   │   │   │   └── price_RIOT.csv
│   │   │   └── energy
│   │   │       ├── price_COG.csv
│   │   │       ├── price_DVN.csv
│   │   │       └── price_HFC.csv
│   │   └── scripts
│   │       └── download_historical_price.py
│   └── twitter
│       ├── data
│       │   ├── historical
│       │   │   ├── cryptocurrency
│       │   │   │   └── tweets.csv
│       │   │   └── energy
│       │   │       └── tweets.csv
│       │   └── streaming
│       │       ├── twitter_sentiment_scores_cryptocurrency.txt
│       │       ├── twitter_sentiment_scores_energy.txt
│       │       └── twitter_sentiment_scores_test_for_fun.txt
│       └── scripts
│           ├── combine_historical_tweets.py
│           ├── download_historical_tweets.py
│           ├── download_streaming_tweets.py
│           ├── process_streaming_tweets.py
│           └── visualize_streaming_tweets.py
├── docs
│   └── pictures
│       └── workflow.png
├── model
│   ├── LSTM_DP_altered.ipynb
│   └── LSTM_DP_altered.py
├── playground
│   ├── BingNewsAPI.ipynb
│   ├── CombineSentimentStock.ipynb
│   ├── ContextualWebSeachAPI.ipynb
│   ├── DataPipline_test.ipynb
│   ├── DL_Clean_from_3Sources.ipynb
│   ├── GetGoogleNews.ipynb
│   ├── GetNews.ipynb
│   ├── GoogleNewsPackage.ipynb
│   ├── ModifyGoogleNews.ipynb
│   ├── NewsAPI.ipynb
│   ├── NewsAPI_Notes.md
│   ├── NewsCatcher.ipynb
│   └── price_correlation.ipynb
├── README.md
├── requirements.txt
└── utils
    ├── fetchcontextweb.py
    └── fetchgooglenews.py
```
```
│   │   │   ├── GoogleNews_Bitcoin_large.csv: the google news that contain 'Bitcoin'
│   │   │   └── GoogleNews_Energy_large.csv: the google news that contain 'oil' and 'gas'
│   ├── GetGoogleNews_Energy_large.ipynb: produce GoogleNews_Energy_large_all.csv
│   ├── GetGoogleNews_Bitcoin_large.ipynb: produce GoogleNews_Bitcoin_large_all.csv
```
## 2. Instructions for running
## 2. Preprocessing of Data
### 2.1 Raw Data
### 2.2 Proprecessed Data
## 3. LSTM models
