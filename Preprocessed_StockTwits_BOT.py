from multiprocessing.dummy import Pool as ThreadPool
from Database.Manage_database import Manage_StockDatabase, Stock,Real_values,StockTwits
import time

class Preprocessed_StockTwits_BOT:

    def __init__(self,execute_time):
        self.execute_time=execute_time
        self.db=Manage_StockDatabase()

    def Full_Preprocess(self):
        session=self.db.Session()
        stocks=session.query(Stock).all()
        #pool1 = ThreadPool(8)
        # Open the urls in their own threads
        # and return the results
        pool3=ThreadPool(8)
        pool3.map(self.Check_Preprocess,stocks)
        pool3.close()
        pool3.join()
        pool4=ThreadPool(4)
        pool4.map(self.db.Preprocess_Stocktwits,stocks)
        pool4.close()
        pool4.join()
        session.close()

    def Check_repeted(self,stock):
        # Open the urls in their own threads
        # and return the results
        self.db.Repeted_StockTwits(stock=stock,time_out=self.execute_time*60*60)
        return

    def Check_Preprocess(self,stock):
        self.db.check_Preprocesses_StockTwits(stock=stock,time_out=self.execute_time*60*60)
        return

    def cycle_execute(self):
        # Continuous execution
        #starttime = time.time()
        timeout = time.time() + self.execute_time*60 # execute_time seconds times 2 meaning the script will run for this minutes
        while time.time() <= timeout:
            try:
                self.Full_Preprocess()
                print('Se fue a dormir')
                #time.sleep(60*5)  # 5 minutes interval between each new iteration
            except KeyboardInterrupt:
                print('\n\nKeyboard exception received. Exiting.')
                exit()


bot=Preprocessed_StockTwits_BOT(execute_time=180)
#bot.db.Delete_repeted_StockTwits_preprocesses()
#bot.cycle_execute()
bot.db.labelled_StockTwits()