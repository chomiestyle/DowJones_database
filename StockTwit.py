
from multiprocessing.dummy import Pool as ThreadPool
from Database.Manage_database import Manage_StockDatabase, Stock
import time

class StockTwits_BOT:

    def __init__(self,execute_time):
        self.execute_time=execute_time
        self.db=Manage_StockDatabase()

    def StockTwits_update(self):
        session=self.db.Session()
        stocks=session.query(Stock).all()
        pool = ThreadPool(4)
        #Open the urls in their own threads
        #and return the results
        pool.map(self.colect_Twits, stocks)
        #close the pool and wait for the work to finish
        pool.close()
        pool.join()
        session.close()

    def check_repeted_Twits(self,stock):
        stock.repr()
        len_repetead=self.db.Repeted_StockTwits(stock=stock,time_out=self.execute_time*60)
        print(len_repetead)
        return len_repetead

    def check_preprocesses_Twits(self,stock):
        stock.repr()
        len_preprocesses=self.db.check_Preprocesses_StockTwits(stock=stock,time_out=self.execute_time*60)
        print(len_preprocesses)
        return len_preprocesses

    def colect_Twits(self,stock):
        stock.repr()
        dataframe, Time_out = self.db.get_fresh_new_Twits(stock=stock)
        print(dataframe)
        while Time_out != None:
            checks_faltantes=self.db.check_Preprocesses_StockTwits(stock=stock,time_out=Time_out)
            repeted_faltantes=self.db.Repeted_StockTwits(stock=stock, time_out=Time_out)
            if checks_faltantes>0 or repeted_faltantes>0:
                dataframe,Time_out=self.db.get_fresh_new_Twits(stock=stock)
                print(dataframe)
            else:
                break
        return


    def cycle_execute(self):

        # Continuous execution
        #starttime = time.time()
        timeout = time.time() + self.execute_time*60 # execute_time seconds times 2 meaning the script will run for this minutes
        while time.time() <= timeout:
            try:
                self.StockTwits_update()
                print('Mucho trabajo  dormire 5 minutos')
                time.sleep(60*5)  # 5 minutes interval between each new iteration
            except KeyboardInterrupt:
                print('\n\nKeyboard exception received. Exiting.')
                exit()


bot=StockTwits_BOT(execute_time=180)
bot.cycle_execute()