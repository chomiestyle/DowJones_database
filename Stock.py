import  Database.Data_manage_SQLalchemy as db
from sqlalchemy import Column, Integer, String, Float,Table,ForeignKey,REAL, DateTime,TEXT,BOOLEAN
from sqlalchemy.orm import relationship

class Real_values_days(db.Base):
    __tablename__ = 'Real_values_days'

    id = Column(Integer, primary_key=True)
    Time = Column('Time',DateTime,nullable=True)
    Open = Column('Open',REAL,nullable=True)
    Close=Column('Close',REAL,nullable=True)
    High = Column('High',REAL,nullable=True)
    Low = Column('Low',REAL,nullable=True)
    Volume = Column('Volume',REAL,nullable=True)
    Adjclose = Column('AdjClose',REAL,nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="Real_prices_days")

    def __init__(self,stock):
        self.stock=stock

    def add_value(self,time,open,close,high,low,volume,adjclose):
        self.Time=time
        self.Open=open
        self.Close=close
        self.High=high
        self.Low=low
        self.Volume=volume
        self.Adjclose=adjclose

    def repr(self):
        print('Time: {} Open: {} Close: {} High: {} Low : {} Volume :{}'.format(self.Time,self.Open,self.Close,self.High,self.Low,self.Volume))


class Real_values(db.Base):
    __tablename__ = 'Real_values'

    id = Column(Integer, primary_key=True)
    Time = Column('Time',DateTime,nullable=True)
    Open = Column('Open',REAL,nullable=True)
    Close=Column('Close',REAL,nullable=True)
    High = Column('High',REAL,nullable=True)
    Low = Column('Low',REAL,nullable=True)
    Volume = Column('Volume',REAL,nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="Real_prices")

    def __init__(self,stock):
        self.stock=stock

    def add_value(self,time,open,close,high,low,volume):
        self.Time=time
        self.Open=open
        self.Close=close
        self.High=high
        self.Low=low
        self.Volume=volume

    def repr(self):
        print('Time: {} Open: {} Close: {} High: {} Low : {} Volume :{}'.format(self.Time,self.Open,self.Close,self.High,self.Low,self.Volume))

class Predictions_LSTM_1step(db.Base):
    __tablename__ = 'Predictions_LSTM_1step_values'

    id = Column(Integer, primary_key=True)
    Time = Column('Time',DateTime,nullable=True)
    Open = Column('Open',REAL,nullable=True)
    Close=Column('Close',REAL,nullable=True)
    High = Column('High',REAL,nullable=True)
    Low = Column('Low',REAL,nullable=True)
    Volume = Column('Volume',REAL,nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="Predictions_LSTM_1step_prices")

    def __init__(self,stock):
        self.stock=stock

    def add_value(self,time,open,close,high,low,volume):
        self.Time=time
        self.Open=open
        self.Close=close
        self.High=high
        self.Low=low
        self.Volume=volume

    def repr(self):
        print('Time: {} Open: {} Close: {} High: {} Low : {} Volume :{}'.format(self.Time,self.Open,self.Close,self.High,self.Low,self.Volume))

class Bollinger_Band(db.Base):
    __tablename__ = 'Bollinger_Band'

    id = Column(Integer, primary_key=True)
    Time = Column('Time', DateTime, nullable=True)
    BB_UP= Column('BB_UP', REAL, nullable=True)
    BB_DOWN = Column('BB_DOWN', REAL, nullable=True)
    BB_WIDTH = Column('BB_WIDTH', REAL, nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="Bollinger_bands")

    def __init__(self, stock):
        self.stock = stock

    def add_value(self, time, bb_up, bb_down, bb_width):
        self.Time = time
        self.BB_UP = bb_up
        self.BB_DOWN = bb_down
        self.BB_WIDTH = bb_width

    def repr(self):
        print('Time: {} bollinger up: {} bollinger down: {} bollinger width: {} '.format(self.Time, self.BB_UP, self.BB_DOWN,self.BB_WIDTH))
