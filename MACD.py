# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 14:13:19 2021

@author: NGC
"""

from kiteconnect import KiteConnect
import os
import logging
import pandas as pd


cwd = os.chdir("D:\\AlgorithmicTrading")


#generating access token

access_token = open("access_token.txt",'r').read()
key_secret = open("api_key.txt",'r').read().split()

kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)

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

#fetchOHLC("ACC","5minute",5)

def MACD(DF,a,b,c):
    """function to calculate MACD
       typical values a(fast moving average) = 12; 
                      b(slow moving average) =26; 
                      c(signal line ma window) =9"""
    df = DF.copy()
    df["MA_Fast"]=df["close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
    df.dropna(inplace=True)
    return df

ohlc = fetchOHLC("ICICIBANK","5minute",5)
macd = MACD(ohlc,12,26,9)





