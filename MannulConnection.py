from kiteconnect import KiteConnect
import pandas as pd

api_key = "0qtbn18ow3ic6v4j"
api_secret = "3hjb6gn3i1xzzgy2qcytqhsggs7kb0qk"
kite = KiteConnect(api_key=api_key)

print(kite.login_url())

request_token = "Nd7sakVWEvURxbnJgssfgtrZofHKPYcb"

data = kite.generate_session(request_token, api_secret = api_secret)

kite.set_access_token(data["access_token"])

instrument_dump = kite.instruments("NSE")