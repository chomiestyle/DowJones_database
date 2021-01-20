from Database.Manage_IA_database import Load_Dataset
import pandas as pd
import numpy as np

symbol='AAPL'
data=Load_Dataset()
data.combine_price_and_sentiment(symbol=symbol)