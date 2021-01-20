import  Database.Data_manage_SQLalchemy as db
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from Database.Stock import Real_values, StockTwits,Real_values_days,StockTwits_preprocessed,Fundamental_information,Financial_News_Finbert_preprocessed

from Prices_extractor.Price_extractor import *
from StockTwits.StockTwits_extractor import *
from StockTwits.StockTwits_preprocesses import *
from Work.Technical_Analysis import *
from Fundamental_Analisis.FinBERT.predict import finbert_prediction
import random
import pytz

##StockTwits data functions
#from Fundamental_Analysis.load_data import LoadData, get_stocktwits_preprocessed_table
# from Fundamental_Analisis.sentiment_analysis import SentimentAnalysis
#
# from sklearn.externals import joblib
import datetime
import feedparser
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import time
from Database.Stock import Stock,Financial_News,Financial_News_preprocessed
from Financial_News.Web_scrapping.StockNEWS.Scrapper import goose_article_information,full_scrap_finviz,full_scrap_NASDAQ,raw_scraper
from Financial_News.news_preprocessing import get_score

## Clase para manejar una base de datos
class Manage_StockDatabase():

    def __init__(self):
        self.engine = db.engine
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.Base = declarative_base()
        # 2 - generate database schema
        self.Base.metadata.create_all(self.engine)



    def Real_values_days(self,stock):
        prices=self.session.query(Real_values_days).filter_by(stock=stock).all()
        if len(prices)==0:
             self.create_StockDatabase_1d(stock=stock)
        else:

            if stock.last_day == None :
                dataframe = self.get_Stock_to_dataframe(stock=stock, Table_info=Real_values_days, index=['Time'])
                last_day=dataframe.tail(1).index[0]
                print(last_day)
                stock.last_day=last_day
                self.session.commit()

            self.update_prices_yahoo_1d(stock=stock)

    ## Crea una base de datos de un indice en particular (probado con el Down Jones)
    def create_StockDatabase_1m(self,list_stocks):
        session=self.Session()
        for ticker in list_stocks:
            new_stock = Stock(ticker)
            prices = get_yfinance_m(new_stock.name, '7d')
            prices.dropna(inplace=True)
            if prices.empty:
                print('no hay valores en {}'.format(ticker))
                continue
            cont = 0
            # all_real_value=[]
            for time in prices.index:
                # print(time)
                row = prices.iloc[cont]
                Open = row['Open']
                Close = row['Close']
                High = row['High']
                Volume = row['Volume']
                Low = row['Low']
                values = Real_values_days(new_stock)
                values.add_value(time=time, open=Open, close=Close, high=High, low=Low, volume=Volume)
                session.add(values)
                cont += 1
                new_stock.last_time = time
                session.add(new_stock)
                session.commit()
        session.close()

    ## Crea una base de datos con intervalos de 1 dia de un indice en particular (probado con el Down Jones)
    def create_StockDatabase_1d(self,stock):
        session = self.Session()
        #new_stock = stock
        prices = get_yfinance_d(stock.name)
        print(prices)
        prices.dropna(inplace=True)
        if prices.empty:
            print('no hay valores en {}'.format(stock.name))
            return
        # all_real_value=[]
        cont=0
        for day in prices.index:
            # print(time)
            row = prices.iloc[cont]
            Open = row['open']
            Close = row['close']
            High = row['high']
            Volume = row['volume']
            Low = row['low']
            Adjclose=row['adjclose']
            values = Real_values_days(stock)
            values.add_value(time=day, open=Open, close=Close, high=High, low=Low, volume=Volume,adjclose=Adjclose)
            local_object = session.merge(values)
            session.add(local_object)
            session.commit()
            if cont==[len(prices.index)-1]:
                session2 = self.Session()
                # print(last_update_time_datetime)
                stock2 = session2.query(Stock).filter_by(name=stock.name).first()
                stock2.last_day = day
                session2.commit()
                session2.close()
            #session.add(values)
            cont += 1
            #session.add(new_stock)

        session.close()
        return


