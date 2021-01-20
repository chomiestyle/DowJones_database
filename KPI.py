# =============================================================================
# Measuring the performance of a buy and hold strategy - CAGR
# Author : Mayank Rasu (http://rasuquant.com/wp/)

# Please report bug/issues in the Q&A section
# =============================================================================

# Import necesary libraries
import numpy as np
import yfinance as yf
import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import copy
import matplotlib.pyplot as plt


#daily data
def CAGR(DF,n_d):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    if n_d==12:
        ret='mon_ret'
    elif n_d==252:
        ret='daily_ret'
        df[ret] = DF["Adj Close"].pct_change()

    df["cum_return"] = (1 + df[ret]).cumprod()
    n = len(df)/n_d
    #CAGR = (df["cum_return"][-1])**(1/n) - 1
    CAGR = (df["cum_return"].tolist()[-1]) ** (1 / n) - 1
    return CAGR

#Volatility of a strategy is represented by the standard deviation of the returns
#This capture the variability of returns of the mean return
#Annualization is achived by multiplying volatility by square root of the annualization factor
#widely used measure of risk. However this aproach asumes normal distributions of returns wich is not true
#Does not capture tail risk

def volatility(DF,n_d):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    if n_d==12:
        ret='mon_ret'
    elif n_d==252:
        ret='daily_ret'
        df[ret] = DF["Adj Close"].pct_change()
    vol = df[ret].std() * np.sqrt(n_d)
    return vol


def sharpe(DF, rf,n_d):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df,n_d) - rf) / volatility(df,n_d)
    return sr


def sortino(DF, rf,n_d):
    "function to calculate sortino ratio ; rf is the risk free rate"
    if n_d==12:
        ret='mon_ret'
    elif n_d==252:
        ret='daily_ret'
    df = DF.copy()
    df[ret] = DF["Adj Close"].pct_change()
    df["neg_ret"] = np.where(df[ret] < 0, df[ret], 0)
    neg_vol = df["neg_ret"].std() * np.sqrt(252)
    sr = (CAGR(df,n_d) - rf) / neg_vol
    return sr


def max_dd(DF,n_d):
    "function to calculate max drawdown"
    df = DF.copy()
    if n_d==12:
        ret='mon_ret'
    elif n_d==252:
        ret='daily_ret'
        df[ret] = DF["Adj Close"].pct_change()

    df["cum_return"] = (1 + df[ret]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"] / df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd


def calmar(DF,n_d):
    "function to calculate calmar ratio"
    df = DF.copy()
    clmr = CAGR(df,n_d) / max_dd(df,n_d)
    return clmr
