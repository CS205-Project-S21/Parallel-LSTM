# The Application of Big Data and Big Compute in Stock Price Predictions
Team Members: Minhuan Li, Yichen Geng, Tianlei He, Lihong Zhang

## 1. Project Introduction
This is a Big Data and Big Compute project to predict stock prices, and analyze how parallel computing improves the prediciton performance. 

There are many published models to predict stock prices, but the data processing and model training on time-series data take long time. Big Data and Big Compute are good methods to solve these issues. In this project, We predict future stock prices based on previous stock prices and google news by LSTM models, and improve the runtime performance by parallel computing techniques, e.g. spark, hadoop, loop unrolling, and etc.  
## 2. Workflow
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
There are 4 subfolders in model folder, where lstm_2009_5 contains the LSTM models to predict 5 days' prices based on data from 2009 to 2021, etc.
In each subfolder, one python file builds and trains one LSTM model, and the python file is named by (industry)_(stock)_(data starting year)_(# of prediction days). For example, energy_HFC_2009_5.py returns an LSTM model which predict 5 days' prices based on data from 2009 to 2021.