## funcion que actualiza los valores de los precios por minuto desde yahoo finance
    def update_prices_yahoo(self,stock):
        print(stock.name)
        prices = get_yfinance_m(stock.name, '7d')
        if prices.empty:
            return
        prices.dropna(inplace=True)
        prices_last=prices.tail(2)
        print(prices_last)
        if len(prices_last)<2:
            last_yahoo_time = prices_last.index[0]
        else:
            last_yahoo_time=prices_last.index[1]
        last_yahoo_time_string = last_yahoo_time.strftime("%Y-%m-%d %H:%M:%S")
        last_yahoo_time_datetime = datetime.datetime.strptime(last_yahoo_time_string, "%Y-%m-%d %H:%M:%S")

        #cont = 0
        last_time_string = stock.last_time.strftime("%Y-%m-%d %H:%M:%S")
        last_time= datetime.datetime.strptime(last_time_string, "%Y-%m-%d %H:%M:%S")

        print(last_yahoo_time_datetime)
        print(last_time)
        self.fill_prices(t1=last_time,t2=last_yahoo_time_datetime,stock=stock,prices=prices)
        last_update_time = prices_last.index[0]
        last_update_time_string = last_update_time.strftime("%Y-%m-%d %H:%M:%S")
        last_update_time_datetime = datetime.datetime.strptime(last_update_time_string, "%Y-%m-%d %H:%M:%S")
        print('new last update')
        session=self.Session()
        print(last_update_time_datetime)
        stock2=session.query(Stock).filter_by(name=stock.name).first()
        stock2.last_time=last_update_time_datetime
        session.commit()
        session.close()

    def update_prices_yahoo_1d(self,stock):
        print(stock.name)
        prices = get_yfinance_d(stock.name)
        if prices.empty:
            return
        prices.dropna(inplace=True)
        prices_last=prices.tail(2)
        print(prices_last)
        if len(prices_last)<2:
            last_yahoo_time = prices_last.index[0]
        else:
            last_yahoo_time=prices_last.index[1]
        last_yahoo_time_string = last_yahoo_time.strftime("%Y-%m-%d %H:%M:%S")
        last_yahoo_time_datetime = datetime.datetime.strptime(last_yahoo_time_string, "%Y-%m-%d %H:%M:%S")

        #cont = 0
        last_time_string = stock.last_day.strftime("%Y-%m-%d %H:%M:%S")
        last_time= datetime.datetime.strptime(last_time_string, "%Y-%m-%d %H:%M:%S")

        print(last_yahoo_time_datetime)
        print(last_time)
        self.fill_prices_1d(t1=last_time,t2=last_yahoo_time_datetime,stock=stock,prices=prices)
        last_update_time = prices_last.index[0]
        last_update_time_string = last_update_time.strftime("%Y-%m-%d %H:%M:%S")
        last_update_time_datetime = datetime.datetime.strptime(last_update_time_string, "%Y-%m-%d %H:%M:%S")
        print('new last update')
        session=self.Session()
        print(last_update_time_datetime)
        stock2=session.query(Stock).filter_by(name=stock.name).first()
        stock2.last_day=last_update_time_datetime
        session.commit()
        session.close()

    def fill_holes(self,stock):
        session = self.Session()
        dataframe= pd.read_sql(session.query(Real_values).filter_by(stock=stock).statement, con=self.engine)
        session.close()
        for val in dataframe.index:
            if val < len(dataframe.index) - 1:
                time = dataframe.iloc[val]['Time']
                next_time = dataframe.iloc[val + 1]['Time']
                difference = next_time.minute - time.minute
                if difference > 1:
                    prices = get_yfinance_m(stock.name, '7d')
                    self.fill_prices(t1=time, t2=next_time, stock=stock,prices=prices)
            else:
                print('ultimo valor')
    def fill_prices(self,t1, t2, stock,prices):

        cont1 = 0
        cont_t1 = 0
        cont_t2 = 0
        for date in prices.index:
            time_string = date.strftime("%Y-%m-%d %H:%M:%S")
            date_val = datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
            if date_val == t1:
                cont_t1 = cont1
            if date_val == t2:
                cont_t2 = cont1
            cont1 += 1
        hole = prices.iloc[cont_t1:cont_t2]
        cont=0
        session = self.Session()
        for time in hole.index:
            time_string = time.strftime("%Y-%m-%d %H:%M:%S")
            t_value = datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
            lastest = max((t1, t_value))  # Si es t1, significa que no es necesario agregar
            if lastest == t_value and lastest!=t1:
                row=hole.iloc[cont]
                Open = row['Open']
                Close = row['Close']
                High = row['High']
                Volume = row['Volume']
                Low = row['Low']
                values = Real_values(stock)
                values.add_value(time=t_value, open=Open, close=Close, high=High, low=Low, volume=Volume)
                local_object = session.merge(values)
                session.add(local_object)
                session.commit()
            cont+=1
        session.close()

    def fill_prices_1d(self,t1, t2, stock,prices):
        cont1 = 0
        cont_t1 = 0
        cont_t2 = 0
        for date in prices.index:
            time_string = date.strftime("%Y-%m-%d %H:%M:%S")
            date_val = datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
            if date_val == t1:
                cont_t1 = cont1
            if date_val == t2:
                cont_t2 = cont1
            cont1 += 1
        hole = prices.iloc[cont_t1:cont_t2]
        #print(hole)
        cont=0
        session = self.Session()
        for time in hole.index:
            time_string = time.strftime("%Y-%m-%d %H:%M:%S")
            t_value = datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
            lastest = max((t1, t_value))  # Si es t1, significa que no es necesario agregar
            if lastest == t_value and lastest!=t1:
                row=hole.iloc[cont]
                Open = row['open']
                Close = row['close']
                High = row['high']
                Volume = row['volume']
                Low = row['low']
                Adjclose=row['adjclose']
                values_days = Real_values_days(stock)
                values_days.add_value(time=t_value, open=Open, close=Close, high=High, low=Low, volume=Volume,adjclose=Adjclose)
                local_object = session.merge(values_days)
                session.add(local_object)
                session.commit()
            cont+=1
        session.close()

    def delete_repeted_values(self,stock):
        session=self.Session()
        prices=session.query(Real_values).filter_by(stock=stock)
        for p in prices:
            repeted=session.query(Real_values).filter_by(stock=stock).filter_by(Time=p.Time).filter_by(Open=p.Open).filter_by(Close=p.Close).filter_by(High=p.High).filter_by(Low=p.Low).all()
            c=0
            if len(repeted)>1:
                first=True
                for r in repeted:
                    if first:
                        r.repr()
                        first=False
                    else:
                        r.repr()
                        local_object = session.merge(r)
                        session.delete(local_object)
                        session.commit()
                        c+=1
            print('Elimino {} precios'.format(c))
        session.close()
    def export_1d_data(self,save_dir):
        import numpy as np
        import os
        session=self.Session()
        stocks=session.query(Stock).all()
        for stock in stocks:
            data=self.get_Stock_to_dataframe(stock=stock,Table_info=Real_values_days)
            data=data[['Time','Open','Close','High','Low','Volume','AdjClose']]
            data=data.sort_values(by=['Time'])
            data=data.drop_duplicates(subset=['Time'])
            data=data.rename(columns={'Time':'Date'})
            data['serial_number']=np.linspace(0,len(data.values)-1,len(data.values))
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
            file_name='{}.csv'.format(stock.name)
            save_path = os.path.join(save_dir, file_name)
            data.to_csv(save_path)
        session.close()



    def export_1m_data(self,path_dir,n_val=None):
        import numpy as np
        session=self.Session()
        stocks=session.query(Stock).all()
        for stock in stocks:
            stock.repr()
            data=self.get_Stock_to_dataframe(stock=stock,Table_info=Real_values)
            data=data[['Time','Open','Close','High','Low','Volume']]
            data=data.sort_values(by=['Time'])
            data=data.drop_duplicates(subset=['Time'])
            #data['Time']=data['Time'].apply(lambda x: )
            #print(data['Time'].values)
            data=data.rename(columns={'Time':'datetime'})
            data['minutes'] = data['datetime'].apply(lambda x: x.time())
            data['date'] = data['datetime'].apply(lambda x: x.date())
            #data['serial_number'] = np.linspace(0, len(data.values) - 1, len(data.values))
            data_final=pd.DataFrame(columns=['datetime','Open','Close','High','Low','Volume','serial_number'])
            for data_day in data.groupby(['date'], sort=True):
                data_day=data_day[1]
                data_day['serial_number']=np.linspace(0, len(data_day.values) - 1, len(data_day.values))
                data_final=data_final.append(data_day)
            if n_val!=None:
                data_final=data_final.tail(n_val)
            #print(data_final['serial_number'])
            data_final.to_csv(path_dir+'/{}.csv'.format(stock.name))

    def export_1m_AT_data(self):

            session = self.Session()
            stocks = session.query(Stock).all()
            for stock in stocks:
                stock.repr()
                data = self.get_Stock_to_dataframe(stock=stock, Table_info=Real_values)
                data = data[['Time', 'Open', 'Close', 'High', 'Low', 'Volume']]
                data = data.sort_values(by=['Time'])
                data = data.drop_duplicates(subset=['Time'])
                ###ADD Technical inciators
                data=get_technical_indicator(DF=data)
                print(data)
                data = data.rename(columns={'Time': 'datetime'})
                data['minutes'] = data['datetime'].apply(lambda x: x.time())
                data['date'] = data['datetime'].apply(lambda x: x.date())
                # data['serial_number'] = np.linspace(0, len(data.values) - 1, len(data.values))
                data_final = pd.DataFrame(
                    columns=['datetime', 'Open', 'Close', 'High', 'Low', 'Volume', 'serial_number'])
                for data_day in data.groupby(['date'], sort=True):
                    data_day = data_day[1]
                    data_day['serial_number'] = np.linspace(0, len(data_day.values) - 1, len(data_day.values))
                    data_final = data_final.append(data_day)
                data_final.to_csv(
                    'C:/Users/56979/PycharmProjects/TradingGym/trading_env/test/data/1minute_data/DOWJONES/AT_data/{}.csv'.format(
                        stock.name))




