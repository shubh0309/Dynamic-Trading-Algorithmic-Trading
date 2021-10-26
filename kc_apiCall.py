# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 23:59:50 2021

@author: NGC
"""

from kiteconnect import KiteConnect
import os


cwd =os.chdir("D:\\AlgorithmicTrading")

#generatig trading session

access_token = open("access_token.txt",'r').read()
key_secret = open("api_key.txt",'r').read().split()

kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)


#fetch quote datils
quote = kite.quote("NSE:INFY")

#fetching last trading price of an instrument
ltp = kite.ltp("NSE:ACC")

#fetch order details
orders = kite.orders()

#fetch position details
positions = kite.positions()

#fetch holding details
holdings = kite.holdings()
