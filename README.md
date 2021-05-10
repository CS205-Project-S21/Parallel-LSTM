# The Application of Big Data and Big Compute in Stock Price Predictions
Team Members: Minhuan Li, Yichen Geng, Tianlei He, Lihong Zhang

## 1. Project Introduction
This is a Big Data and Big Compute project to predict stock prices, and analyze how parallel computing improves the prediciton performance. 

There are many published models to predict stock prices, but the data processing and model training on time-series data take long time. Big Data and Big Compute are good methods to solve these issues. In this project, We predict future stock prices based on previous stock prices and google news by LSTM models, and improve the runtime performance by parallel computing techniques, e.g. spark, hadoop, loop unrolling, and etc.  
## 2. Workflow
![](./docs/pictures/workflow.png)
The workflow figure above contains 3 steps:
- Our data are composed of 2 parts, Google News and Yahoo Finance Historical Market Data. We fetched these data by the get_news() and get_stock_price() functions in fetch_data.py. 
- Then we process the raw data by general_preprocess.py. 
- Finally we train the LSTM models based on the processed data on Harvard Cannon. 
## 3. Directory structure

```
.
├── data
│   ├── news
│   │   ├── data
│   │   │   ├── cryptocurrency
│   │   │   │   └── GoogleNews_Bitcoin_large_all.csv
│   │   │   └── energy
│   │   │       ├── GoogleNews_Energy_large_all.csv
│   │   │       └── GoogleNews_Energy_Mega_all.csv
│   │   └── scripts
│   │       ├── GetGoogleNews_Bitcoin_large.ipynb
│   │       ├── GetGoogleNews_Energy_large.ipynb
│   │       └── GetGoogleNews_Energy_Mega.ipynb
│   ├── processed_data
│   │   ├── data
│   │   │   ├── processed_data_cryptocurrency.csv
│   │   │   ├── processed_data_cryptocurrency_15.csv
│   │   │   ├── processed_data_cryptocurrency_short.csv
│   │   │   ├── processed_data_energy.csv
│   │   │   ├── processed_data_energy_15.csv
│   │   │   ├── processed_data_energy_mega_15.csv
│   │   │   └── processed_data_energy_short.csv
│   │   └── scripts
│   │       ├── general_preprocess.py
│   │       └── general_preprocess_twitter.py
│   ├── stock_price
│   │   ├── data
│   │   │   ├── cryptocurrency
│   │   │   │   ├── price_BTC.csv
│   │   │   │   ├── price_IXIC.csv
│   │   │   │   ├── price_MARA.csv
│   │   │   │   └── price_RIOT.csv
│   │   │   └── energy
│   │   │       ├── COG_large.csv
│   │   │       ├── DVN_large.csv
│   │   │       ├── HFC_large.csv
│   │   │       ├── price_COG.csv
│   │   │       ├── price_DVN.csv
│   │   │       ├── price_HFC.csv
│   │   │       └── price_IXIC.csv
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
├── model
│   ├── lstm_2009_1
│   │   ├── energy_COG_2009_1.py
│   │   ├── energy_DVN_2009_1.py
│   │   └── energy_HFC_2009_1.py
│   ├── lstm_2009_5
│   │   ├── energy_COG_2009_5.py
│   │   ├── energy_DVN_2009_5.py
│   │   └── energy_HFC_2009_5.py
│   ├── lstm_2016_1
│   │   ├── crypto_BTC_2016_1.py
│   │   ├── crypto_MARA_2016_1.py
│   │   ├── crypto_RIOT_2016_1.py
│   │   ├── energy_COG_2016_1.py
│   │   ├── energy_DVN_2016_1.py
│   │   └── energy_HFC_2016_1.py
│   ├── lstm_2016_5
│   │   ├── crypto_BTC_2016_5.py
│   │   ├── crypto_MARA_2016_5.py
│   │   ├── crypto_RIOT_2016_5.py
│   │   ├── energy_COG_2016_5.py
│   │   ├── energy_DVN_2016_5.py
│   │   └── energy_HFC_2016_5.py
│   ├── model_saved
│   │   ├── cryptocurrency_BTC_2016_1.h5
│   │   ├── cryptocurrency_BTC_2016_5.h5
│   │   ├── cryptocurrency_MARA_2016_1.h5
│   │   ├── cryptocurrency_MARA_2016_5.h5
│   │   ├── cryptocurrency_RIOT_2016_1.h5
│   │   ├── cryptocurrency_RIOT_2016_5.h5
│   │   ├── energy_COG_2009_1.h5
│   │   ├── energy_COG_2009_5.h5
│   │   ├── energy_COG_2016_1.h5
│   │   ├── energy_cog_2016_5.h5
│   │   ├── energy_DVN_2009_1.h5
│   │   ├── energy_DVN_2009_5.h5
│   │   ├── energy_DVN_2016_1.h5
│   │   ├── energy_DVN_2016_5.h5
│   │   ├── energy_HFC_2009_1.h5
│   │   ├── energy_HFC_2009_5.h5
│   │   ├── energy_HFC_2016_1.h5
│   │   └── energy_HFC_2016_5.h5
│   ├── models_for_prediction
│   │   ├── BTC-USD.h5
│   │   ├── COG.h5
│   │   ├── DVN.h5
│   │   ├── HFC.h5
│   │   ├── MARA.h5
│   │   └── RIOT.h5
│   ├── readme.txt
│   └── short
│       ├── LSTM_energy_COG_short.py
│       └── LSTM_energy_short.ipynb
├── utils
│   ├── fetch_context_web.py
│   ├── fetch_data.py
│   ├── fetch_google_news.py
│   └── price_predictor.py
├── playground
├── docs
├── README.md
├── .gitignore
└── requirements.txt
```
```
│   │   │   ├── GoogleNews_Bitcoin_large.csv: the google news that contain 'Bitcoin'
│   │   │   └── GoogleNews_Energy_large.csv: the google news that contain 'oil' and 'gas'
│   ├── GetGoogleNews_Energy_large.ipynb: produce GoogleNews_Energy_large_all.csv
│   ├── GetGoogleNews_Bitcoin_large.ipynb: produce GoogleNews_Bitcoin_large_all.csv
```
## 4. How to use

