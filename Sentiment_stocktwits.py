from Database.Manage_IA_database import Load_Dataset
import pandas as pd
import numpy as np

def get_global_sentiment(list):
    total_score=0
    for s in list:
        if s=='Bullish':
            total_score=total_score+1
        elif s=='Bearish':
            total_score=total_score-1
    return total_score

data=Load_Dataset()
# price_minutes=data.get_prices(symbol='AAPL',type_data='minutes')
# features=['Time','Open','Close','High','Volume','Low']
# price_minutes=price_minutes[features]
# price_minutes=price_minutes.sort_values(by=['Time'])
# price_minutes['minutes'] = price_minutes['Time'].apply(lambda x: x.time())
# price_minutes['date'] = price_minutes['Time'].apply(lambda x: x.date())
# # data['serial_number'] = np.linspace(0, len(data.values) - 1, len(data.values))
# data_final = pd.DataFrame(columns=['datetime', 'Open', 'Close', 'High', 'Low', 'Volume', 'serial_number'])
# for data_day in price_minutes.groupby(['date'], sort=True):
#     data_day = data_day[1]
#     print(data_day)
    #data_day['serial_number'] = np.linspace(0, len(data_day.values) - 1, len(data_day.values))
    #data_final = data_final.append(data_day)
#price_minutes['Time']=price_minutes['Time'].apply(lambda x: )
#print(price_minutes)
#price_days=data.get_prices(symbol='AAPL',type_data='days')
#print(price_days)
symbol='AAPL'
stocktwits=data.get_StockTwits(symbol=symbol)
features=['Time','sentiment']
stocktwits=stocktwits[features]
print(stocktwits)
news=stocktwits.sort_values(by=['Time'])
stocktwits['minutes'] = stocktwits['Time'].apply(lambda x: x.time())
stocktwits['date'] = stocktwits['Time'].apply(lambda x: x.date())
# # data['serial_number'] = np.linspace(0, len(data.values) - 1, len(data.values))
# data_final = pd.DataFrame(columns=['datetime', 'Open', 'Close', 'High', 'Low', 'Volume', 'serial_number'])
date,sentiment,pos_score,neg_score,naive_bayes=[],[],[],[],[]
for data_day in stocktwits.groupby(['date'], sort=True):
    date_val =data_day[0]
    print(data_day[0])
    data_day = data_day[1]
    print(data_day)
    score_sentiment = get_global_sentiment(data_day['sentiment'].values)
    #score_pos = data_day['pos_score'].mean()
    #score_neg = data_day['neg_score'].mean()
    #score_naive = get_global_sentiment(data_day['Naive_bayes_sentiment'].values)

    date.append(date_val)
    sentiment.append(score_sentiment)
    #pos_score.append(score_pos)
    #neg_score.append(score_neg)
    #naive_bayes.append(score_naive)

sentiment_dataframe=pd.DataFrame()
sentiment_dataframe['date']=date
#sentiment_dataframe['pos']=pos_score
#sentiment_dataframe['neg']=neg_score
sentiment_dataframe['sentiment']=sentiment
#sentiment_dataframe['naive_bayes']=naive_bayes


save_path='C:/Users/56979/PycharmProjects/DOW_JONES_BOTS/Analaysers_BOTS/Prepare_data_to_Analaysers/sentiment_stocktwits'
sentiment_dataframe.to_csv(save_path+'/{}.csv'.format(symbol))