class MACD_values(db.Base):
    __tablename__ = 'MACD_values'

    id = Column(Integer, primary_key=True)
    Time = Column('Time', DateTime, nullable=True)
    MA_FAST= Column('MA_Fast', REAL, nullable=True)
    MA_SLOW= Column('MA_Slow', REAL, nullable=True)
    MACD= Column('MACD', REAL, nullable=True)
    Signal= Column('Signal', REAL, nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="MACD_value")

    def __init__(self, stock):
        self.stock = stock

    def add_value(self, time, ma_fast, ma_slow, macd,signal):
        self.Time = time
        self.MA_FAST = ma_fast
        self.MA_SLOW = ma_slow
        self.MACD = macd
        self.Signal = signal

    def repr(self):
        print('Time: {} MA FAST: {} MA SLOW: {} MACD: {}  Signal : {}'.format(self.Time, self.MA_FAST, self.MA_SLOW,self.MACD,self.Signal))

class Top_3_indicator(db.Base):
    __tablename__ = 'Top_3_indicator'

    id = Column(Integer, primary_key=True)
    Time = Column('Time', DateTime, nullable=True)
    MA= Column('MA', REAL, nullable=True)
    EMA= Column('EMA', REAL, nullable=True)
    MOMENTUM= Column('MOMENTUM', REAL, nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="Top_3_indicators")

    def __init__(self, stock):
        self.stock = stock

    def add_value(self, time, ma, ema, momentum):
        self.Time = time
        self.MA = ma
        self.EMA = ema
        self.MOMENTUM = momentum

    def repr(self):
        print('Time: {} MA : {} EMA: {} MOMENTUM: {}'.format(self.Time, self.MA, self.EMA,self.MOMENTUM))



class StockTwits(db.Base):
    __tablename__ = 'StockTwits'

    id = Column(Integer, primary_key=True)
    message_id = Column('message_id', Integer)
    Time = Column('Time', DateTime, nullable=True)
    #Time_zone=Column('Time_zone',DateTime)
    Message= Column('Message', TEXT, nullable=True)
    User= Column('User_id',Integer,nullable=True)
    sentiment=Column('sentiment',String, nullable=True)
    preprocessed=Column('Preprocessed',BOOLEAN,nullable=True)
    exist_one=Column('exist_one',BOOLEAN,nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="Messages_Stocktwits")

    def __init__(self, stock):
        self.stock = stock

    def add_value(self, time,message,user,message_id):
        self.Time = time
        self.Message = message
        self.User = user
        self.message_id=message_id

    def add_sentiment(self,sentiment):
        self.sentiment=sentiment
    def add_proprocessed(self,bool):
        self.preprocessed=bool

    def repr(self):
        print('Time: {} '.format(self.Time))
        print('Id : {}'.format(self.id))
        print('Twitter count : {}'.format(self.User))
        print('Message id: {}'.format(self.message_id))
        print('New : {}'.format(self.Message))
        print('Sentiment : {}'.format(self.sentiment))

class StockTwits_preprocessed(db.Base):
    __tablename__ = 'StockTwits_preprocessed'

    id = Column(Integer, primary_key=True)
    message_id = Column('message_id', Integer, nullable=True)
    Time = Column('Time', DateTime, nullable=True)
    Message= Column('Message', TEXT, nullable=True)
    User= Column('User_id',Integer,nullable=True)
    sentiment=Column('sentiment',String, nullable=True)
    sentiment_positive=Column('pos_score',Float,nullable=True)
    sentiment_negative=Column('neg_score', Float, nullable=True)
    naive_bayes_classifier=Column('Naive_bayes_sentiment',String,nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="Messages_Stocktwits_preproccesed")

    def __init__(self, stock):
        self.stock = stock

    def add_value(self, time,message,user,message_id,sentiment):
        self.Time = time
        self.Message = message
        self.User = user
        self.message_id=message_id
        self.sentiment=sentiment
    def add_sentiment_score(self, sentiment_score):
        self.sentiment_positive=float(sentiment_score[0])
        self.sentiment_negative=float(sentiment_score[1])

    def add_naive_bayes_sentiment(self,naive_sentiment):
        self.naive_bayes_classifier=naive_sentiment

    def repr(self):
        print('Time: {} '.format(self.Time))
        print('Twitter count : {}'.format(self.User))
        print('Message id: {}'.format(self.message_id))
        print('New : {}'.format(self.Message))
        print('Sentiment : {}'.format(self.sentiment))
        print('pos sentiment : {} neg sentiment : {}  '.format(self.sentiment_positive,self.sentiment_negative))
        print('Naive bayes sentiment : {}'.format(self.naive_bayes_classifier))

