
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from stocktrends import Renko
import pandas as pd


#Moving Average
def MA(dataset,window, state ='Close'):
    # Create window days Moving Average
    dataset['ma{}'.format(window)] = dataset[state].rolling(window=window).mean()
    return dataset

#Exponencial Moving Average
def EMA(dataset, state='Close'):
    # Create Exponential moving average
    dataset['ema'] = dataset[state].ewm(com=0.5).mean()
    return dataset

def Momentum(dataset,n, state='Close'):
    M=pd.Series(dataset[state].diff(n),name='Momentum'+ str(n))
    dataset[M.name]=M
    #values=dataset.join(M)
    return dataset

#Rate of change
def ROC(dataset,n, state='Close'):
    M=dataset[state].diff(n-1)
    N=dataset[state].shift(n-1)
    ROC=pd.Series(M / N, name ='ROC_'+ str(n))
    dataset[ROC.name]=ROC

#Moving Average Convergence Divergence
#It is a trend following momentum indicator wich is calculated by taking the difference of two moving average of an asset price
#(typically 12 period MA and 26 period MA
#A signal line is also calculated wich is again a moving average (typically 9 period) of the MACD line calculated as per the above step
#The MACD line cutting the signal line from below signals bullish period and the former cutting the latter from above signals bearish. This is called crossover strategy
def MACD(DF,a,b,c,state='Close'):
    """function to calculate MACD
       typical values a = 12; b =26, c =9"""
    df = DF.copy()
    DF["MA_Fast"]=df[state].ewm(span=a,min_periods=a).mean()
    DF["MA_Slow"]=df[state].ewm(span=b,min_periods=b).mean()
    DF["MACD"]=DF["MA_Fast"]-DF["MA_Slow"]
    DF["Signal"]=DF["MACD"].ewm(span=c,min_periods=c).mean()
    DF.dropna(inplace=True)
    return DF

