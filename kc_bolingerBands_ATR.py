# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 12:51:41 2021

@author: NGC
"""

from kiteconnect import KiteConnect
import os
import logging
import pandas as pd
import numpy as np
import datetime as dt


cwd = os.chdir("D:\\AlgorithmicTrading")


#generating access token

access_token = open("access_token.txt",'r').read()
key_secret = open("api_key.txt",'r').read().split()

kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)


#get all nse instrument

instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)
instrument_df.to_csv("NSE_Instruments.csv",index=False)


def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1



def fetchOHLC(ticker,interval,duration):
    """extracts historical data and outputs in the form of dataframe"""
    instrument = instrumentLookup(instrument_df,ticker)
    data = pd.DataFrame(kite.historical_data(instrument,dt.date.today()-dt.timedelta(duration), dt.date.today(),interval))
    data.set_index("date",inplace=True)
    return data

fetchOHLC("ACC","5minute",5)



def bollBnd(DF,n):
    "function to calculate Bollinger Band"#we have taken 2 as a standard deviation
    df = DF.copy()
    df["MA"] = df['close'].rolling(n).mean()
    #df["MA"] = df['close'].ewm(span=n,min_periods=n).mean()
    df["BB_up"] = df["MA"] + 2*df['close'].rolling(n).std(ddof=0) #ddof=0 is required since we want to take the standard deviation of the population and not sample
    df["BB_dn"] = df["MA"] - 2*df['close'].rolling(n).std(ddof=0) #ddof=0 is required since we want to take the standard deviation of the population and not sample
    df["BB_width"] = df["BB_up"] - df["BB_dn"]
    df.dropna(inplace=True)
    return df

ohlc = fetchOHLC("ICICIBANK","5minute",5)
bollBnd = bollBnd(ohlc,20)


def atr(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['high']-df['low'])
    df['H-PC']=abs(df['high']-df['close'].shift(1))
    df['L-PC']=abs(df['low']-df['close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].ewm(com=n,min_periods=n).mean()
    return df['ATR']


ohlc = fetchOHLC("ICICIBANK","5minute",5)
atr = atr(ohlc,20)



def simple_moving(df,n):
    sma = df['close'].rolling(window=n).mean()
    return sma


def rsi(df, n):
    "function to calculate RSI"
    delta = df["close"].diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[n-1]] = np.mean( u[:n]) # first value is average of gains
    u = u.drop(u.index[:(n-1)])
    d[d.index[n-1]] = np.mean( d[:n]) # first value is average of losses
    d = d.drop(d.index[:(n-1)])
    rs = u.ewm(com=n,min_periods=n).mean()/d.ewm(com=n,min_periods=n).mean()
    return 100 - 100 / (1+rs)

ohlc = fetchOHLC("INFY","3minute",5)
rs = rsi(ohlc,14)
a=simple_moving(ohlc,20)
b=simple_moving(ohlc,200)
r = rs.iloc[-1]










