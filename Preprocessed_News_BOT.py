from multiprocessing.dummy import Pool as ThreadPool
from Database.Manage_database import Manage_StockDatabase, Stock,Real_values,StockTwits,Financial_News
import time
import datetime
class Preprocessed_News_BOT:

    def __init__(self,execute_time):
        self.execute_time=execute_time
        self.db=Manage_StockDatabase()

    def Full_Preprocess(self):
        self.db.add_datetime_news()
        session=self.db.Session()
        stock=session.query(Stock).filter_by(name='AAPL').first()
        start = datetime.datetime(2020,2, 1, 0, 0, 0)
        #for stock in stocks:
        #    stock.repr()
        self.db.Finbert_preprocess_news(stock=stock,start=start)
        self.db.add_Financial_new_preprocessed()
        session.close()


    def cycle_execute(self):
        # Continuous execution
        #starttime = time.time()
        timeout = time.time() + self.execute_time*60 # execute_time seconds times 2 meaning the script will run for this minutes
        while time.time() <= timeout:
            try:
                #self.db.add_datetime_news()
                self.Full_Preprocess()
                print('Se fue a dormir')
                break
                #time.sleep(60*5)  # 5 minutes interval between each new iteration
            except KeyboardInterrupt:
                print('\n\nKeyboard exception received. Exiting.')
                exit()


bot=Preprocessed_News_BOT(execute_time=180)
bot.cycle_execute()