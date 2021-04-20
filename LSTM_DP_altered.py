'''
# LSTM model
from https://github.com/Xinyi6/DP-LSTM-Differential-Privacy-inspired-LSTM-for-Stock-Prediction-Using-Financial-News and make some changes

### Where we can use big compute:
- Adding noises to data
- The computations of multi-sequence predictions
- The calculation of MSE

### Where we cannot use big compute:
- The training of LSTM
'''

import numpy as np
import pandas as pd
#import datetime as dt
#from numpy import newaxis
from keras.layers import Dense, Activation, Dropout, LSTM
from keras.models import Sequential, load_model
#from keras.callbacks import EarlyStopping, ModelCheckpoint
#from sklearn.linear_model import LinearRegression
#from sklearn.ensemble import RandomForestRegressor
#from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

#from math import pi,sqrt,exp,pow,log
#from numpy.linalg import det, inv
#from abc import ABCMeta, abstractmethod
#from sklearn import cluster

#import statsmodels.api as sm 
#import scipy.stats as scs
#import scipy.optimize as sco
#import scipy.interpolate as sci
#from scipy import stats

#import matplotlib.pyplot as plt


def main():
    # read data
    data = pd.read_csv('data/processed_data.csv')
    
    # ratio of train and test data 0.8:0.2
    train_len = int(len(data)*0.8)
    test_len = len(data) - train_len
    
    # process data
    def str2num(row):
        l = row.split(',')
        result = []
        result.append(float(l[0][1:]))
        for n in l[1:-1]:
            result.append(float(n))
        result.append(float(l[-1][:-1]))
        return result
    
    df_prices_train = list(data['StockPrice'][:train_len])
    df_prices_test = list(data['StockPrice'][train_len:])
    df_senti_train = list(data['NewsScore'][:train_len])
    df_senti_test = list(data['NewsScore'][train_len:])
    
    # prepare train and test data
    def input_data(df_prices, df_senti):
        x = []
        y = []
        for i, row in enumerate(df_prices):
            prices = str2num(row)
            senti = str2num(df_senti[i])
            one_row = []
            for i, p in enumerate(prices[:-1]):
                one_row.append([p, senti[i]])
            x.append(one_row)
            y.append(prices[-1])
        x = np.array(x)
        y = np.array(y)
        return x, y
    
    x_train, y_train = input_data(df_prices_train, df_senti_train)
    x_test, y_test = input_data(df_prices_test, df_senti_test)
    
    # model parameters setting
    split = 0.85 # train_data percent
    sequence_length=21;  # is the window length of a subset
    normalise= True  # normalize 3 features
    batch_size=64;
    input_dim=2  # ['price','review','sentiment']
    input_timesteps=21 # the window length of a training data set
    neurons=10  # number of neurons in one LSTM layer
    epochs=10
    prediction_len=1  # predict one day's price
    dense_output=1  # output size of the last dense layer
    drop_out=0.1  # dropout rate
    
    # Build LSTM MODEL
    model = Sequential()
    model.add(LSTM(neurons, input_shape=(input_timesteps, input_dim), return_sequences = True))
    model.add(Dropout(drop_out))
    model.add(LSTM(neurons,return_sequences = True))
    model.add(LSTM(neurons,return_sequences =False))
    model.add(Dropout(drop_out))
    model.add(Dense(dense_output, activation='linear'))
    # Compile model
    model.compile(loss='mean_squared_error',
                    optimizer='adam')
    # Fit the model
    model.fit(x_train,y_train,epochs=epochs,batch_size=batch_size)
    
    #multi sequence predict
    prediction_seqs = model.predict(x_test).reshape(-1,) # prediction data
    # !! parallelizable !!
    print('RMSE on Test set', np.sqrt(mean_squared_error(prediction_seqs, y_test)))
    
    #plt.plot(y_test, label = 'true')
    #plt.plot(prediction_seqs, label = 'pred')
    #plt.xlabel('days')
    #plt.ylabel('stock price')
    #plt.legend()
if __name__ == '__main__':
    main()