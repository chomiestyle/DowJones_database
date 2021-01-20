from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

def connect_database(param_dic):
    connect = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(param_dic['user'], param_dic['password'], param_dic['host'],param_dic['port'] ,param_dic['database'])
    engine = create_engine(connect,pool_size=50, max_overflow=20,pool_timeout=120)
    return engine




# 2 - generate database schema
#Base.metadata.create_all(engine)


#### Actualizar todas las bases de datos

down_jones_param_dic = {'host': 'localhost', 'database': 'down_jones', 'user': 'postgres', 'password': 'sleepy1992', 'port': 5433}
nasdaq_param_dic={'host': 'localhost','database': 'nasdaq', 'user': 'postgres', 'password': 'sleepy1992', 'port': 5433}
sp500_param_dic={'host': 'localhost','database': 'sp500', 'user': 'postgres', 'password': 'sleepy1992', 'port': 5433}
web_scraping_param_dic={'host': 'localhost','database': 'web_scrapping', 'user': 'postgres', 'password': 'sleepy1992', 'port': 5433}
web_scraping_latest_news_param_dic={'host': 'localhost','database': 'intra_day_trading_news', 'user': 'postgres', 'password': 'sleepy1992', 'port': 5433}
crypto_param_dic={'host': 'localhost','database': 'cryptocurrencies', 'user': 'postgres', 'password': 'sleepy1992', 'port': 5433}
###Aca trabajo con las bases de datos ya creadas y las actualizo cada una

diccionarios=[down_jones_param_dic,nasdaq_param_dic,sp500_param_dic,web_scraping_param_dic,crypto_param_dic]

engine = connect_database(diccionarios[0])
# Session = sessionmaker(bind=engine)
# session = Session()
Base = declarative_base()

# engine_webscrapping=connect_database(web_scraping_param_dic)
# Session_webscrapping=sessionmaker(bind=engine_webscrapping)
# session_webscrapping=Session_webscrapping()
# Base_webscraping=declarative_base()


# engine_webscrapping_latest_news=connect_database(web_scraping_latest_news_param_dic)
# Session_webscrapping_latest_news=sessionmaker(bind=engine_webscrapping_latest_news)
# session_webscrapping_latest_news=Session_webscrapping_latest_news()
# Base_webscraping_latest_news=declarative_base()