#Convierte  una tabla de sql en dataframe (pensada para tener la tabla stock de la base de datos y luego poder iterar en todos los stocks dentro de esa base
#Para nuestro caso table_name puede ser stock o Real_value por ahora

    def sql_to_dataframe(self,table_name='Stock'):
        table_df = pd.read_sql_table(table_name,con=self.engine,index_col='stock_id')
        return table_df


#Entrega un dataframe de un stock en particular, solo necesita el nombre del stock y una session de la base de datos
    def get_Stock_to_dataframe(self,stock,Table_info,start=datetime.datetime(1900, 1, 30, 0, 0, 0),end=datetime.datetime.now(),index=None):
            session = self.Session()
            #stock=session.query(Stock).filter(Stock.name == stock).first()

            if index==None:
                stock_pd= pd.read_sql(session.query(Table_info).filter(Table_info.stock_id == stock.id).statement, con=self.engine)
            else:
                stock_pd = pd.read_sql(session.query(Table_info).filter(Table_info.stock_id == stock.id).statement, con=self.engine,index_col=index)
            session.close()
            return stock_pd



    def input_gaphs(self,stock_name,start_time,end_time):
        pd = self.get_Stock_to_dataframe(stock_name=stock_name, start=start_time, end=end_time)
        pd = pd.sort_values('Time')
        cont = 0
        candle_stick = []
        volume=[]
        for val in pd.index:
            row = pd.iloc[cont]
            time = row['Time']
            time_string = time.strftime("%Y-%m-%d %H:%M:%S")
            open = row['Open']
            high = row['High']
            close = row['Close']
            low = row['Low']
            vol = row['Volume']
            dicc = {'t': time_string, 'o': open, 'h': high, 'l': low, 'c': close}
            candle_stick.append(dicc)
            volume.append(vol)
            cont += 1
        return candle_stick,volume





