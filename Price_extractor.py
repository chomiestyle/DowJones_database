
import yfinance as yf
from yahoo_fin.stock_info import *
#from yahoo_fin  import *

###obtengo valores de un stock  por minuto
def get_yfinance_m( stock, period):
    features = ['Open', 'High', 'Low', 'Close', 'Volume']
    val = yf.Ticker(stock)
    val_historical = val.history(period=period, interval="1m")
    return val_historical[features]

###obtengo valores de un stock  por dia
def get_yfinance_d( stock_name):
    features = ['open', 'high', 'low', 'close', 'volume','adjclose']
    #val = yf.Ticker(stock_name)
    #val_historical = val.history(period=max)
    val_historical=get_data(stock_name)
    #print(val_historical)
    return val_historical[features]



import pandas_datareader.data as web
import datetime

#start = datetime.datetime(2018, 1, 1).strftime('%Y-%m-%d')

#end = datetime.datetime(2020, 1, 1).strftime('%Y-%m-%d')


# try 'yahoo' if Google doesn't work. make sure to check the website mentioned above
# search QA forums if you have any issues on this, many questions have already been answered there!

def get_yahoo_data(Stock_name, start, end):
    Data = web.DataReader(Stock_name, 'yahoo', start, end)
    return Data


import quandl
#quandl.ApiConfig.api_key ='_5anjYuf9K7ypJ_e9p2N'
#data = quandl.get_table('ZACKS/FC', ticker='AAPL')
def get_quandl_data(Stock_name, start, end):
#mydata = quandl.get("EIA/PET_RWTC_D")
    mydata = quandl.get(Stock_name,start_date=start,end_date=end)
    return  mydata