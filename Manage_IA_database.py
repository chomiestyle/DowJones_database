from Database.Manage_database import Manage_StockDatabase
from Database.Stock import Stock,Real_values,Bollinger_Band,Top_3_indicator,MACD_values,StockTwits,Real_values_days,StockTwits_preprocessed,Financial_News_preprocessed
#from Work.Technical_Analysis import BollBnd,MA,EMA,Momentum,MACD
import pandas as pd
from datetime import timedelta


def get_global_sentiment(list):
    total_score=0
    for s in list:
        if s=='Bullish':
            total_score=total_score+1
        elif s=='Bearish':
            total_score=total_score-1
    return total_score

class Load_Dataset():


    def __init__(self):

        self.StockData=Manage_StockDatabase()
        self.save_news_sentiment_dir_path = 'C:/Users/56979/PycharmProjects/DOW_JONES_BOTS/Analaysers_BOTS/Prepare_data_to_Analaysers/sentiment_news'
        self.save_stocktwits_sentiment_dir_path = 'C:/Users/56979/PycharmProjects/DOW_JONES_BOTS/Analaysers_BOTS/Prepare_data_to_Analaysers/sentiment_stocktwits'
        self.save_combined_news_price_path = 'C:/Users/56979/PycharmProjects/DOW_JONES_BOTS/Analaysers_BOTS/Prepare_data_to_Analaysers/combined_data'
        #self.NewsData=Manage_NewsDatabase()

    def get_prices(self, symbol,type_data):
        session=self.StockData.Session()
        stock=session.query(Stock).filter_by(name=symbol).first()
        if type_data=='days':
            prices=self.StockData.get_Stock_to_dataframe(stock=stock,Table_info=Real_values_days)
        elif type_data=='minutes':
            prices = self.StockData.get_Stock_to_dataframe(stock=stock, Table_info=Real_values)
        else:
            print('type_day invalido')
            return None
        session.close()
        return prices
    def get_StockTwits(self, symbol):
        session=self.StockData.Session()
        stock = session.query(Stock).filter_by(name=symbol).first()
        stocktwits_messages =self.StockData.get_Stock_to_dataframe(stock=stock,Table_info=StockTwits)
        session.close()
        return stocktwits_messages

    def get_Financial_news(self, symbol):
        session = self.StockData.Session()
        stock = session.query(Stock).filter_by(name=symbol).first()
        financial_news =self.StockData.get_Stock_to_dataframe(stock=stock,Table_info=Financial_News_preprocessed)
        session.close()
        return financial_news

    def Financial_news_sentiment_group(self,symbol):
        news = self.get_Financial_news(symbol=symbol)
        features = ['Publish datetime', 'sentiment title', 'sentiment summary', 'finbert sentiment summary',
                    'finbert sentiment title', 'finbert sentiment text']
        news = news[features]
        print(news)
        news = news.sort_values(by=['Publish datetime'])
        news['minutes'] = news['Publish datetime'].apply(lambda x: x.time())
        news['date'] = news['Publish datetime'].apply(lambda x: x.date())
        # # data['serial_number'] = np.linspace(0, len(data.values) - 1, len(data.values))
        # data_final = pd.DataFrame(columns=['datetime', 'Open', 'Close', 'High', 'Low', 'Volume', 'serial_number'])
        date, sentiment_title, sentiment_summary, finbert_sentiment_title, finbert_sentiment_summary, finbert_sentiment_text = [], [], [], [], [], []
        for data_day in news.groupby(['date'], sort=True):
            date_val = data_day[0]
            print(data_day[0])
            data_day = data_day[1]
            print(data_day)
            score_title = data_day['sentiment title'].mean()
            score_summary = data_day['sentiment summary'].mean()
            score_fin_text = data_day['finbert sentiment text'].mean()
            score_fin_title = data_day['finbert sentiment title'].mean()
            score_fin_summary = data_day['finbert sentiment summary'].mean()

            date.append(date_val)
            sentiment_title.append(score_title)
            sentiment_summary.append(score_summary)
            finbert_sentiment_title.append(score_fin_title)
            finbert_sentiment_text.append(score_fin_text)
            finbert_sentiment_summary.append(score_fin_summary)

        sentiment_dataframe = pd.DataFrame()
        sentiment_dataframe['title'] = sentiment_title
        sentiment_dataframe['summary'] = sentiment_summary
        sentiment_dataframe['fin_title'] = finbert_sentiment_title
        sentiment_dataframe['fin_summary'] = finbert_sentiment_summary
        sentiment_dataframe['fin_text'] = finbert_sentiment_text
        sentiment_dataframe['date'] = date


        sentiment_dataframe.to_csv(self.save_news_sentiment_dir_path + '/{}.csv'.format(symbol))
        return sentiment_dataframe

    def StockTwits_sentiment_group(self,symbol):
        stocktwits = self.get_StockTwits(symbol=symbol)
        features = ['Time', 'sentiment']
        stocktwits = stocktwits[features]
        print(stocktwits)
        news = stocktwits.sort_values(by=['Time'])
        stocktwits['minutes'] = stocktwits['Time'].apply(lambda x: x.time())
        stocktwits['date'] = stocktwits['Time'].apply(lambda x: x.date())
        # # data['serial_number'] = np.linspace(0, len(data.values) - 1, len(data.values))
        # data_final = pd.DataFrame(columns=['datetime', 'Open', 'Close', 'High', 'Low', 'Volume', 'serial_number'])
        date, sentiment, pos_score, neg_score, naive_bayes = [], [], [], [], []
        for data_day in stocktwits.groupby(['date'], sort=True):
            date_val = data_day[0]
            print(data_day[0])
            data_day = data_day[1]
            print(data_day)
            score_sentiment = get_global_sentiment(data_day['sentiment'].values)
            # score_pos = data_day['pos_score'].mean()
            # score_neg = data_day['neg_score'].mean()
            # score_naive = get_global_sentiment(data_day['Naive_bayes_sentiment'].values)

            date.append(date_val)
            sentiment.append(score_sentiment)
            # pos_score.append(score_pos)
            # neg_score.append(score_neg)
            # naive_bayes.append(score_naive)

        sentiment_dataframe = pd.DataFrame()
        sentiment_dataframe['date'] = date
        # sentiment_dataframe['pos']=pos_score
        # sentiment_dataframe['neg']=neg_score
        sentiment_dataframe['sentiment'] = sentiment
        # sentiment_dataframe['naive_bayes']=naive_bayes
        sentiment_dataframe.to_csv(self.save_stocktwits_sentiment_dir_path + '/{}.csv'.format(symbol))
        return sentiment_dataframe

    def combine_price_and_sentiment(self,symbol):
        self.StockTwits_sentiment_group(symbol=symbol)
        self.Financial_news_sentiment_group(symbol=symbol)
        price_days = self.get_prices(symbol=symbol, type_data='days')
        features = ['Time', 'Open', 'Close', 'High', 'Volume', 'Low']
        price_days = price_days[features]
        price_days = price_days.sort_values(by=['Time'])
        price_days['Time'] = price_days['Time'].apply(lambda x: x.date())
        sent_news = pd.read_csv(self.save_news_sentiment_dir_path + '/{}.csv'.format(symbol), index_col=6, parse_dates=True)
        print(sent_news)
        dataFrame_news = price_days.set_index('Time').join(sent_news)
        result_news = dataFrame_news.dropna()
        print(result_news)
        result_news.to_csv(self.save_combined_news_price_path + '/{}_news_prices.csv'.format(symbol))
        sent_stocktwits = pd.read_csv(self.save_stocktwits_sentiment_dir_path + '/{}.csv'.format(symbol), index_col=1,parse_dates=True)
        print(sent_stocktwits)
        dataFrame_stocktwits = price_days.set_index('Time').join(sent_stocktwits)
        result_stocktwits = dataFrame_stocktwits.dropna()
        print(result_stocktwits)
        result_stocktwits.to_csv(self.save_combined_news_price_path + '/{}_stocktwits_prices.csv'.format(symbol))

        return dataFrame_news,dataFrame_stocktwits

    def aggregate_StockTwits_price(self, symbol):
        """
            compile stocktwits data for stock prediction analysis in the following form
            (date, sentiment_calculated_bullish, sentiment_calculated_bearish, sentiment_actual_previous, tweet_volume_change, cash_volume, label)

            we have choice to take previous n days sentiment_calculated and using label of next nth day

            returns dataframes for AAPL, AMZN, GOOGL respectively
        """
        price_data = self.get_prices(symbol=symbol,type_data='days')
        dataStocktwits=self.get_StockTwits(symbol=symbol)
        dataStocktwits['Time'] = dataStocktwits['Time'].apply(lambda x: x.date())
        dataStocktwits.rename(columns={'Time': 'date'}, inplace=True)
        features=['date','Naive_bayes_sentiment','Message']
        dataStocktwits=dataStocktwits[features]
        dataStocktwits = dataStocktwits.groupby(['date', 'Naive_bayes_sentiment'], sort=True).count()
        print(dataStocktwits)
        combined_data = self.combine_price_and_sentiment(dataStocktwits, price_data)
        print('aca esta el combined data ')
        print(combined_data)

        return combined_data

    def get_stock_prediction_data(self, symbol='ALL', type='training'):

        """
            get the training and test data for stock prediction in format
            (sentiment_calculated_bullish, sentiment_calculated_bearish, sentiment_actual_previous,
            tweet_volume_change, cash_volume, label)

            Standardize the data before using.
        """
        if symbol=='ALL':
            tickers_list=self.StockData.session.query(Stock).all()
            combined_data=pd.DataFrame()
            for ticker in tickers_list:
                print(ticker)
                data_SYMBOL=self.aggregate_StockTwits_price(symbol=ticker.name)
                combined_data=combined_data.append(data_SYMBOL,ignore_index=True)
            data=combined_data

        else:

            data=self.aggregate_StockTwits_price(symbol=symbol)


        print(data)
        import numpy as np
        data.sort_values('date')
        data.drop(columns='date', inplace=True)
        data_training, data_test = np.split(data.sample(frac=1), [int(.9 * len(data))])
        if type=='training':
            return data_training

        elif type=='test':
            return data_test
        else:
            print('El type no es correcto')
            return
