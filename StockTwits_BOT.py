from Database.Manage_database import Manage_StockDatabase
from Database.Stock import Stock, StockTwits,Real_values
import datetime
import time

#### Actualizar todas las bases de datos


# ##Asi creo la base de datos inicial
new_database=Manage_StockDatabase()
# #sp500.create_database(tickers_sp500())
start_time=datetime.datetime(2020,9,17).strftime('%Y-%m-%d')
# end_time=datetime.datetime(2020, 9, 23).strftime('%Y-%m-%d')
final=datetime.datetime.now()

# ###Aca trabajo con las bases de datos ya creadas y las actualizo cada una
#
session=new_database.Session()
stocks=session.query(Stock).all()
print('\n### All Stocks:')

for stock in stocks:
     stock.repr()
     #new_database.update_prices(stock=stock)
     new_database.preprocess_stocktwits_data(stock=stock)
     #df=new_database.get_Stock_to_dataframe(stock_name=stock.name,Table_info=Real_values)
     #new_database.fill_holes(dataframe=df,stock=stock)
     #new_database.delete_repeted_StockTwits(stock=stock,Table=StockTwits)
     #time.sleep(10)
new_database.finish_connection()