class Financial_News(db.Base):
    __tablename__ = 'Financial_News'

    id = Column(Integer, primary_key=True)
    guid = Column('guid', String)
    published = Column('published', String, nullable=True)
    datetime_published=Column('Publish datetime',DateTime,nullable=True)
    summary= Column('summary', TEXT, nullable=True)
    title= Column('title',TEXT,nullable=True)
    text=Column('text',TEXT,nullable=True)
    source=Column('source',TEXT,nullable=True)
    url=Column('url',TEXT,nullable=True)
    image=Column('Image',TEXT,nullable=True)
    p_date=Column('p_date',TEXT,nullable=True)
    keywords=Column('keywords',String)
    sentiment_title=Column('sentiment title',Float, nullable=True)
    sentiment_summary=Column('sentiment summary',Float, nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="Financial_new")
    Finbert_preprocessed = relationship('Financial_News_Finbert_preprocessed', uselist=True, back_populates='financial_new')

    def __init__(self, stock):
        self.stock = stock

    def add_value(self, guid,published,summary,title,text,source,url,image,p_date):
        self.guid = guid
        self.published = published
        self.summary = summary
        self.title=title
        self.text=text
        self.source=source
        self.url=url
        self.image=image
        self.p_date=p_date


    def add_sentiment(self,sentiment_title,sentiment_summary):
        self.sentiment_title= sentiment_title
        self.sentiment_summary= sentiment_summary

    def add_datetime_published(self,datetime):
        self.datetime_published=datetime
    def add_keywords(self,list):
        #keywords=[]
        #for word in list:
        #    print(word)
        #    keywords.append(word)
        #print(keywords)
        self.keywords=list


    def repr(self):
        print('Time: {} '.format(self.published))
        print('Id : {}'.format(self.id))
        print('Title : {}'.format(self.title))
        print('Summary: {}'.format(self.summary))
        print('published: {}'.format(self.published))
        print('Sentiment title : {}'.format(self.sentiment_title))
        print('Sentiment summary: {}'.format(self.sentiment_summary))





class Financial_News_preprocessed(db.Base):
    __tablename__ = 'Financial_News_preprocessed'

    id = Column(Integer, primary_key=True)
    guid = Column('guid', String)
    #published = Column('published', String, nullable=True)
    datetime=Column('Publish datetime',DateTime,nullable=True)
    summary= Column('summary', TEXT, nullable=True)
    title= Column('title',TEXT,nullable=True)
    text=Column('text',TEXT,nullable=True)
    source=Column('source',TEXT,nullable=True)
    url=Column('url',TEXT,nullable=True)
    keywords=Column('keywords',String)
    sentiment_title=Column('sentiment title',Float, nullable=True)
    sentiment_summary=Column('sentiment summary',Float, nullable=True)
    finbert_sentiment_title = Column('finbert sentiment title', Float, nullable=True)
    finbert_sentiment_summary = Column('finbert sentiment summary', Float, nullable=True)
    finbert_sentiment_text = Column('finbert sentiment text', Float, nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="Financial_new_preprocessed")

    def __init__(self, stock):
        self.stock = stock

    def add_value(self,id, guid,published,summary,title,text,source,url):
        self.id=id
        self.guid = guid
        self.datetime = published
        self.summary = summary
        self.title=title
        self.text=text
        self.source=source
        self.url=url

    def add_sentiment(self,sentiment_title,sentiment_summary):
        self.sentiment_title= sentiment_title
        self.sentiment_summary= sentiment_summary

    def add_finbert_sentiment(self,sentiment_title,sentiment_summary,sentiment_text):
        self.finbert_sentiment_title= sentiment_title
        self.finbert_sentiment_summary= sentiment_summary
        self.finbert_sentiment_text = sentiment_text


    def add_keywords(self,list):
        self.keywords=list


    def repr(self):
        print('Time: {} '.format(self.published))
        print('Id : {}'.format(self.id))
        print('Title : {}'.format(self.title))
        print('Summary: {}'.format(self.summary))
        print('published: {}'.format(self.published))
        print('Sentiment title : {}'.format(self.sentiment_title))
        print('Sentiment summary: {}'.format(self.sentiment_summary))

