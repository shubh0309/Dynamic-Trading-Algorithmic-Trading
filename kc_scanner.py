# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 11:31:03 2021

@author: NGC
"""
from kiteconnect import KiteConnect
import pandas as pd
import datetime as dt
import os
import time
import numpy as np
import requests



cwd = os.chdir("D:\\AlgorithmicTrading")


#generate trading session
access_token = open("access_token.txt",'r').read()
key_secret = open("api_key.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)

#get dump of all NSE instruments
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)

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

def doji(ohlc_df):    
    """returns dataframe with doji candle column"""
    df = ohlc_df.copy()
    avg_candle_size = abs(df["close"] - df["open"]).median()
    df["doji"] = abs(df["close"] - df["open"]) <=  (0.05 * avg_candle_size)
    return df

def maru_bozu(ohlc_df):    
    """returns dataframe with maru bozu candle column"""
    df = ohlc_df.copy()
    avg_candle_size = abs(df["close"] - df["open"]).median()
    df["h-c"] = df["high"]-df["close"]
    df["l-o"] = df["low"]-df["open"]
    df["h-o"] = df["high"]-df["open"]
    df["l-c"] = df["low"]-df["close"]
    df["maru_bozu"] = np.where((df["close"] - df["open"] > 2*avg_candle_size) & \
                               (df[["h-c","l-o"]].max(axis=1) < 0.005*avg_candle_size),"maru_bozu_green",
                               np.where((df["open"] - df["close"] > 2*avg_candle_size) & \
                               (abs(df[["h-o","l-c"]]).max(axis=1) < 0.005*avg_candle_size),"maru_bozu_red",False))
    df.drop(["h-c","l-o","h-o","l-c"],axis=1,inplace=True)
    return df

def hammer(ohlc_df):    
    """returns dataframe with hammer candle column"""
    df = ohlc_df.copy()
    df["hammer"] = (((df["high"] - df["low"])>3*(df["open"] - df["close"])) & \
                   ((df["close"] - df["low"])/(.001 + df["high"] - df["low"]) > 0.6) & \
                   ((df["open"] - df["low"])/(.001 + df["high"] - df["low"]) > 0.6)) & \
                   (abs(df["close"] - df["open"]) > 0.1* (df["high"] - df["low"]))
    return df


def shooting_star(ohlc_df):    
    """returns dataframe with shooting star candle column"""
    df = ohlc_df.copy()
    df["sstar"] = (((df["high"] - df["low"])>3*(df["open"] - df["close"])) & \
                   ((df["high"] - df["close"])/(.001 + df["high"] - df["low"]) > 0.6) & \
                   ((df["high"] - df["open"])/(.001 + df["high"] - df["low"]) > 0.6)) & \
                   (abs(df["close"] - df["open"]) > 0.1* (df["high"] - df["low"]))
    return df

def levels(ohlc_day):    
    """returns pivot point and support/resistance levels"""
    high = round(ohlc_day["high"][-1],2)
    low = round(ohlc_day["low"][-1],2)
    close = round(ohlc_day["close"][-1],2)
    pivot = round((high + low + close)/3,2)
    r1 = round((2*pivot - low),2)
    r2 = round((pivot + (high - low)),2)
    r3 = round((high + 2*(pivot - low)),2)
    s1 = round((2*pivot - high),2)
    s2 = round((pivot - (high - low)),2)
    s3 = round((low - 2*(high - pivot)),2)
    return (pivot,r1,r2,r3,s1,s2,s3)

def trend(ohlc_df,n):
    "function to assess the trend by analyzing each candle"
    df = ohlc_df.copy()
    df["up"] = np.where(df["low"]>=df["low"].shift(1),1,0)
    df["dn"] = np.where(df["high"]<=df["high"].shift(1),1,0)
    if df["close"][-1] > df["open"][-1]:
        if df["up"][-1*n:].sum() >= 0.7*n:
            return "uptrend"
    elif df["open"][-1] > df["close"][-1]:
        if df["dn"][-1*n:].sum() >= 0.7*n:
            return "downtrend"
    else:
        return None
   
def res_sup(ohlc_df,ohlc_day):
    """calculates closest resistance and support levels for a given candle"""
    level = ((ohlc_df["close"][-1] + ohlc_df["open"][-1])/2 + (ohlc_df["high"][-1] + ohlc_df["low"][-1])/2)/2
    p,r1,r2,r3,s1,s2,s3 = levels(ohlc_day)
    l_r1=level-r1
    l_r2=level-r2
    l_r3=level-r3
    l_p=level-p
    l_s1=level-s1
    l_s2=level-s2
    l_s3=level-s3
    lev_ser = pd.Series([l_p,l_r1,l_r2,l_r3,l_s1,l_s2,l_s3],index=["p","r1","r2","r3","s1","s2","s3"])
    sup = lev_ser[lev_ser>0].idxmin()
    res = lev_ser[lev_ser<0].idxmax()
    return (eval('{}'.format(res)), eval('{}'.format(sup)))

def candle_type(ohlc_df):    
    """returns the candle type of the last candle of an OHLC DF"""
    candle = None
    if doji(ohlc_df)["doji"][-1] == True:
        candle = "doji"    
    if maru_bozu(ohlc_df)["maru_bozu"][-1] == "maru_bozu_green":
        candle = "maru_bozu_green"       
    if maru_bozu(ohlc_df)["maru_bozu"][-1] == "maru_bozu_red":
        candle = "maru_bozu_red"        
    if shooting_star(ohlc_df)["sstar"][-1] == True:
        candle = "shooting_star"        
    if hammer(ohlc_df)["hammer"][-1] == True:
        candle = "hammer"       
    return candle



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



def simple_moving(df,n):
    sma = df['close'].rolling(window=n).mean()
    return sma



def st_dir_refresh(ohlc,ticker):
    """function to check for supertrend reversal"""
    global st_dir
    if ohlc["st1"][-1] > ohlc["close"][-1] and ohlc["st1"][-2] < ohlc["close"][-2]:
        st_dir[ticker][0] = "red"
    if ohlc["st2"][-1] > ohlc["close"][-1] and ohlc["st2"][-2] < ohlc["close"][-2]:
        st_dir[ticker][1] = "red"
    if ohlc["st3"][-1] > ohlc["close"][-1] and ohlc["st3"][-2] < ohlc["close"][-2]:
        st_dir[ticker][2] = "red"
    if ohlc["st1"][-1] < ohlc["close"][-1] and ohlc["st1"][-2] > ohlc["close"][-2]:
        st_dir[ticker][0] = "green"
    if ohlc["st2"][-1] < ohlc["close"][-1] and ohlc["st2"][-2] > ohlc["close"][-2]:
        st_dir[ticker][1] = "green"
    if ohlc["st3"][-1] < ohlc["close"][-1] and ohlc["st3"][-2] > ohlc["close"][-2]:
        st_dir[ticker][2] = "green"

def sl_price(ohlc):
    """function to calculate stop loss based on supertrends"""
    st = ohlc.iloc[-1,[-3,-2,-1]]
    if st.min() > ohlc["close"][-1]:
        sl = (0.6*st.sort_values(ascending = True)[0]) + (0.4*st.sort_values(ascending = True)[1])
    elif st.max() < ohlc["close"][-1]:
        sl = (0.6*st.sort_values(ascending = False)[0]) + (0.4*st.sort_values(ascending = False)[1])
    else:
        sl = st.mean()
    return round(sl,1)





def placeSLOrder(symbol,buy_sell,quantity,sl_price):    
    # Place an intraday stop loss order on NSE - handles market orders converted to limit orders
    if buy_sell == "buy":
        t_type=kite.TRANSACTION_TYPE_BUY
        t_type_sl=kite.TRANSACTION_TYPE_SELL
    elif buy_sell == "sell":
        t_type=kite.TRANSACTION_TYPE_SELL
        t_type_sl=kite.TRANSACTION_TYPE_BUY
    market_order = kite.place_order(tradingsymbol=symbol,
                    exchange=kite.EXCHANGE_NSE,
                    transaction_type=t_type,
                    quantity=quantity,
                    order_type=kite.ORDER_TYPE_MARKET,
                    product=kite.PRODUCT_MIS,
                    variety=kite.VARIETY_REGULAR)
    a = 0
    while a < 10:
        try:
            order_list = kite.orders()
            break
        except:
            print("can't get orders..retrying")
            a+=1
    for order in order_list:
        if order["order_id"]==market_order:
            if order["status"]=="COMPLETE":
                kite.place_order(tradingsymbol=symbol,
                                exchange=kite.EXCHANGE_NSE,
                                transaction_type=t_type_sl,
                                quantity=quantity,
                                order_type=kite.ORDER_TYPE_SL,
                                price=sl_price,
                                trigger_price = sl_price,
                                product=kite.PRODUCT_MIS,
                                variety=kite.VARIETY_REGULAR)
            else:
                kite.cancel_order(order_id=market_order,variety=kite.VARIETY_REGULAR)



def ModifyOrder(order_id,price):    
    # Modify order given order id
    kite.modify_order(order_id=order_id,
                    price=price,
                    trigger_price=price,
                    order_type=kite.ORDER_TYPE_SL,
                    variety=kite.VARIETY_REGULAR)      



'''
def supertrend(DF,n,m):
    """function to calculate Supertrend given historical candle data
        n = n day ATR - usually 7 day ATR is used
        m = multiplier - usually 2 or 3 is used"""
    df = DF.copy()
    df['ATR'] = atr(df,n)
    df["B-U"]=((df['high']+df['low'])/2) + m*df['ATR'] 
    df["B-L"]=((df['high']+df['low'])/2) - m*df['ATR']
d    df["U-B"]=df["B-U"]
    df["L-B"]=df["B-L"]
    ind = df.index
    for i in range(n,len(df)):
        if df['close'][i-1]<=df['U-B'][i-1]:
            df.loc[ind[i],'U-B']=min(df['B-U'][i],df['U-B'][i-1])
        else:
            df.loc[ind[i],'U-B']=df['B-U'][i]    
    for i in range(n,len(df)):
        if df['close'][i-1]>=df['L-B'][i-1]:
            df.loc[ind[i],'L-B']=max(df['B-L'][i],df['L-B'][i-1])
        else:
            df.loc[ind[i],'L-B']=df['B-L'][i]  
    df['Strend']=np.nan
    for test in range(n,len(df)):
        if df['close'][test-1]<=df['U-B'][test-1] and df['close'][test]>df['U-B'][test]:
            df.loc[ind[test],'Strend']=df['L-B'][test]
            break
        if df['close'][test-1]>=df['L-B'][test-1] and df['close'][test]<df['L-B'][test]:
            df.loc[ind[test],'Strend']=df['U-B'][test]
            break
    for i in range(test+1,len(df)):
        if df['Strend'][i-1]==df['U-B'][i-1] and df['close'][i]<=df['U-B'][i]:
            df.loc[ind[i],'Strend']=df['U-B'][i]
        elif  df['Strend'][i-1]==df['U-B'][i-1] and df['close'][i]>=df['U-B'][i]:
            df.loc[ind[i],'Strend']=df['L-B'][i]
        elif df['Strend'][i-1]==df['L-B'][i-1] and df['close'][i]>=df['L-B'][i]:
            df.loc[ind[i],'Strend']=df['L-B'][i]
        elif df['Strend'][i-1]==df['L-B'][i-1] and df['close'][i]<=df['L-B'][i]:
            df.loc[ind[i],'Strend']=df['U-B'][i]
    return df['Strend']

'''







def candle_pattern(ohlc_df,ohlc_day,ticker):    
    """returns the candle pattern identified"""
    pattern = None
    signi = "low"
    avg_candle_size = abs(ohlc_df["close"] - ohlc_df["open"]).median()
    sup, res = res_sup(ohlc_df,ohlc_day)
    
    
    rs = rsi(ohlc_df,14)
    r = rs.iloc[-1]
    

    
    if (sup - 1.5*avg_candle_size) < ohlc_df["close"][-1] < (sup + 1.5*avg_candle_size):
        signi = "HIGH"
        
    if (res - 1.5*avg_candle_size) < ohlc_df["close"][-1] < (res + 1.5*avg_candle_size):
        signi = "HIGH"
    
    if candle_type(ohlc_df) == 'doji' \
        and ohlc_df["close"][-1] > ohlc_df["close"][-2] \
        and ohlc_df["close"][-1] > ohlc_df["open"][-1]:
            pattern = "doji_bullish"
    
    if candle_type(ohlc_df) == 'doji' \
        and ohlc_df["close"][-1] < ohlc_df["close"][-2] \
        and ohlc_df["close"][-1] < ohlc_df["open"][-1]:
            pattern = "doji_bearish" 
            
    if candle_type(ohlc_df) == "maru_bozu_green":
        pattern = "maru_bozu_bullish"
    
    if candle_type(ohlc_df) == "maru_bozu_red":
        pattern = "maru_bozu_bearish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "uptrend" and candle_type(ohlc_df) == "hammer":
        pattern = "hanging_man_bearish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "downtrend" and candle_type(ohlc_df) == "hammer":
        pattern = "hammer_bullish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "uptrend" and candle_type(ohlc_df) == "shooting_star":
        pattern = "shooting_star_bearish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "uptrend" \
        and candle_type(ohlc_df) == "doji" \
        and ohlc_df["high"][-1] < ohlc_df["close"][-2] \
        and ohlc_df["low"][-1] > ohlc_df["open"][-2]:
        pattern = "harami_cross_bearish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "downtrend" \
        and candle_type(ohlc_df) == "doji" \
        and ohlc_df["high"][-1] < ohlc_df["open"][-2] \
        and ohlc_df["low"][-1] > ohlc_df["close"][-2]:
        pattern = "harami_cross_bullish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "uptrend" \
        and candle_type(ohlc_df) != "doji" \
        and ohlc_df["open"][-1] > ohlc_df["high"][-2] \
        and ohlc_df["close"][-1] < ohlc_df["low"][-2]:
        pattern = "engulfing_bearish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "downtrend" \
        and candle_type(ohlc_df) != "doji" \
        and ohlc_df["close"][-1] > ohlc_df["high"][-2] \
        and ohlc_df["open"][-1] < ohlc_df["low"][-2]:
        pattern = "engulfing_bullish"
       
        
       
   # print(signi)
    #print(pattern)
    #print(r)
    quantity = int(2000/ohlc_df["close"][-1])
#    print(quantity)
 
    if signi == "HIGH":
        if(r>=50):
            if(pattern == "engulfing_bullish" or pattern == "harami_cross_bullish" or pattern == "hammer_bullish" or pattern == "maru_bozu_bullish" or pattern == "doji_bullish"):
               # placeSLOrder(ticker,"buy",quantity,sl_price(ohlc_df))       
               #placeSLOrder(ticker,"buy",quantity,sl_price(ohlc_df))
               
               t_type=kite.TRANSACTION_TYPE_BUY
               kite.place_order(tradingsymbol=ticker,
                    exchange=kite.EXCHANGE_NSE,
                    transaction_type=t_type,
                    quantity=quantity,
                    order_type=kite.ORDER_TYPE_MARKET,
                    product=kite.PRODUCT_MIS,
                    variety=kite.VARIETY_REGULAR)
               
               requests.post('https://textbelt.com/text', {
                       'phone': '+919792836413',
                       'message': 'Hello world BUY ORDER ',
                       'key': 'textbelt',
                       })
               
               print("BUY ORDER PLACED")
        else:
            if(pattern == "engulfing_bearish" or pattern == "harami_cross_bearish" or pattern == "shooting_star_bearish" or pattern == "hanging_man_bearish" or pattern == "maru_bozu_bearish" or pattern == "doji_bearish"):
                t_type=kite.TRANSACTION_TYPE_SELL
                kite.place_order(tradingsymbol=ticker,
                    exchange=kite.EXCHANGE_NSE,
                    transaction_type=t_type,
                    quantity=quantity,
                    order_type=kite.ORDER_TYPE_MARKET,
                    product=kite.PRODUCT_MIS,
                    variety=kite.VARIETY_REGULAR)
                
                
                requests.post('https://textbelt.com/text', {
                       'phone': '+919792836413',
                       'message': 'Hello world SELL ORDER ',
                       'key': 'textbelt',
                       })
                
                #   placeSLOrder(ticker,"sell",quantity,sl_price(ohlc_df))
                print("SELL ORDER PLACED")
    
    return "Significance - {}, Pattern - {} , RSI value {}".format(signi,pattern,r)





#tickers = ["JINDALSTEL","ZEEL","FRETAIL","WIPRO","VEDL"]


tickers = ["ZEEL","WIPRO","VEDL","ULTRACEMCO","UPL","TITAN","TECHM","TATASTEEL",
           "TATAMOTORS","TCS","SUNPHARMA","SBIN","SHREECEM","RELIANCE","POWERGRID",
           "ONGC","NESTLEIND","MARUTI","M&M","LT","KOTAKBANK","JSWSTEEL","INFY",
           "INDUSINDBK","ITC","ICICIBANK","HDFC","HINDUNILVR","HINDALCO",
           "HEROMOTOCO","HDFCBANK","HCLTECH","GRASIM","GAIL","EICHERMOT","DRREDDY",
           "COALINDIA","CIPLA","BRITANNIA","INFRATEL","BHARTIARTL","BPCL","BAJAJFINSV",
           "BAJFINANCE","BAJAJ-AUTO","AXISBANK","ASIANPAINT","ADANIPORTS",
           "MCDOWELL-N","UBL","NIACL","SIEMENS","SRTRANSFIN","SBILIFE","PNB",
           "PGHH","PFC","PEL","PIDILITIND","PETRONET","PAGEIND","OFSS","NMDC",
           "MOTHERSUMI","MARICO","LUPIN","L&TFH","INDIGO","IBULHSGFIN","ICICIPRULI",
           "ICICIGI","HINDZINC","HINDPETRO","HAVELLS","HDFCLIFE","HDFCAMC","GODREJCP",
           "GICRE","DIVISLAB","DABUR","DLF","CONCOR","COLPAL","CADILAHC","BOSCHLTD",
           "BIOCON","BERGEPAINT","BANKBARODA","BANDHANBNK","BAJAJHLDNG","DMART",
           "AUROPHARMA","ASHOKLEY","AMBUJACEM","ADANITRANS","ACC",
           "WHIRLPOOL","WABCOINDIA","VOLTAS","VINATIORGA","VBL","VARROC","VGUARD",
           "UNIONBANK","UCOBANK","TRENT","TORNTPOWER","TORNTPHARM","THERMAX","RAMCOCEM",
           "TATAPOWER","TATACONSUM","TVSMOTOR","TTKPRESTIG","SYNGENE","SYMPHONY",
           "SUPREMEIND","SUNDRMFAST","SUNDARMFIN","SUNTV","SAIL","SOLARINDS",
           "SHRIRAMCIT","SANOFI","SRF","SKFINDIA","SJVN","RELAXO",
           "RAJESHEXPO","RECLTD","RBLBANK","QUESS","PRESTIGE","POLYCAB","PHOENIXLTD",
           "OIL","OBEROIRLTY","NATIONALUM",
           "NLCINDIA","NBCC","NATCOPHARM","MUTHOOTFIN","MPHASIS","MOTILALOFS","MINDTREE",
           "MFSL","MRPL","MANAPPURAM","MAHINDCIE","M&MFIN","MGL","MRF","LTI","LICHSGFIN",
           "LTTS","KANSAINER","KRBL","JUBILANT","JUBLFOOD","JINDALSTEL","JSWENERGY",
           "IPCALAB","NAUKRI","IGL","IOB","INDHOTEL","INDIANB","IDFCFIRSTB",
           "IDBI","HUDCO","HONAUT","HAL","HEG","GSPL",
           "GUJGASLTD","GRAPHITE","GODREJPROP","GODREJIND","GODREJAGRO","GLENMARK",
           "GLAXO","GILLETTE","GMRINFRA","FORTIS","FEDERALBNK",
           "EXIDEIND","ESCORTS","ERIS","ENGINERSIN","ENDURANCE","EMAMILTD","EDELWEISS",
           "EIHOTEL","LALPATHLAB","DALBHARAT","CUMMINSIND","CROMPTON","COROMANDEL","CUB",
           "CHOLAFIN","CHOLAHLDNG","CENTRALBK","CASTROLIND","CANBK","CRISIL","CESC",
           "BBTC","BLUEDART","BHEL","BHARATFORG","BEL","BAYERCROP","BATAINDIA",
           "BANKINDIA","BALKRISIND","ASTRAL","APOLLOTYRE","APOLLOHOSP",
           "AMARAJABAT","ALKEM","APLLTD","AJANTPHARM","ABFRL","ABCAPITAL","ADANIPOWER",
           "ADANIGREEN","ABBOTINDIA","AAVAS","AARTIIND","AUBANK","AIAENG","3MINDIA"]


def main():
    
    for ticker in tickers:
        try:
            ohlc = fetchOHLC(ticker, '3minute',5)
            ohlc_day = fetchOHLC(ticker, 'day',30) 
            ohlc_day = ohlc_day.iloc[:-1,:]       
            cp = candle_pattern(ohlc,ohlc_day,ticker) 
            
            
           
            print(ticker, ": ",cp) 
            
            
        except:
            print("skipping for ",ticker)
  

# Continuous execution        
starttime=time.time()
timeout = time.time() + 60*1*1  # 60 seconds times 60 meaning the script will run for 1 hr
while time.time() <= timeout:
    try:
        print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        main()
        time.sleep(180 - ((time.time() - starttime) % 180.0)) # 300 second interval between each new execution
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()