#
# ###StockTwits Tables#############################
    def get_prev_StockTwits_from_db(self,stock):
        session = self.Session()
        prev_messages = []
        for m in session.query(StockTwits).filter_by(stock=stock).all():
            prev_messages.append(m.message_id)
        session.close()
        return prev_messages

    def get_fresh_new_Twits(self,stock):
        print('entro al get refresh')
        old_data = self.get_prev_StockTwits_from_db(stock)
        twits,Time_out=extractor(old_messages_id=old_data,SYMBOL=stock.name)
        if not twits.empty:
            ##Add new Twits to database
            utc = pytz.UTC
            session_twits=self.Session()
            for i in twits.index:
                message=twits.iloc[i]
                message_time = message['datetime']
                message_id = message['message_id']
                dt = datetime.datetime.strptime(message_time, "%Y-%m-%dT%H:%M:%SZ")
                dt = dt.replace(tzinfo=utc)
                twits_message = StockTwits(stock=stock)
                sentiment=message['sentiment']
                twits_message.add_sentiment(sentiment=sentiment)
                text = message['message']
                text_array = text.split()
                text2 = ' '
                for a in text_array:
                    s = a.encode('utf-8')
                    #print(s)
                    v = s.decode("utf-8", errors="replace").replace("\x00", "\uFFFD")
                    #print(v)
                    text2 = text2 + ' ' + v
                user = message['user']
                twits_message.add_value(time=dt, user=int(user), message=text2, message_id=int(message_id))
                local_object = session_twits.merge(twits_message)
                session_twits.add(local_object)
                # StockTwits Preprocessing
                message = clean2(message=text2)
                message_preprocessed = StockTwits_preprocessed(stock=stock)
                message_preprocessed.add_value(time=dt, message=message, user=int(user),
                                               message_id=int(message_id),
                                               sentiment=sentiment)

                # message_preprocessed.add_sentiment_score(sentiment_score=score)
                message_preprocessed.repr()
                # message_preprocessed.add_naive_bayes_sentiment(naive_sentiment=naive)
                local_object_2 = session_twits.merge(message_preprocessed)
                session_twits.add(local_object_2)
                # local_object2 = session.merge(m)
                local_object.preprocessed = True
                session_twits.commit()
            session_twits.close()
        return twits,Time_out

    def Delete_repeted_StockTwits_preprocesses(self):
        from sqlalchemy import func,and_
        print('Elimina los StockTwits preprocesados que  estan repetido')
        #Table = StockTwits
        session=self.Session()
        # helper subquery: find first row (by primary key) for each unique date
        subq = (session.query(StockTwits_preprocessed.message_id, func.min(StockTwits_preprocessed.id).label("min_id")).group_by(StockTwits_preprocessed.message_id)).subquery('message_id_min_id')
        sq = (session.query(StockTwits_preprocessed.id).join(subq, and_(StockTwits_preprocessed.message_id == subq.c.message_id,StockTwits_preprocessed.id != subq.c.min_id) )).subquery("subq")
        dq = (session.query(StockTwits_preprocessed).filter(StockTwits_preprocessed.id.in_(sq))).delete(synchronize_session=False)
        session.commit()
        session.close()

    def Delete_repeted_StockTwits(self):
        from sqlalchemy import func,and_
        print('Elimina StockTwits  repetidos')
        #Table = StockTwits
        session=self.Session()
        # helper subquery: find first row (by primary key) for each unique date
        subq = (session.query(StockTwits.message_id, func.min(StockTwits.id).label("min_id")).group_by(StockTwits.message_id)).subquery('message_id_min_id')
        sq = (session.query(StockTwits.id).join(subq, and_(StockTwits.message_id == subq.c.message_id,StockTwits.id != subq.c.min_id) )).subquery("subq")
        dq = (session.query(StockTwits).filter(StockTwits.id.in_(sq))).delete(synchronize_session=False)
        session.commit()
        session.close()



    def Repeted_StockTwits(self,stock,time_out):
        print('checkea si esta repetido')
        #Table = StockTwits
        session=self.Session()
        StockTwit=session.query(StockTwits).filter_by(stock=stock).filter(StockTwits.exist_one==None).all()
        print(len(StockTwit))
        contador=0
        timeout = time.time() + time_out  # execute_time seconds times
        for m in StockTwit:
            #m.repr()
            if time.time() <= timeout:
                repeated=session.query(StockTwits).filter_by(stock=stock).filter_by(message_id=m.message_id).all()
                local_object = session.merge(m)
                if len(repeated)==1:

                    local_object.exist_one = True
                else:
                    local_object.exist_one = False

                session.commit()
                contador+=1

            else:
                session.close()
                return len(StockTwit)-contador
        session.close()
        return len(StockTwit)-contador

    def delete_repeted_StockTwits(self,stock):
        print('Entra al delete')
        session=self.Session()
        Twits=session.query(StockTwits).filter_by(stock=stock).filter_by(exist_one=False).all()
        print(len(Twits))
        for m in Twits:
            array=session.query(StockTwits).filter_by(stock=stock).filter_by(Time=m.Time).filter_by(User=m.User).filter_by(Message=m.Message).filter_by(message_id=m.message_id).all()
            print(len(array))
            first=True
            cont=0
            for sm in array:
                if first:
                    sm.repr()
                    local_object = session.merge(sm)
                    local_object.exist_one=True
                    session.commit()
                    first=False
                else:
                    local_object2 = session.merge(sm)
                    session.delete(local_object2)
                    session.commit()
                    cont+=1
            print('elimino {}'.format(cont))

    def check_Preprocesses_StockTwits(self,stock,time_out):
        print('checkea si esta preprocesado')
        session=self.Session()
        StockTwit=session.query(StockTwits).filter_by(stock=stock).filter(StockTwits.preprocessed!=True).all()
        print(len(StockTwit))
        timeout = time.time() + time_out  # execute_time seconds times
        contador=0
        for m in StockTwit:
            if time.time() <= timeout:
                preprocesses=session.query(StockTwits_preprocessed).filter_by(stock=stock).filter_by(message_id=m.message_id).all()
                print(len(preprocesses))
                local_object = session.merge(m)
                local_object.repr()
                if len(preprocesses)==0:
                    print('Este es false')
                    local_object.preprocessed = False
                else:
                    local_object.preprocessed = True
                session.commit()
                contador+=1
            else:
                session.close()
                return len(StockTwit)-contador
        session.close()
        return len(StockTwit)-contador

    def labelled_StockTwits(self):
        session=self.Session()
        Twits_pd = pd.read_sql(session.query(StockTwits).filter(StockTwits.sentiment!=None).statement, con=self.engine)
        stocks=pd.read_sql(session.query(Stock).statement,con=self.engine,index_col=['id'])
        stocks_name=stocks['name'].sort_index()
        feature=['message_id','Message','sentiment','stock_id']
        Twits_pd=Twits_pd[feature]
        file_csv_location = 'C:/Users/56979/PycharmProjects/Fundamental_Analisis/StockTwits_classifiers/All_labelled_data/DowJones_labelled_data.csv'
        feature=['message_id','Message','sentiment','stock_id']
        Twits_pd=Twits_pd[feature]
        # for m in Twits_pd['stock_id'].values:
        #     print(m)
        #     print(stocks_name.iloc[m-1])
        # print('se acabo ')
        Twits_pd['stock_id']=Twits_pd['stock_id'].apply(lambda x:stocks_name.iloc[x-1] )
        Twits_pd.to_csv(file_csv_location)

        Twits_pd.to_csv(file_csv_location)
        session.close()
        return Twits_pd



    def Preprocess_Stocktwits(self,stock):
        print('Entra al preprocess')
        session=self.Session()
        StockTwits_messages=session.query(StockTwits).filter_by(stock=stock).filter_by(preprocessed=False).all()
        print(len(StockTwits_messages))
        for m in StockTwits_messages:
                #print('se proprosesa')
                time = m.Time
                message = m.Message
                message=clean2(message=message)
                ####Sentiment score####
                #score=get_sentiword_score(message=message)
                ####Naive Sentiment
                #naive=tweet_classifier.predict([message])
                #naive=naive[0]
                user = int(m.User)
                sentiment = m.sentiment
                message_id = int(m.message_id)
                message_preprocessed = StockTwits_preprocessed(stock=stock)
                message_preprocessed.add_value(time=time, message=message, user=user,
                                                   message_id=message_id,
                                                   sentiment=sentiment)

                #message_preprocessed.add_sentiment_score(sentiment_score=score)
                #message_preprocessed.repr()
                #message_preprocessed.add_naive_bayes_sentiment(naive_sentiment=naive)
                local_object = session.merge(message_preprocessed)
                m.preprocessed=True
                session.add(local_object)
                session.commit()
        session.close()

        return

    def export_sentiment_stocktwits(self,stock,dir_path):
            data = self.get_Stock_to_dataframe(stock=stock, Table_info=StockTwits_preprocessed)
            data = data[['datetime','sentiment title','sentiment summary','finbert sentiment summary','finbert sentiment title','finbert sentiment text']]
            #data = data.drop_duplicates(subset=['title'])
            data.to_csv(dir_path+'/{}.csv'.format(stock.name))