class Financial_News_Finbert_preprocessed(db.Base):
    __tablename__ = 'Financial_News_Finbert_preprocessed'

    id = Column(Integer, primary_key=True)
    sentiment_title=Column('sentiment title',TEXT, nullable=True)
    sentiment_summary=Column('sentiment summary',TEXT, nullable=True)
    sentiment_text=Column('sentiment text',TEXT, nullable=True)
    financial_new_id = Column(Integer, ForeignKey('Financial_News.id'))
    financial_new = relationship("Financial_News", back_populates="Finbert_preprocessed")

    def __init__(self, financial_new):
        self.financial_new = financial_new

    def add_value(self,summary,title,text):

        self.sentiment_summary = summary
        self.sentiment_title=title
        self.sentiment_text=text



    def repr(self):
        print('Sentiment title : {}'.format(self.sentiment_title))
        print('Sentiment summary: {}'.format(self.sentiment_summary))

class Stock(db.Base):
    __tablename__ = 'Stock'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    last_time = Column(DateTime, nullable=True)
    last_day=Column(DateTime, nullable=True)
    last_StockTwits_message_id = Column(Integer, default=None)
    last_StockTwits_message_time=Column(DateTime,default=None)
    Real_prices= relationship("Real_values", uselist=True, back_populates="stock")
    Real_prices_days = relationship("Real_values_days", uselist=True, back_populates="stock")
    Predictions_LSTM_1step_prices = relationship("Predictions_LSTM_1step", uselist=True, back_populates="stock")
    Bollinger_bands=relationship('Bollinger_Band', uselist=True, back_populates='stock')
    MACD_value=relationship('MACD_values',uselist=True,back_populates='stock')
    Top_3_indicators=relationship('Top_3_indicator',uselist=True,back_populates='stock')
    Messages_Stocktwits = relationship('StockTwits', uselist=True, back_populates='stock')
    Messages_Stocktwits_preproccesed = relationship('StockTwits_preprocessed', uselist=True, back_populates='stock')
    Trainning_data = relationship('Trainning_Table', uselist=True, back_populates='stock')
    Financial_new=relationship('Financial_News', uselist=True, back_populates='stock')
    Financial_new_preprocessed=relationship('Financial_News_preprocessed', uselist=True, back_populates='stock')
    Fundamental_information = relationship('Fundamental_information', uselist=True, back_populates='stock')
    def __init__(self,name):
        self.name=name

    def repr(self):
        print('El Stock en cuestion es : {}'.format(self.name))
        print('El ultimo valor de actualizacion es : {}'.format(self.last_time))
        print('El ultimo tiempo de actualizacion para stocktwits es : {}'.format(self.last_StockTwits_message_time))


