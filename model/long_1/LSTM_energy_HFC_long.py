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

stock = 'HFC'
industry = 'energy'

def main():
    # read data
    data = pd.read_csv('../../data/processed_data/data/processed_data_' + industry + '.txt')
    
    # ratio of train and test data 0.8:0.2
    data = data.iloc[:-1]
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
    
    df_prices_train = list(data['StockPrice_' + stock][:train_len])
    df_prices_test = list(data['StockPrice_' + stock][train_len:])
    df_senti_train = list(data['NewsScore'][:train_len])
    df_senti_test = list(data['NewsScore'][train_len:])
    
    # prepare train and test data
    def input_data(df_prices, df_senti):
        x = []
        y = []
        min_max = []
        for i, row in enumerate(df_prices):
            if type(row) == float:
                print(row)
            prices = str2num(row)
            senti = str2num(df_senti[i])
            one_row = []
            for i, p in enumerate(prices[:-3]):
                one_row.append([p, senti[i]])
            x.append(one_row)
            y.append(prices[-3])
            min_max.append(prices[-2:])
        x = np.array(x)
        y = np.array(y)
        return x, y, min_max
    
    x_train, y_train, min_max_train = input_data(df_prices_train, df_senti_train)
    x_test, y_test, min_max_test = input_data(df_prices_test, df_senti_test)
    
    # model parameters setting
    split = 0.85 # train_data percent
    sequence_length=21;  # is the window length of a subset
    normalise= True  # normalize 3 features
    batch_size=64;
    input_dim=2  # ['price','sentiment']
    input_timesteps=21 # the window length of a training data set
    neurons=10  # number of neurons in one LSTM layer
    epochs=50
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
    print('Normalized RMSE on Test set', np.sqrt(mean_squared_error(prediction_seqs, y_test)))
    
    # Denormalize prediction results
    ori_price = pd.read_csv('../../data/stock_price/data/' + industry +'/price_' + stock + '.csv')
    
    max_price = np.max(ori_price['Price'])
    min_price = np.min(ori_price['Price'])
    def denorm(x, min_max):
        de_result = []
        for i, v in enumerate(x):
            min_p, max_p = min_max[i]
            v_denorm = v * (max_p - min_p) + min_p
            de_result.append(v_denorm)
        return de_result
    
    pred_denorm = denorm(prediction_seqs, min_max_test)
    ytest_denorm = denorm(y_test, min_max_test)
    print('Industry: ', industry, '; stock: ', stock.upper())
    print('The max price is {0}, the min price is {1}'.format(max_price, min_price))
    print('The RMSE of predictions is', np.sqrt(mean_squared_error(pred_denorm, ytest_denorm)))
    #plt.plot(y_test, label = 'true')
    #plt.plot(prediction_seqs, label = 'pred')
    #plt.xlabel('days')
    #plt.ylabel('stock price')
    #plt.legend()
if __name__ == '__main__':
    main()