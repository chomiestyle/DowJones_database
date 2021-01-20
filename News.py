
from multiprocessing.dummy import Pool as ThreadPool
import yfinance as yf
from yahoo_fin.stock_info import *
from Database.Manage_database import Manage_StockDatabase, Stock,Real_values
import time

class News_BOT:

    def __init__(self,execute_time):
        self.execute_time=execute_time
        self.db=Manage_StockDatabase()

    def read_news(self):
        #stock_list=self.get_stock_list()
        stock_list = self.db.session.query(Stock).all()
        pool_yahoo = ThreadPool(4)
        print('Lee el Yahoo')
        pool_yahoo.map(self.db.read_YAHOO, stock_list)
        # # close the pool and wait for the work to finish
        pool_yahoo.close()
        pool_yahoo.join()
        print('Ahora lee el Finviz')
        pool_finviz=ThreadPool(4)
        pool_finviz.map(self.db.read_finviz,stock_list)
        pool_finviz.close()
        pool_finviz.join()
        # print('Ahora lee el Nasdaq')
        pool_nasdaq=ThreadPool(4)
        pool_nasdaq.map(self.db.read_nasdaq,stock_list)
        pool_nasdaq.close()
        pool_nasdaq.join()



    def get_stock_list(self):
        ###Metodo que uso para privilegiar los activos que estan menos provistos de noticias#######
        file = open('C:/Users/56979/PycharmProjects/DOW_JONES_BOTS/Database/Total_news.txt', 'r')
        symbols, cantidad = [], []
        for line in file.readlines():
            l = line.split(',')
            if len(l) > 1:
                #print(l)
                symbol = l[0]
                news = l[1]
                #print('El stock {} tiene {} noticias'.format(symbol, news))
                symbols.append(symbol)
                cantidad.append(int(news))
        dataframe = pd.DataFrame(columns=['Symbol', 'Cantidad_news'])
        dataframe['Symbol'] = symbols
        dataframe['Cantidad_news'] = cantidad
        data = dataframe.sort_values(by=['Cantidad_news'])
        #print(len(data.values))
        sorted_stocks = []
        session=self.db.Session()
        stocks=session.query(Stock).all()
        for array in data.values:
            symbol = array[0]
            print(data)
            #print(symbol)
            for stock in stocks:
                if stock.name == symbol:
                    sorted_stocks.append(stock)

        for s in sorted_stocks:
            s.repr()
        session.close()
        return sorted_stocks

    def cycle_execute(self):

        # Continuous execution
        timeout = time.time() + self.execute_time*60*60 # execute_time seconds times 2 meaning the script will run for this minutes
        while time.time() <= timeout:
            try:
                self.read_news()
                print('Se fue a dormir')
                time.sleep(60*5)  # 5 minutes interval between each new iteration
            except KeyboardInterrupt:
                print('\n\nKeyboard exception received. Exiting.')
                exit()


bot=News_BOT(execute_time=12)
bot.cycle_execute()
#bot.db.export_news()