class Fundamental_information(db.Base):
    __tablename__ = 'Fundamental_information'

    id = Column(Integer, primary_key=True)
    name = Column('Name', String)
    sector = Column('Sector', String, nullable=True)
    price = Column('Price', REAL, nullable=True)
    price_earnings = Column('Price/Earnings', REAL, nullable=True)
    dividend_yield = Column('Dividend Yield', REAL, nullable=True)
    earnings_share = Column('Earnings/share', REAL, nullable=True)
    weak52_low = Column('52 Week Low', REAL, nullable=True)
    weak52_high = Column('52 Week High', REAL, nullable=True)
    market_cap=Column('Market Cap', REAL, nullable=True)
    ebitda = Column('EBITDA', REAL, nullable=True)
    price_sales = Column('Price sales', REAL, nullable=True)
    price_book = Column('Price/book', REAL, nullable=True)
    sec_filing_url=Column('SEC filings', String, nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="Fundamental_information")
    def __init__(self, stock):
        self.stock = stock

    def add_value(self, name, sector, price, price_earnings, dividend_yield, earnings_share, weak52_low, weak52_high,
                  market_cap,ebitda,price_sales,price_book,sec_filings_url):
        self.name = name
        self.sector = sector
        self.price = price
        self.price_earnings = price_earnings
        self.dividend_yield = dividend_yield
        self.earnings_share = earnings_share
        self.weak52_low = weak52_low
        self.weak52_high = weak52_high
        self.market_cap = market_cap
        self.ebitda=ebitda
        self.price_sales=price_sales
        self.price_book=price_book
        self.sec_filing_url=sec_filings_url

    def repr(self):
        print('Name: {} '.format(self.name))
        print('sector: {}'.format(self.sector))
        print('price : {}'.format(self.price))
        print('sec filings: {}'.format(self.sec_filing_url))
        print('Earnings/Shared: {}'.format(self.earnings_share))
        print('Price Sales : {}'.format(self.price_sales))
        print('Divided Yield: {}'.format(self.dividend_yield))



class Trainning_Table(db.Base):
    __tablename__ = 'Trainning_Table'

    id = Column(Integer, primary_key=True)
    message_id = Column('message_id', Integer, nullable=True)
    Time = Column('Time', DateTime, nullable=True)
    Open = Column('Open', REAL, nullable=True)
    Close = Column('Close', REAL, nullable=True)
    High = Column('High', REAL, nullable=True)
    Low = Column('Low', REAL, nullable=True)
    Volume = Column('Volume', REAL, nullable=True)
    Message = Column('Message', TEXT, nullable=True)
    User = Column('User_id', Integer, nullable=True)
    sentiment = Column('sentiment', String, nullable=True)
    sentiment_positive = Column('pos_score', Float, nullable=True)
    sentiment_negative = Column('neg_score', Float, nullable=True)
    naive_bayes_classifier = Column('Naive_bayes_sentiment', String, nullable=True)
    stock_id = Column(Integer, ForeignKey('Stock.id'))
    stock = relationship("Stock", back_populates="Trainning_data")

    def __init__(self, stock):
        self.stock = stock

    def add_StockTwits_value(self, time, message, user, message_id, sentiment):
        self.Time = time
        self.Message = message
        self.User = user
        self.message_id = message_id
        self.sentiment = sentiment

    def add_sentiment_score(self, sentiment_score):
        self.sentiment_positive = sentiment_score[0]
        self.sentiment_negative = sentiment_score[1]

    def add_naive_bayes_sentiment(self, naive_sentiment):
        self.naive_bayes_classifier = naive_sentiment

    def add_Real_day_value(self,time,open,close,high,low,volume):
        self.Time=time
        self.Open=open
        self.Close=close
        self.High=high
        self.Low=low
        self.Volume=volume

    def repr(self):
        print('Time: {} '.format(self.Time))
        print('Twitter count : {}'.format(self.User))
        print('Message id: {}'.format(self.message_id))
        print('New : {}'.format(self.Message))
        print('Sentiment : {}'.format(self.sentiment))
        print('pos sentiment : {} neg sentiment : {}  '.format(self.sentiment_positive, self.sentiment_negative))
        print('Naive bayes sentiment : {}'.format(self.naive_bayes_classifier))


