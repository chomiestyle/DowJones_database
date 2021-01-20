
from multiprocessing.dummy import Pool as ThreadPool
from Database.Manage_database import Manage_StockDatabase, Stock,Real_values
import time
from Real_Time_Plot.Plot import plot
import datetime


class Prices_BOT:

    def __init__(self,execute_time):
        self.execute_time=execute_time
        self.db=Manage_StockDatabase()

    def yahoo_update(self):
        session=self.db.Session()
        stocks=session.query(Stock).all()
        pool = ThreadPool(8)
        pool.map(self.db.update_prices_yahoo, stocks)
        # close the pool and wait for the work to finish
        pool.close()
        pool.join()
        session.close()

    def delete_repeted(self):
        session=self.db.Session()
        stocks=session.query(Stock).all()

        for stock in stocks:
            stock.repr()
            self.db.delete_repeted_values(stock=stock)
        # pool = ThreadPool(9)
        # # Open the urls in their own threads
        # # and return the results
        # pool.map(self.db.delete_repeted_values, stocks)
        # # close the pool and wait for the work to finish
        # pool.close()
        # pool.join()
        session.close()


    def cycle_execute(self):

        # Continuous execution
        #starttime = time.time()
        timeout = time.time() + self.execute_time*60 # execute_time seconds times 2 meaning the script will run for this minutes
        while time.time() <= timeout:
            try:
                self.yahoo_update()
                #real_time_train_path='C:/Users/56979/PycharmProjects/Real-Time-Stock-Market-Prediction-using-Ensemble-DL-and-Rainbow-DQN/rainbow/data/database_data/Dow_Jones/1_day'
                #self.db.export_1d_data(real_time_train_path)

                real_time_path='C:/Users/56979/PycharmProjects/Real-Time-Stock-Market-Prediction-using-Ensemble-DL-and-Rainbow-DQN/Database/DOWJONES'
                self.db.export_1m_data(real_time_path,100)
                real_time_train_path='C:/Users/56979/PycharmProjects/Real-Time-Stock-Market-Prediction-using-Ensemble-DL-and-Rainbow-DQN/rainbow/data/database_data/Dow_Jones/1_minute'
                self.db.export_1m_data(real_time_train_path)
                #print('Se fue a dormir 5 minutitos')
                #time.sleep(60*5)  # 5 minutes interval between each new iteration
                break
            except KeyboardInterrupt:
                print('\n\nKeyboard exception received. Exiting.')
                exit()


bot=Prices_BOT(execute_time=120)
bot.cycle_execute()
#dir_save_mtss_gan='C:/Users/56979/PycharmProjects/MTSS_GAN/mtss_gan/data'
#dir_save_RL_hype='C:/Users/56979/PycharmProjects/RL_Hyperparameter_Optimizer/data'
#bot.db.export_1d_data(save_dir=dir_save_mtss_gan)