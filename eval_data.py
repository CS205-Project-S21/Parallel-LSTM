#!/usr/bin/env python
# coding: utf-8

import finnhub  #api finnhub to get more evaluation
import time
import datetime
import numpy as np
from calendar import monthrange # calculate number of days in a month

def aggregate_indicator(name):
    tech_anls = finnhub_client.aggregate_indicator(name, 'D')
    overal_list = np.zeros(3)
    overal_list[0] = tech_anls['technicalAnalysis']['count']['buy']
    overal_list[1] = tech_anls['technicalAnalysis']['count']['neutral']
    overal_list[2] = tech_anls['technicalAnalysis']['count']['sell']
    return overal_list

def get_recom(name, date_list):
    recom_rate = finnhub_client.recommendation_trends(name)
    evaluate = np.zeros(5) # buy, hold, sell, strongbuy, strongsell
    for date in date_list:
        if list(recom_rate[0].values())[2] == date:
            total = (list(recom_rate[0].values())[0] + list(recom_rate[0].values())[1] + list(recom_rate[0].values())[3]
                      + list(recom_rate[0].values())[4] + list(recom_rate[0].values())[5])
            evaluate[0] = list(recom_rate[0].values())[0] / total
            evaluate[1] = list(recom_rate[0].values())[1] / total
            evaluate[2] = list(recom_rate[0].values())[3] / total
            evaluate[3] = list(recom_rate[0].values())[4] / total
            evaluate[4] = list(recom_rate[0].values())[5] / total
    return evaluate


def date10_list():
    # generate the list of 10 days
    today = datetime.datetime.today()
    date_list = []
    for i in range(20):
        num_days = monthrange(today.year, today.month - 1)[1]  # number of days in last month
        if today.month < 10 and 0 < today.day - i < 10:
            date_list.append("{}-0{}-0{}".format(today.year, today.month, today.day-i))
        elif today.month < 10 and today.day - i < 0:
            date_list.append("{}-0{}-{}".format(today.year, today.month-1, num_days + today.day-i))          
        elif today.month >= 10 and 0 < today.day - i < 10:
            date_list.append("{}-{}-0{}".format(today.year, today.month, today.day-i))
        elif today.month >= 10 and today.day - i < 0:
            date_list.append("{}-0{}-{}".format(today.year, today.month-1, num_days + today.day-i))
        elif today.month < 10 and today.day - i >= 10:
            date_list.append("{}-0{}-{}".format(today.year, today.month, today.day-i))
        elif today.month >= 10 and today.day -i >= 10:
            date_list.append("{}-{}-{}".format(today.year, today.month, today.day-i))
    return date_list


date = date10_list()
big_firm_eval = get_recom('RIOT', date)
print(big_firm_eval)

