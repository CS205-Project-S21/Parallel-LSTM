# The Application of Big Data and Big Compute in Stock Price Predictions
Team Members: Minhuan Li, Yichen Geng, Tianlei He, Lihong Zhang

## 1. Workflow
![](./docs/pictures/workflow.png)
## 2. Directory structure

```
├── LSTM_DP_altered.ipynb
├── LSTM_DP_altered.py
├── README.md
├── data
│   ├── news_Cryptocurrency
│   │   ├── data
│   │   │   ├── GoogleNews_Bitcoin_large.csv: the google news that contain 'Bitcoin'
│   │   │   ├── news_large.csv
│   │   │   ├── news_small.csv
│   │   │   └── profile_test.csv
│   │   └── python_files
│   │       ├── download_news.py
│   │       ├── get_news_3API.py
│   │       └── news_sentiment_analysis.py
│   ├── news_Energy
│   │   ├── data
│   │   │   └── GoogleNews_Energy_large.csv: the google news that contain 'oil' and 'gas'
│   │   └── python_files
│   │       ├── GetNews.ipynb
│   │       ├── download_news.py
│   │       ├── get_news_3API.py
│   │       └── news_sentiment_analysis.py
│   ├── processed_data
│   │   ├── data
│   │   │   ├── processed_data_crypto_RIOT.csv
│   │   │   ├── processed_data_energy_CHK.csv
│   │   │   ├── processed_data_energy_DVN.csv
│   │   │   └── processed_data_energy_HFC.csv
│   │   └── python_files
│   │       └── General_PreProcess.py
│   ├── stock_price
│   │   └── python_files
│   ├── stock_price_Cryptocurrency
│   │   ├── data
│   │   │   ├── alldate_BTC.csv
│   │   │   ├── alldate_IXIC.csv
│   │   │   ├── alldate_RIOT.csv
│   │   │   └── profile_test.csv
│   │   └── python_files
│   │       ├── download_historical_price.py
│   │       └── preprocess_historical_price.py
│   ├── stock_price_Energy
│   │   ├── data
│   │   │   ├── alldate_CHK.csv
│   │   │   ├── alldate_DVN.csv
│   │   │   └── alldate_HFC.csv
│   │   └── python_files
│   │       ├── download_historical_price.py
│   │       └── preprocess_historical_price.py
│   └── twitter
│       ├── data
│       │   └── twitter_sentiment_scores.txt
│       └── python_files
│           ├── download_twitter.py
│           ├── tweet_processing.py
│           ├── twitter_client.py
│           └── visualize.py
├── playground: draft codes to fetch and preprocess data
│   ├── BingNewsAPI.ipynb
│   ├── CombineSentimentStock.ipynb
│   ├── ContextualWebSeachAPI.ipynb
│   ├── DL_Clean_from_3Sources.ipynb
│   ├── DataPipline_test.ipynb
│   ├── GetGoogleNews.ipynb
│   ├── GetGoogleNews_Energy_large.ipynb: produce GoogleNews_Energy_large_all.csv
│   ├── GetGoogleNews_Bitcoin_large.ipynb: produce GoogleNews_Bitcoin_large_all.csv
│   ├── GetNews.ipynb
│   ├── GoogleNewsPackage.ipynb
│   ├── ModifyGoogleNews.ipynb
│   ├── NewsAPI.ipynb
│   ├── NewsAPI_Notes.md
│   └── NewsCatcher.ipynb
├── requirements.txt
└── utils: utilities to fetch data
    ├── __pycache__
    │   └── fetchgooglenews.cpython-38.pyc
    └── fetchgooglenews.py
```

│   │   │   ├── GoogleNews_Bitcoin_large.csv: the google news that contain 'Bitcoin'
│   │   │   └── GoogleNews_Energy_large.csv: the google news that contain 'oil' and 'gas'
│   ├── GetGoogleNews_Energy_large.ipynb: produce GoogleNews_Energy_large_all.csv
│   ├── GetGoogleNews_Bitcoin_large.ipynb: produce GoogleNews_Bitcoin_large_all.csv
## 2. Instructions for running
## 2. Preprocessing of Data
### 2.1 Raw Data
### 2.2 Proprecessed Data
## 3. LSTM models