For stock price prediction, our software can be simply used with following lines of codes:

Step 1: Clone this repo with: 
```
git clone -b main https://github.com/CS205-Project-S21/Parallel-LSTM.git
```

Step 2: Install related packages:
We recommend you to first create a virtual environment with [conda](https://docs.conda.io/en/latest/miniconda.html) and do this step in the virtual environment:
```
conda create -n stock_price python==3.8
conda activate stock_price
```
Then run:
```
pip install Pararrel-LSTM/requirements.txt
```


Step 3: Change into working directory and run command:
```
cd Pararrel-LSTM/utils
python price_predictor.py --ticker <stock-ticker>
```
You can replace the `<stock-ticker>` with one in the following list: `[BTC-USD, MARA, RIOT, COG, DVN, HFC]`. The software will present the prediction in great plots.

<img src="./docs/usage_processed.gif" width="800" />



## 5. Preprocessing of Data
### 5.1 Raw Data
The raw data are stored in the data/stock_price/data/ and data/news/data/ directories.
### 5.2 Preprocessed Data
The preprocessed data are stored in the data/processed_data/data directory.

For detailed explanations of our data types, sources and data processing techniques, please refer to our website https://sites.google.com/g.harvard.edu/group6/home.
## 6. LSTM models
LSTM models are popular time-series models used to predict stock prices. We built LSTM models based on a publication [DP-LSTM: Differential Privacy-inspired LSTM for Stock Prediction Using Financial News](https://arxiv.org/pdf/1912.10806v1.pdf).
### 6.1 Comparison of Models based on Different Datasets
The improvements on LSTM model training by parallel computing may be different for stock prices in different industry and different prediciton windows. To test the scalability of the parallel computing in model training, we build and train LSTM models with the following datasets of different industries and time ranges.
- Industry: 
  - cryptocurrency: BTC-USD, MARA, RIOT
  - energy: COG, DVN, HFC
- Historical market data: 
  - cryptocurrency: year 2016-2021
  - energy: year 2009-2021

There are 4 subfolders in model folder, e.g. lstm_2009_5 contains the LSTM models to predict 5 days' prices based on data from 2009 to 2021, and other subfolders follow the same naming method.
In each subfolder, one python file builds and trains one LSTM model, and the python files are named by (industry)_(stock)_(data starting year)_(# of prediction days). For example, energy_HFC_2009_5.py returns an LSTM model which predict 5 days' prices based on data from 2009 to 2021.

### 6.2 Model Training by cuDNN and GPU 
In general, LSTM training is sequential, which takes long time. We apply CUDA Deep Neural Network (cuDNN) and GPU to LSTM training and get practical speedup = 3 compared to CPU training.