####Financial news #########
    def add_Financial_new(self,new_data_list, stock):
        print('entra a guardar')
        print(new_data_list.index)
        for i in new_data_list.index:
            new_data=new_data_list.iloc[i]
            #print(new_data)
            guid = new_data['guid']
            published = new_data['published']
            summary = new_data['summary']
            split_summary = str(summary).split(' ')
            title = new_data['title']
            text = new_data['text']
            split_text = str(text).split(' ')
            if len(split_summary) < 2 or len(split_text) < 2:
                print('sale por falta de summary o texto ')
                continue

            source = new_data['fuente']
            url = new_data['url']
            p_date = new_data['p_date']
            image = new_data['image']
            keywords = new_data['keywords']
            if type(keywords) == float or keywords == '':
                keywords = ['No', 'keywords']
            session=self.Session()
            exist_new = session.query(Financial_News).filter_by(stock=stock).filter_by(text=text).filter_by(
                         title=title).filter_by(url=url).filter_by(summary=summary).all()
            #exist_new=[]
            print(len(exist_new))
            if len(exist_new) != 0:
                print('esta wea ya existia ')
                continue
            else:
                new = Financial_News(stock=stock)

                new.add_value(guid=guid, published=published, summary=summary, title=title, text=text, source=source,
                                      url=url, image=image, p_date=p_date)
                sentiment_summary = new_data['sentiment_summary']
                sentiment_title = new_data['sentiment_title']
                new.add_sentiment(sentiment_title=sentiment_title, sentiment_summary=sentiment_summary)
                new.add_keywords(keywords)
                new.repr()
                local_object = session.merge(new)
                session.add(local_object)
                #session.add(new)
                session.commit()
                session.close()
        return

    def read_YAHOO(self, stock):

            session=self.Session()
            yahoo_old_news= pd.read_sql(session.query(Financial_News).filter_by(stock=stock).filter(Financial_News.guid!='No_guid').statement,con=self.engine)
            #source_page='https://finance.yahoo.com'
            YAHOO_URL = 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=%s&region=US&lang=en-US'
            # """Download VADER"""
            try:
                nltk.data.find('vader_lexicon')
            except LookupError:
                nltk.download('vader_lexicon', quiet=True)

            ##Busca en Yahoo finance
            while True:
                try:
                    feed = feedparser.parse(YAHOO_URL % stock.name)
                    break
                except Exception as ex:
                    print(ex.args)
                    ##Web scrapping method ### Sirve para que parezca mas humano scraper
                    time_request = random.randint(0, 50)
                    print('DORMIRA POR {} SEGUNDOS'.format(time_request))
                    time.sleep(time_request)

            yahoo_news=pd.DataFrame(columns=['guid','author','title','published','text','summary','keywords','image','fuente','url','p_date','sentiment_summary','sentiment_title'])
            for entry in feed.entries:
                if entry.guid in yahoo_old_news['guid'].values:
                    print('Esta noticia de yahoo ya existe')
                    continue

                info = goose_article_information(tmp=entry.link)
                if info==None:
                    continue
                """Find url and skip if exists"""

                if len(info['keywords'])==0 or len(info['author'])==0 or  info['image']==None:
                        #url_article = entry.link
                        image,keywords,author = raw_scraper(info['url'],memoize=False)
                        if keywords!=None:
                            if len(keywords)>0:
                                print(keywords)
                                info['keywords']=keywords
                        if image!=None:
                            info['image']=image


                        if author!=None:
                            if len(author)>0:
                                info['author']=author

                """Analyze the sentiment"""
                sia = SentimentIntensityAnalyzer()
                _summary = sia.polarity_scores(entry.summary)['compound']
                _title = sia.polarity_scores(entry.title)['compound']

                """Parse the date"""
                p_date = '%s_%s' % (stock.name,
                                        datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S +0000').strftime(
                                            "%Y-%m-%d"))
                new_data = {'guid': entry.guid,
                                'author': info['author'],
                                'title': entry.title,
                                'published': entry.published,
                                'text': info['text'],
                                'summary': entry.summary,
                                'keywords': info['keywords'],
                                'image': info['image'],
                                'fuente': info['fuente'],
                                'url': info['url'],
                                'p_date': p_date,
                                'sentiment_summary': _summary,
                                'sentiment_title': _title}

                data = pd.DataFrame([new_data])
                yahoo_news = yahoo_news.append(data, ignore_index=True)

                #yahoo_news.append(new_data)
            self.add_Financial_new(new_data_list=yahoo_news, stock=stock)
            ###Cierro session para no molestar
            session.close()

    def read_finviz(self,stock):
            session=self.Session()
            finviz_old_news= pd.read_sql(session.query(Financial_News).filter_by(stock=stock).filter(Financial_News.guid =='No_guid').statement,con=self.engine)
            finviz_old_news2 = pd.read_sql(
                session.query(Financial_News).filter_by(stock=stock).filter(Financial_News.guid == 'No_guid_finviz').statement,con=self.engine)
            #print(finviz_old_news)
            # """Download VADER"""
            try:
                 nltk.data.find('vader_lexicon')
            except LookupError:
                    nltk.download('vader_lexicon', quiet=True)
            cont=0
            articles = full_scrap_finviz(stock_name=stock.name)
            finviz_news=pd.DataFrame(columns=['guid','author','title','published','text','summary','keywords','image','fuente','url','p_date','sentiment_summary','sentiment_title'])
            for link in articles:
                if link in finviz_old_news['url'].values:
                    old_new=session.query(Financial_News).filter_by(url=link).first()
                    if old_new.guid=='No_guid':
                        old_new.guid='No_guid_finviz'
                        session.commit()
                    print('Esta noticia de finviz ya esta en la base de datos')
                    continue
                if link in finviz_old_news2['url'].values:
                    #old_new=session.query(Financial_News).filter_by(url=link).first()
                    #if old_new.guid=='No_guid':
                    #    old_new.guid='No_guid_finviz'
                    #    session.commit()
                    print('Esta noticia de finviz ya esta en la base de datos')
                    continue
                print(link)
                info = goose_article_information(tmp=link)
                if info ==None:
                    continue
                    ###Cierro session para no molestar
                if len(info['keywords'])==0 or len(info['author'])==0 or  info['image']==None :
                        #url_article = entry.link
                        image,keywords,author = raw_scraper(info['url'],memoize=False)
                        if keywords!=None:
                            if len(keywords)>0:
                                print(keywords)
                                info['keywords']=keywords
                        if image!=None:
                            info['image']=image
                        if author!=None:
                            if len(author)>0:
                                info['author']=author

                summary = info['summary']
                title = info['title']
                published = info['published']
                """Analyze the sentiment"""
                sia = SentimentIntensityAnalyzer()
                _summary = sia.polarity_scores(summary)['compound']
                _title = sia.polarity_scores(title)['compound']
                # strftime
                """Parse the date"""
                p_date = '{}_%{}'.format(stock.name, str(published))
                new_data = {'guid': 'No_guid_finviz',
                                'author': info['author'],
                                'title': title,
                                'published': published,
                                'text': info['text'],
                                'summary': summary,
                                'keywords': info['keywords'],
                                'image': info['image'],
                                'fuente': info['fuente'],
                                'url': info['url'],
                                'p_date': p_date,
                                'sentiment_summary': _summary,
                                'sentiment_title': _title}
                data=pd.DataFrame([new_data])
                finviz_news=finviz_news.append(data,ignore_index=True)
            self.add_Financial_new(new_data_list=finviz_news, stock=stock)
            session.close()

    def read_nasdaq(self, stock):
        session = self.Session()
        nasdaq_old_news = pd.read_sql(
            session.query(Financial_News).filter_by(stock=stock).filter(Financial_News.guid == 'No_guid').statement,
            con=self.engine)
        nasdaq_old_news2 = pd.read_sql(
            session.query(Financial_News).filter_by(stock=stock).filter(
                Financial_News.guid == 'No_guid_nasdaq').statement, con=self.engine)
        # print(finviz_old_news)
        # """Download VADER"""
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)

        articles = full_scrap_NASDAQ(stock=stock.name,MAX_VALUE=100)
        nasdaq_news = pd.DataFrame(columns=['guid','author','title','published','text','summary','keywords','image','fuente','url','p_date','sentiment_summary','sentiment_title'])
        for link in articles:
            if link in nasdaq_old_news['url'].values:
                old_new = session.query(Financial_News).filter_by(url=link).first()
                if old_new.guid == 'No_guid':
                    old_new.guid = 'No_guid_nasdaq'
                    session.commit()
                print('Esta noticia de nasdaq.com ya esta en la base de datos')
                continue
            if link in nasdaq_old_news2['url'].values:
                print('Esta noticia de nasdaq.com ya esta en la base de datos')
                continue
            info = goose_article_information(tmp=link)
            if info == None:
                print('No se puede sacar nada del articulo')
                continue

            ###Cierro session para no molestar
            if len(info['keywords']) == 0 or len(info['author']) == 0 or info['image'] == None:
                # url_article = entry.link
                image, keywords, author = raw_scraper(info['url'], memoize=False)
                if keywords != None:
                    if len(keywords) > 0:
                        print(keywords)
                        info['keywords'] = keywords
                if image != None:
                    info['image'] = image

                if author != None:
                    if len(author) > 0:
                        info['author'] = author

            summary = info['summary']
            title = info['title']
            published = info['published']
            """Analyze the sentiment"""
            sia = SentimentIntensityAnalyzer()
            _summary = sia.polarity_scores(summary)['compound']
            _title = sia.polarity_scores(title)['compound']
            # strftime
            """Parse the date"""
            p_date = '{}_%{}'.format(stock.name, str(published))
            new_data = {'guid': 'No_guid',
                        'author': info['author'],
                        'title': title,
                        'published': published,
                        'text': info['text'],
                        'summary': summary,
                        'keywords': info['keywords'],
                        'image': info['image'],
                        'fuente': info['fuente'],
                        'url': info['url'],
                        'p_date': p_date,
                        'sentiment_summary': _summary,
                        'sentiment_title': _title}
            data = pd.DataFrame([new_data])
            nasdaq_news = nasdaq_news.append(data, ignore_index=True)

        self.add_Financial_new(new_data_list=nasdaq_news, stock=stock)
        session.close()
    def add_datetime_news(self):
        import arrow
        dict_mese = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',
                     'July': '07', 'Aug': '08', 'Sep': '09', 'Sept': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        session = self.Session()
        stocks = session.query(Stock).all()
        print('\n### All Stocks:')
        file = open('Total_news.txt', 'w')
        file.write('Symbol : Cantidad \n')
        for stock in stocks:
            stock.repr()
            news = session.query(Financial_News).filter_by(stock=stock).filter_by(datetime_published=None).all()
            for n in news:
                try:
                    date_split = n.published.split(',')
                    if len(date_split) == 1:
                        date_time_str = date_split[0]
                        utc = arrow.get(date_time_str)

                    elif len(date_split) == 2:
                        d2 = date_split[0].split(' ')
                        if len(d2) >= 2:
                            d1 = date_split[1].split(' ')
                            if len(d1) <= 4:
                                año = d1[1]
                                hora = d1[2]
                                try:
                                    match = re.search('AM', hora)
                                    s = match.start()
                                    e = match.end()
                                    # print('Found "{}"\nin "{}"\nfrom {} to {} ("{}")'.format(
                                    #     match.re.pattern, match.string, s, e, hora[s:e]))
                                    hora = hora[0:s]
                                except:
                                    match = re.search('PM', hora)
                                    s = match.start()
                                    e = match.end()
                                    # print('Found "{}"\nin "{}"\nfrom {} to {} ("{}")'.format(
                                    #     match.re.pattern, match.string, s, e, hora[s:e]))
                                    hora = hora[0:s]
                                    hora_split = hora.split(':')
                                    hora_12 = int(hora_split[0]) + 12
                                    if hora_12 >= 24:
                                        hora_12 = int(hora_split[0])
                                    hora = str(hora_12) + ':' + hora_split[1]
                                # print('año:{}, hora:{}'.format(año,hora))
                                # print(d2)
                                mes = dict_mese[d2[0]]
                                dia = d2[1]
                                # print('mes: {} , dia: {}'.format(mes,dia))
                                # date_time_str = '2018-06-29 08:15:27.243860'
                                date_time_str = año + '-' + mes + '-' + dia + ' ' + hora
                                # utc = arrow.get(date_time_str)
                                # print(date_time_str)
                                # date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
                                date = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
                                utc = arrow.get(date)
                            else:
                                # print('except')
                                # print(d2)
                                # print(d1)
                                año = d1[1]
                                hora = d1[2]
                                m_t = d1[3]
                                # print(m_t)
                                if m_t == 'pm':
                                    # print(m_t)
                                    # print(d1)
                                    hora_split = hora.split(':')
                                    hora_12 = int(hora_split[0]) + 12
                                    if hora_12 >= 24:
                                        hora_12 = int(hora_split[0])
                                    hora = str(hora_12) + ':' + hora_split[1]
                                # print(año)
                                # print(hora)
                                dia = d2[1]
                                mes = d2[0].strip('.')
                                mes = dict_mese[mes]
                                # print(mes)
                                date_time_str = año + '-' + mes + '-' + dia + ' ' + hora
                                # print(date_time_str)
                                # utc = arrow.get(date_time_str)
                                datetime_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
                                utc = arrow.get(datetime_obj)

                        else:
                            # print('segundo except')
                            second_split = date_split[1].split(' ')
                            # print(second_split)
                            dia = second_split[1]
                            mes = second_split[2]
                            mes = dict_mese[mes]
                            año = second_split[3]
                            hora = second_split[4]
                            date_time_str = año + '-' + mes + '-' + dia + ' ' + hora
                            utc = arrow.get(date_time_str)

                except:
                    print('este except')
                    print(n.published)
                    if n.published != None:
                        #print(date_split)
                        second_split = date_split[0].split(':')
                        #print(second_split)
                        tercer_split = second_split[1].split(' ')
                        #print(tercer_split)
                        cuarto_split = tercer_split[1].split('.')
                        #print(cuarto_split)
                        mes = cuarto_split[0]
                        mes = dict_mese[mes]
                        dia = tercer_split[2]
                        quinto_split = date_split[1].split(' ')
                        año = quinto_split[1]
                        hora = quinto_split[3]
                        m_t = quinto_split[4]
                        #print(m_t)
                        if m_t == 'p.m.':
                            # print(d1)
                            hora_split = hora.split(':')
                            hora_12 = int(hora_split[0]) + 12
                            if hora_12 >= 24:
                                hora_12 = int(hora_split[0])
                            hora = str(hora_12) + ':' + hora_split[1]
                        date_time_str = año + '-' + mes + '-' + dia + ' ' + hora
                        date = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
                        utc = arrow.get(date)
                        # time.sleep(3)
                    else:
                        continue
                date_time_obj = utc.to('America/New_York')
                print(date_time_obj.datetime)
                n.datetime_published=date_time_obj.datetime
                session.commit()
        session.close()
    def Finbert_preprocess_news(self,stock,start):
        #import csv
        print('Entra al preprocess')
        session = self.Session()
        News = session.query(Financial_News).filter_by(stock=stock).filter(Financial_News.datetime_published>=start).all()
        Finbert_dataframe = pd.read_sql(session.query(Financial_News_Finbert_preprocessed).statement,con=self.engine)
        print(len(News))
        for m in News:
            new_id = m.id
            if new_id in Finbert_dataframe['financial_new_id'].values:
                continue
            print('se preprosesa')
            #time = m.datetime_published
            text = m.text
            title=m.title
            summary = m.summary
            text_result,summary_result,title_result=finbert_prediction(text=text,summary=summary,title=title)
            finbert_preprocesse=Financial_News_Finbert_preprocessed(financial_new=m)
            #print(finbert_preprocesse.financial_new_id)
            title_save_path='C:/Users/56979/PycharmProjects/DOW_JONES_BOTS/Preprocessing_BOTS/News/news_preprocesses/title.csv'
            summary_save_path = 'C:/Users/56979/PycharmProjects/DOW_JONES_BOTS/Preprocessing_BOTS/News/news_preprocesses/summary.csv'
            text_save_path = 'C:/Users/56979/PycharmProjects/DOW_JONES_BOTS/Preprocessing_BOTS/News/news_preprocesses/text.csv'
            title_result.to_csv(title_save_path)
            summary_result.to_csv(summary_save_path)
            text_result.to_csv(text_save_path)
            try:
                file_title = open(title_save_path, "r")
                title_lines=file_title.readlines()
                print(title_lines)
                file_summary = open(summary_save_path, "r")
                summary_lines = file_summary.readlines()
                print(summary_lines)
                file_text = open(text_save_path, "r")
                text_lines = file_text.readlines()
                print(text_lines)
                finbert_preprocesse.add_value(summary=summary_lines, title=title_lines, text=text_lines)
                session.commit()
            except:
                continue

        session.close()

        return

    def add_Financial_new_preprocessed(self):
        print('Entra al get_new_score')
        session = self.Session()
        News_preprocess = session.query(Financial_News_Finbert_preprocessed).all()
        Financial_new_preprocessed_dataframe = pd.read_sql(session.query(Financial_News_preprocessed).statement, con=self.engine)
        print(Financial_new_preprocessed_dataframe['id'].values)
        #print(len(News_preprocess))
        for new in News_preprocess:
            #print('entra al loop')
            new_id=new.financial_new_id
            if new_id in Financial_new_preprocessed_dataframe['id'].values:
                continue
            financial_new=session.query(Financial_News).filter_by(id=new_id).first()
            if financial_new!=None:
                #financial_new.repr()
                time=financial_new.datetime_published
                #print(time)
                title_list=new.sentiment_title
                summary_list=new.sentiment_summary
                text_list=new.sentiment_text
                if title_list!=None and summary_list!=None and text_list!=None:
                    title_score,summary_score,text_score=get_score(title_list=title_list,text_list=text_list,summary_list=summary_list)
                    preprocess_new=Financial_News_preprocessed(stock=financial_new.stock)
                    preprocess_new.add_value(id=new_id,guid=financial_new.guid,published=time,summary=financial_new.summary,title=financial_new.title,text=financial_new.text,source=financial_new.source,url=financial_new.url)
                    preprocess_new.add_sentiment(sentiment_title=financial_new.sentiment_title,sentiment_summary=financial_new.sentiment_summary)
                    preprocess_new.add_keywords(list=financial_new.keywords)
                    preprocess_new.add_finbert_sentiment(sentiment_summary=summary_score,sentiment_title=title_score,sentiment_text=text_score)
                    session.commit()


        session.close()


    def export_sentiment_news(self,stock,dir_path):
            data = self.get_Stock_to_dataframe(stock=stock, Table_info=Financial_News_preprocessed)
            data = data[['datetime','sentiment title','sentiment summary','finbert sentiment summary','finbert sentiment title','finbert sentiment text']]
            #data = data.drop_duplicates(subset=['title'])
            data.to_csv(dir_path+'/{}.csv'.format(stock.name))




    def add_Fundamental_information(self,new_data, stock):
        Fundamental = Fundamental_information(stock=stock)
        name=str(new_data['Name'].values[0])
        print(str(name))
        sector=str(new_data['Sector'].values[0])
        # #sector = new_data['Sector']
        price = float(new_data['Price'].values[0])
        price_earnings = float(new_data['Price/Earnings'].values[0])
        dividend_yields = float(new_data['Dividend Yield'].values[0])
        earnings_share = float(new_data['Earnings/Share'].values[0])
        week_52_low = float(new_data['52 Week Low'].values[0])
        week_52_high = float(new_data['52 Week High'].values[0])
        marketcap = float(new_data['Market Cap'].values[0])
        ebitda = float(new_data['EBITDA'].values[0])
        price_sales = float(new_data['Price/Sales'].values[0])
        price_book = float(new_data['Price/Book'].values[0])
        sec_filings = str(new_data['SEC Filings'].values[0])
        Fundamental.add_value(name=name,sector=sector,price=price,
                               price_earnings=price_earnings,
                               dividend_yield=dividend_yields,
                               earnings_share=earnings_share,weak52_low=week_52_low,
                               weak52_high=week_52_high,market_cap=marketcap,ebitda=ebitda,
                               price_sales=price_sales,price_book=price_book,sec_filings_url=sec_filings)
        self.session.add(Fundamental)
        Fundamental.repr()
        self.session.commit()
        return