#Average True Range
#ATR takes in account the market movement each day in either direction and averaging the out.
# It focuses on total price movement and conveys how wildly the market is swingin as it moves
def ATR(DF,n,state='Close'):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df[state].shift(1))
    df['L-PC']=abs(df['Low']-df[state].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df.dropna(inplace=True)
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    DF['ATR']=df2['ATR']
    return df2

#Bollinger Bands
def BollBnd(DF,n,state='Close'):
    "function to calculate Bollinger Band"
    df = DF.copy()
    df["MA"] = df[state].rolling(n).mean()
    DF["BB_up"] = df["MA"] + 2*df[state].rolling(n).std(ddof=0) #ddof=0 is required since we want to take the standard deviation of the population and not sample
    DF["BB_dn"] = df["MA"] - 2*df[state].rolling(n).std(ddof=0) #ddof=0 is required since we want to take the standard deviation of the population and not sample
    DF["BB_width"] = DF["BB_up"] - DF["BB_dn"]
    DF.dropna(inplace=True)
    return DF

#Relative Strength Index
# Is a momentum oscilator wich measures the speed and change of price movements.RSI value oscilates between 0 and 100 with values above 70 indicates that assets has now reached overbougth territory
#Values below 30 signify oversold territory
def RSI(DF,n, state='Close'):
    "function to calculate RSI"
    df = DF.copy()
    df['delta']=df[state] - df[state].shift(1)
    df['gain']=np.where(df['delta']>=0,df['delta'],0)
    df['loss']=np.where(df['delta']<0,abs(df['delta']),0)
    avg_gain = []
    avg_loss = []
    gain = df['gain'].tolist()
    loss = df['loss'].tolist()
    for i in range(len(df)):
        if i < n:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == n:
            avg_gain.append(df['gain'].rolling(n).mean().tolist()[n])
            avg_loss.append(df['loss'].rolling(n).mean().tolist()[n])
        elif i > n:
            avg_gain.append(((n-1)*avg_gain[i-1] + gain[i])/n)
            avg_loss.append(((n-1)*avg_loss[i-1] + loss[i])/n)
    df['avg_gain']=np.array(avg_gain)
    df['avg_loss']=np.array(avg_loss)
    df['RS'] = df['avg_gain']/df['avg_loss']
    DF['RSI'] = 100 - (100/(1+df['RS']))
    DF.dropna(inplace=True)

    return df

# Calculating RSI without using loop
def rsi(df, n, state='Close'):
    "function to calculate RSI"
    delta = df[state].diff().dropna()
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


#Average directional index
#Is a way of measuring the strength of a trend
#Value range from 0 to 100 and quantify the strength of a trend as per below
#0-25 : Absent or weak trend
#25-50 strong trend
#50-75 very strong trend
#75-100 extremdly strong trend
#ADX no say nothing about the direction of the trend, only the strength.
def ADX(DF,n):
    "function to calculate ADX"
    df2 = DF.copy()
    df2['TR'] = ATR(df2,n)['TR'] #the period parameter of ATR function does not matter because period does not influence TR calculation
    df2['DMplus']=np.where((df2['High']-df2['High'].shift(1))>(df2['Low'].shift(1)-df2['Low']),df2['High']-df2['High'].shift(1),0)
    df2['DMplus']=np.where(df2['DMplus']<0,0,df2['DMplus'])
    df2['DMminus']=np.where((df2['Low'].shift(1)-df2['Low'])>(df2['High']-df2['High'].shift(1)),df2['Low'].shift(1)-df2['Low'],0)
    df2['DMminus']=np.where(df2['DMminus']<0,0,df2['DMminus'])
    TRn = []
    DMplusN = []
    DMminusN = []
    TR = df2['TR'].tolist()
    DMplus = df2['DMplus'].tolist()
    DMminus = df2['DMminus'].tolist()
    for i in range(len(df2)):
        if i < n:
            TRn.append(np.NaN)
            DMplusN.append(np.NaN)
            DMminusN.append(np.NaN)
        elif i == n:
            TRn.append(df2['TR'].rolling(n).sum().tolist()[n])
            DMplusN.append(df2['DMplus'].rolling(n).sum().tolist()[n])
            DMminusN.append(df2['DMminus'].rolling(n).sum().tolist()[n])
        elif i > n:
            TRn.append(TRn[i-1] - (TRn[i-1]/n) + TR[i])
            DMplusN.append(DMplusN[i-1] - (DMplusN[i-1]/n) + DMplus[i])
            DMminusN.append(DMminusN[i-1] - (DMminusN[i-1]/n) + DMminus[i])
    df2['TRn'] = np.array(TRn)
    df2['DMplusN'] = np.array(DMplusN)
    df2['DMminusN'] = np.array(DMminusN)
    df2['DIplusN']=100*(df2['DMplusN']/df2['TRn'])
    df2['DIminusN']=100*(df2['DMminusN']/df2['TRn'])
    df2['DIdiff']=abs(df2['DIplusN']-df2['DIminusN'])
    df2['DIsum']=df2['DIplusN']+df2['DIminusN']
    df2['DX']=100*(df2['DIdiff']/df2['DIsum'])
    ADX = []
    DX = df2['DX'].tolist()
    for j in range(len(df2)):
        if j < 2*n-1:
            ADX.append(np.NaN)
        elif j == 2*n-1:
            ADX.append(df2['DX'][j-n+1:j+1].mean())
        elif j > 2*n-1:
            ADX.append(((n-1)*ADX[j-1] + DX[j])/n)
    DF['ADX']=np.array(ADX)
    return df2


#On balance Volume
#Is a momentum indicator which uses changes in trading volume as an indicator of future assets price moves
#
def OBV(DF, state='Close'):
    """function to calculate On Balance Volume"""
    df = DF.copy()
    df['daily_ret'] = df[state].pct_change()
    df['direction'] = np.where(df['daily_ret']>=0,1,-1)
    df['direction'][0] = 0
    df['vol_adj'] = df['Volume'] * df['direction']
    DF['obv'] = df['vol_adj'].cumsum()
    return df

def slope(DF,n, state='Close'):
    "function to calculate the slope of regression line for n consecutive points on a plot"
    ser=DF[state]
    ser = (ser - ser.min())/(ser.max() - ser.min())
    x = np.array(range(len(ser)))
    x = (x - x.min())/(x.max() - x.min())
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y_scaled = ser[i-n:i]
        x_scaled = x[i-n:i]
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    df = DF.copy()
    df['Slope Angle']=slope_angle
    return df

#Renko chart is built using price movement and not price against standarized time intervals. This filter out the noise and lets you vizualise the true trend
#Price movements (fixed) are represented as bricked stacked as 45 degrees to each other.
# A new brick is added to the chart only when the price moves by a pre determined amount in either direction
#Renko chart have a time axis, but the time scale is not fixed. Some bricks may take longer to form tha others. Depending on how long it takesthe price
#to move the requiered box size
#typically is used closing price

def renko_DF(DF,n):
    "function to convert ohlc data into renko bricks"
    df = DF.copy()
    df.reset_index(inplace=True)
    df = df.iloc[:,[0,1,2,3,5,6]]
    df.rename(columns = {"Date" : "date", "High" : "high","Low" : "low", "Open" : "open","Adj Close" : "close", "Volume" : "volume"}, inplace = True)
    df2 = Renko(df)
    df2.brick_size = round(ATR(DF,n)["ATR"][-1],0)
    renko_df = df2.get_ohlc_data() #if using older version of the library please use get_bricks() instead
    return renko_df


def get_technical_indicator(DF):
    MA(DF,7)
    MA(DF,21)
    Momentum(DF,21)
    EMA(DF)
    MACD(DF,12,26,9)
    #Volatily Indicators
    ATR(DF,21)
    BollBnd(DF,21)
    #Extra
    RSI(DF,21)
    return DF


def plot_technical_indicators(dataset, last_days,company_name):
    plt.figure(figsize=(16, 10), dpi=100)
    dataset = dataset.iloc[-last_days:, :]
    x_ = list(dataset.index)

    # Plot first subplot
    plt.subplot(3, 1, 1)
    plt.plot(dataset['ma7'], label='MA 7', color='g', linestyle='--')
    plt.plot(dataset['Close'], label='Closing Price', color='b')
    plt.plot(dataset['ma21'], label='MA 21', color='r', linestyle='--')
    plt.plot(dataset['BB_up'], label='Upper Band', color='c')
    plt.plot(dataset['BB_dn'], label='Lower Band', color='c')
    plt.fill_between(x_, dataset['BB_dn'], dataset['BB_up'], alpha=0.35)
    plt.title('Technical indicators for {} - last {} days.'.format(company_name,last_days))
    plt.ylabel('USD')
    plt.legend()

    # Plot second subplot
    plt.subplot(3, 1, 2)
    plt.title('MACD')
    plt.plot(dataset['MACD'], label='MACD', linestyle='-.')
    plt.plot(dataset['Signal'],label='Signal')
    plt.plot(dataset['Momentum21'], label='Momentum', color='b', linestyle='-')

    plt.subplot(3,1,3)
    plt.plot(dataset['RSI'],label='RSI')
    plt.plot(dataset['obv'],label= 'OBV')
    #plt.plot(dataset['ADX'],label='ADX')

    plt.legend()
    plt.show()