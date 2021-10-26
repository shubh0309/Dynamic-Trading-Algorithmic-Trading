# Dynamic-Trading-Algorithmic-Trading

# We are login into Zerodha 
I am using Web scraping using Salenium to login into my kite zerodha account.and then generated a session for trading .

# We desinged stock scanner to scans stocks in the real time.
  While stock scanning we have tries to find candelstick pattern like Doji , Maru_Bozu , Hanging Man , Hammer , Shooting Star.<br />
  after finding the candelstick pattern we tries to find trend whether there is a bullish or bearish trend in the market.<br />
  after trend we analyse it with Simple Moving Average I have used 20 days MA and 200 days MA.<br />
  after this we tries to find whether the stock price is near Support or Ressistance.<br />
 
# After annalysing all this i have executed the order on stock
  while executing order i have to choose vanue to place order Like BSE or NSE.<br />
  after decideing the vanue i have to place order (long/short)<br />
  I also have to decide which type of order has to be placed like Intraday or Delivery.<br />
  After this i need to decied the quantity of the stock.<br />

# My BUY or SELL descision is based on 
  BUY -> Bullish candel stick pattern + bullish trend + candel near 20MA and 20MA is above 200MA.<br />
  SELL -> Bearish candel stick pattern + bearish trend + candel near 20MA and 20MA is below 200MA.<br />

# After order execution - sending message 
  after execution of order i am sending the message on mobile that your order has been executed on XYZ stock. using textbelt api.

# After placing order there will be two possibility
  Profit booking - profit booking at 2% its rigid<br />
  Loss book - loss booking at 1% its a rigid.<br />
  