# #####Manage Financial_News Database##########################
# class Manage_NewsDatabase():
#     def __init__(self):
#         self.engine = db.engine_webscrapping_latest_news
#         self.Session = sessionmaker(bind=self.engine)
#         self.session = db.Session_webscrapping_latest_news()
#         self.Base = db.Base_webscraping_latest_news
#         # 2 - generate database schema
#         self.Base.metadata.create_all(self.engine)
#
#     def update(self,df, letter_name, section=None):
#         temp = []
#         for i in range(len(df)):
#             row = df.iloc[i, :]
#             title = row['title']
#             link = row['link']
#             image = row['image']
#             full_text = row['Text']
#             date = row['Dates']
#             summary = row['summary']
#             key_words = row['keywords']
#             author = row['Author']
#             news = self.session.query(Financial_News).filter_by(Title=title).first()
#             if news != None:
#                 print('esta noticia ya esta en la base de datos ')
#                 # if news.media_source.section == None and section != None:
#                 #     newsletter_media = self.session.query(Media_Source).filter_by(
#                 #         name=letter_name).filter_by(section=section).first()
#                 #     if newsletter_media == None:
#                 #         newsletter_media = Media_Source(name=letter_name, section=section)
#                 #         self.session.add(newsletter_media)
#                 #     news.media_source = newsletter_media
#                 #     self.session.commit()
#                 #     #news.repr()
#                 continue
#             newsletter_media = self.session.query(Media_Source).filter_by(name=letter_name).filter_by(
#                     section=section).first()
#             if newsletter_media == None:
#                 newsletter_media = Media_Source(name=letter_name, section=section)
#                 self.session.add(newsletter_media)
#             new = Financial_News(media_source=newsletter_media)
#             new.add_value(link=link, title=title, image=image, date=date, summary=summary, text=full_text)
#             new.add_key_words_value(keywords=key_words)
#             new.add_author(autor=author)
#             #new.repr()
#             self.session.add(new)
#             self.session.commit()
#             temp.append(i)
#             print('Updating...')
#
#         if temp:
#             output = df.loc[[i for i in temp]]
#             output.reset_index(inplace=True, drop=True)
#             add_value = True
#         else:
#             output = pd.DataFrame()
#             output['title'] = ['No updates yet.']
#             output['link'] = output['image'] = output['Text'] = output['Dates'] = output['summary'] = ['']
#             add_value = False
#
#         return output, add_value
#
#
#
#
#     def finish_connection(self):
#         self.session.close()



