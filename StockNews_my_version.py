import os
import datetime as dt
import pandas
import feedparser
import requests
import nltk
import sys
from numpy import median
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import time
from goose3 import Goose
#from Database.Manage_database import Manage_StockDatabase
from Database.Stock import Stock,Financial_News
#from Web_scrapping.Newspapers.Newsletters import scrap_url_article
import newspaper
import random
from lxml.html.clean import Cleaner
from htmlmin import minify
from newspaper import Config, Article, Source
from selenium import webdriver
import traceback
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from newspaper import Config, Article, Source
from bs4 import BeautifulSoup as bs




def full_scrap_finviz(stock_name):
    finviz_URL = 'https://finviz.com/quote.ashx?t={}'.format(stock_name)
    chrome_driver = webdriver.Chrome(executable_path="D:/Browser_drivers/chromedriver.exe")
    chrome_driver.get(finviz_URL)
    time.sleep(3)
    page = bs(chrome_driver.page_source, 'html.parser')
    links=[]
    table=page.find('table',id='news-table').find_all('a',class_='tab-link-news')
    print(len(table))
    for t in table:
        links.append(t.get('href'))
    chrome_driver.quit()
    return links

def full_scrap_NASDAQ(stock):
    source='https://www.nasdaq.com'
    nasdaq_URL='https://www.nasdaq.com/market-activity/stocks/{}/news-headlines'.format(stock)
    #driver = webdriver.Chrome(executable_path="D:/Browser_drivers/chromedriver.exe")
    driver=webdriver.Firefox(executable_path="D:/Browser_drivers/geckodriver.exe")
    driver.implicitly_wait(30)
    #driver.add_cookie()
    driver.get(nasdaq_URL)
    time.sleep(3)
    links=[]

    buttons=driver.find_elements_by_class_name('pagination__page')
    max=int(buttons[-1].text)
    print(max)
    contador = 1
    while contador<=max:
        try:
            print(contador)
            # wait 10 seconds before looking for element
            element=WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.XPATH,"//button[@class='pagination__page pagination__page--active' and @data-page='{}']".format(contador))))
            # time.sleep(5)
            print('el clickeable la pagina')
            element.click()
            print('pasa por la pagina {}'.format(contador))
            # driver.implicitly_wait(30)
            page = bs(driver.page_source, 'lxml')
            body = page.find('body')
            # print(body)
            headline_link = body.find_all('a', class_='quote-news-headlines__link')
            # print(len(headline_link))
            for link in headline_link:
                url=source+link.get('href')
                print(url)
                if url not in links:
                    links.append(url)

            if contador==max:
                break

            contador+=1
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,"//button[@class='pagination__page' and @data-page='{}']".format(contador)))).click()
        except Exception as ex:
            print(ex)
            print('se fue al except')
            prueba = driver.find_element_by_id('_evidon_banner')
            print(prueba.text)
            cookie_button=prueba.find_element_by_id("_evidon-decline-button")
            print(cookie_button.text)
            cookie_button.click()
            time.sleep(random.randint(0,50))
            # else quit
    driver.quit()
    print(len(links))
    return links

def convert_proxies(filename):
    f = open(filename, "r")
    proxies_array=[]
    for line in f.readlines():
        line=line.split('\n')
        proxies_array.append(line[0])
    f.close()
    return proxies_array


def article_information(tmp):
    g=Goose({'browser_user_agent': 'Mozilla', 'parser_class':'lxml'})
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
        "Connection": "keep-alive",
        "Host": "www.nasdaq.com",
        "Referer": "http://www.nasdaq.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
    }
    g.config.http_headers=headers
    while True:
        try:
            article = g.extract(url=tmp)
            print('supera el aricle')
            break
        except requests.exceptions.ConnectionError as r:
            print(r.strerror)
            sleepy_time=random.randint(0,20)
            print('Dormira {} segundos'.format(sleepy_time))
            time.sleep(sleepy_time)

    text_goose = article.cleaned_text
    title_goose = article.title
    if title_goose == 'Access to this page has been denied.' or text_goose == None:
        print('sale por falta de acceso')
    #title.append(title_goose)
    #text.append(text_goose)
    meta__description_gosse = article.meta_description
    #summary.append(meta__description_gosse)
    authors_gooose = article.authors
    #authors.append(authors_gooose)
    date_goose = article.publish_date
    #published.append(date_goose)
    meta_keywords_goose = article.meta_keywords
    #keywords.append(meta_keywords_goose)
    info_goose = article.infos
    image_goose = article.top_image
    #image.append(image_goose)
    aditional_data_gosse = article.additional_data
    # =article_goose.final_url
    final_url_goose = article.final_url
    #url.append(final_url_goose_split)
    final_url_goose_split = final_url_goose.split('/')
    # print(final_url_goose_split)
    source_article = final_url_goose_split[2]
    #fuente.append(source_article)
    # print(info_goose['opengraph'])

    goose_result_dicc = {'author': authors_gooose,
                         'title': title_goose,
                         'published': date_goose,
                         'text': text_goose,
                         'summary': meta__description_gosse,
                         'keywords': meta_keywords_goose,
                         'image': image_goose,
                         'fuente': source_article,
                         'url': final_url_goose,
                         'info': info_goose}
    print(goose_result_dicc)

    return goose_result_dicc

def goose_articles_extractor(url_list):
    with Goose({'browser_user_agent': 'Mozilla', 'parser_class':'soup'}) as g:
        #article_extractor=pandas.DataFrame()
        article_extractor = pandas.DataFrame(
                                columns=['guid',
                                        'stock',
                                        'title',
                                        'summary',
                                        'text',
                                        'fuente',
                                        'author',
                                        'published',
                                        'url'
                                        'image',
                                        'p_date',
                                        'sentiment_summary',
                                        'sentiment_title',
                                        'keywords']
                                )

        guid,stock,title,text,authors,summary,text,fuente,published,url,image,keywords=[],[],[],[],[],[],[],[],[],[],[],[]
        for tmp in url_list:
            article = g.extract(url=tmp)
            text_goose = article.cleaned_text
            title_goose = article.title
            if title_goose == 'Access to this page has been denied.' or text_goose == None:
                print('sale por falta de acceso')
                continue

            title.append(title_goose)
            text.append(text_goose)
            meta__description_gosse = article.meta_description
            summary.append(meta__description_gosse)
            authors_gooose = article.authors
            authors.append(authors_gooose)
            date_goose = article.publish_date
            published.append(date_goose)
            meta_keywords_goose = article.meta_keywords
            keywords.append(meta_keywords_goose)
            info_goose = article.infos
            image_goose = article.top_image
            image.append(image_goose)
            aditional_data_gosse = article.additional_data
            # =article_goose.final_url
            final_url_goose = article.final_url
            url.append(final_url_goose_split)
            final_url_goose_split = final_url_goose.split('/')
            # print(final_url_goose_split)
            source_article = final_url_goose_split[2]
            fuente.append(source_article)
            # print(info_goose['opengraph'])

            goose_result_dicc = {'author': authors_gooose,
                                 'title': title_goose,
                                 'date': date_goose,
                                 'text': text_goose,
                                 'summary': meta__description_gosse,
                                 'keywords': meta_keywords_goose,
                                 'image': image_goose,
                                 'fuente': fuente,
                                 'link': final_url_goose,
                                 'info': info_goose}
            print(goose_result_dicc)
        article_extractor['title']=title
        article_extractor['author']=authors
        article_extractor['text']=text
        article_extractor['summary']=summary
        article_extractor['fuente']=fuente
        article_extractor['published']=published
        article_extractor['url']=url
        article_extractor['image']=image
        article_extractor['keywords']=keywords

        return article_extractor

def raw_scraper(url, memoize, language=None):
    config = Config()
    config.memoize_articles = memoize
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    #config.fetch_images = False
    #config.request_timeout=123
    headers = {'content-type': 'application/json'}
    config.headers=headers
    print(config.headers)
    config.browser_user_agent=user_agent
    #config.get_parser()
    filename1='C:/Users/56979/PycharmProjects/Stocks_predictions/Web_scrapping/StockNews/proxies_utiles.txt'
    filename2='C:/Users/56979/PycharmProjects/Stocks_predictions/Web_scrapping/StockNews/http_proxies.txt'
    filename3 = 'C:/Users/56979/PycharmProjects/Stocks_predictions/Web_scrapping/StockNews/free_proxies.txt'
    #https_ip_addresses=convert_proxies(filename1)
    bool=True
    if language != None:
        print('el lenguaje es distinto de None')
        config.language = language
    contador=0
    while bool:
        try:
            #proxy_index = random.randint(0, len(https_ip_addresses) - 1)
            #proxie_ports=https_ip_addresses[proxy_index]
            #proxies = {"http": proxie_ports, "https": proxie_ports,}
            #config.proxies = proxies
            #print('1')
            cleaner = Cleaner()
            print('2')
            cleaner.javascript = True
            print('3')
            cleaner.style = True
            print('4')
            article = newspaper.Article(url=url,config=config)
            print('5')
            article.download()
            print('6')
            if contador>3:
                return None
            #html = minify(article.html)
            print('7')
            #html = cleaner.clean_html(html)
            print('8')
            article.parse()
            print('9')
            bool=False
            #print('el valor que no esta banneado es {}'.format(proxie_ports))
            return article

        except Exception as ex:

            print(ex.args)
            contador+=1
            #if len(https_ip_addresses) == 1:
            #    return None
            #print('el valor que esta banneado es {}'.format(proxie_ports))
            #https_ip_addresses.remove(proxie_ports)
            ##Web scrapping method ### Sirve para que parezca mas humano scraper
            time_request = random.randint(0, 20)
            print('DORMIRA POR {} SEGUNDOS'.format(time_request))
            time.sleep(time_request)



def scrap_url_article(url,language=None):
    ###Primero pruebo lo que puedo sacar con GOOSE
    extractor = Goose({'browser_user_agent': 'Mozilla', 'parser_class':'soup'})
    article_goose = extractor.extract(url=url)
    #print(article_goose.title)
    text_goose = article_goose.cleaned_text
    title_goose = article_goose.title
    meta__description_gosse=article_goose.meta_description
    authors_gooose=article_goose.authors
    date_goose=article_goose.publish_date
    meta_keywords_goose=article_goose.meta_keywords
    info_goose=article_goose.infos
    image_goose=article_goose.top_image
    aditional_data_gosse=article_goose.additional_data
    #=article_goose.final_url
    final_url_goose = article_goose.final_url
    final_url_goose_split=final_url_goose.split('/')
    #print(final_url_goose_split)
    fuente=final_url_goose_split[2]
    #print(info_goose['opengraph'])


    goose_result_dicc={'author':authors_gooose,
                       'title':title_goose,
                       'date':date_goose,
                       'text':text_goose,
                       'summary':meta__description_gosse,
                       'keywords':meta_keywords_goose,
                       'image':image_goose,
                       'fuente':fuente,
                       'link':final_url_goose,
                       'info':info_goose}
    print(goose_result_dicc)

    if article_goose.title =='Access to this page has been denied.' or text_goose==None:
        print('sale por falta de acceso')
        return None

    if fuente=='www.moodys.com' or fuente=='www.nasdaq.com':
        return goose_result_dicc
    article=raw_scraper(url=url,memoize=False,language=language)
    if article==None:
        return goose_result_dicc

    opengrah=info_goose['opengraph']
    #(opengrah)
    if 'url' in opengrah.keys():
        url_article_origin=opengrah['url']
    else:
        meta=article.meta_data
        article_origin=meta['og']
        #print(article_origin)
        if 'url' in article_origin.keys():
            url_article_origin=article_origin['url']

        else:
            url_article_origin=url

    split_original=url_article_origin.split('/')
    #print(split_original)
    split_url=url.split('/')
    if split_original[2]!=split_url[2]:
        print('Aca hay diferente origen')
        print('link de articulo {}'.format(url_article_origin))
        print('link de yahoo {}'.format(url))
        result_dicc=scrap_url_article(url_article_origin)
    else:
        print('este url es del articulo')
        print('link de articulo {}'.format(url_article_origin))
        print('link de yahoo {}'.format(url))
        text=article.text
        fuente2=split_url[2]
        article.nlp()
        author=article.authors
        if len(author)==0:
            author=goose_result_dicc['author']
        title=article.title
        if title==None:
            title=goose_result_dicc['title']
        date=article.publish_date
        if date==None:
            date=goose_result_dicc['date']
        summary=article.summary
        if summary==None:
            summary=goose_result_dicc['summary']
        keywords=article.keywords
        print('estos son los keywords de el article:')
        print(keywords)
        if keywords==None:
            keywords=goose_result_dicc['keywords']
        image=article.top_image
        if image==None:
            image=goose_result_dicc['image']

        result_dicc={'author':author,
                     'title':title,
                     'date':date,
                     'text':text_goose,
                     'summary':summary,
                     'keywords': keywords,
                     'image':image,
                     'fuente':fuente2,
                     'link':url}

    print(result_dicc)
    return result_dicc



class StockNews:
    YAHOO_URL = 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=%s&region=US&lang=en-US'
    TRADING_URL = 'https://api.worldtradingdata.com/api/v1/history'

    #DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'data')

    def __init__(self, stock, database_atache, save_news=True, wt_key=None):
        """
        :param stocks: A list of Stock Symbols such as "AAPL" for Apple, NFLX for Netflix etc.
        :param news_file: Filename of saved news data
        :param summary_file: Filename of saved summary (Stock by day)
        :param save_news: Persist the data to csv or not
        :param closing_hour: attach news for the next trading day after this
        :param closing_minute: attach news for the next trading day after this
        :param wt_key: API Key from https://www.worldtradingdata.com/
        """

        self.stock = stock
        #self.news_file = news_file
        #self.summary_file = summary_file
        self.save_news = save_news
        #self.closing_hour = closing_hour
        #self.closing_minute = closing_minute
        self.wt_key = wt_key
        self.yahoo=True
        self.viz=True
        #self.nasdaq=True
        self.db=database_atache

        if self.save_news:
            print('se guardan')
            # df = pandas.read_csv(os.path.join(self.DATA_FOLDER, self.news_file), header=0, sep=';')
            # df=self.db.get_Stock_to_dataframe(stock_name=self.stock.name,Table_info=Financial_News)
            session=self.db.Session()
            self.df = pandas.read_sql(session.query(Financial_News).filter_by(stock=self.stock).statement,
                                     con=self.db.engine)

            print(self.df)
            session.close()
            if self.df.empty:
                print('efectivamente df estaba vacio ')
                self.fisrt_time=True
                self.df = pandas.DataFrame(
                    columns=['guid',
                             'stock',
                             'title',
                             'summary',
                             'text',
                             'fuente',
                             'author',
                             'published',
                             'url'
                             'image',
                             'p_date',
                             'sentiment_summary',
                             'sentiment_title',
                             'keywords']
                )
            else:
                self.fisrt_time=False



    def read_rss(self):
        """
        :return: pandas.DataFrame
        """

        """Download VADER"""
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)

        self.read_YAHOO()
        self.read_finviz()
        #self.read_NASDAQ()




    def read_YAHOO(self):
        # """
        # :return: pandas.DataFrame
        # """
        #
        # """Download VADER"""
        # try:
        #     nltk.data.find('vader_lexicon')
        # except LookupError:
        #     nltk.download('vader_lexicon', quiet=True)

        if self.yahoo:
            ##Busca en Yahoo finance
            feed = feedparser.parse(self.YAHOO_URL % self.stock.name)
            #print(len(feed.entries))
            for entry in feed.entries:

                if not self.fisrt_time:
                    info=article_information(tmp=entry.link)
                    """Find url and skip if exists"""
                    new_link = self.df.loc[self.df['url'] == info['url']]
                    new_text=self.df.loc[self.df['text']==info['text']]

                    if len(new_link)>0 and len(new_text)>0:
                        new=self.db.session.query(Financial_News).filter_by(stock=self.stock).filter_by(url=new_link).filter_by(text=new_text).first()
                        if new!=None:
                            if new.guid=='No_guid':
                                new.guid=entry.guid
                                self.db.session.commit()

                    """Find guid and skip if exists"""
                    guid = self.df.loc[self.df['guid'] == entry.guid]
                    #guid = df_database.loc[df['guid'] == entry.guid]
                    if len(guid) > 0:
                        continue
                    """Get scrap of the article"""
                url_article=entry.link
                dicc=scrap_url_article(url_article)
                if dicc==None:
                    print('No saco nada del articulo')
                    continue
                """Analyze the sentiment"""
                sia = SentimentIntensityAnalyzer()
                _summary = sia.polarity_scores(entry.summary)['compound']
                _title = sia.polarity_scores(entry.title)['compound']

                """Parse the date"""
                p_date = '%s_%s' % (self.stock.name, dt.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S +0000').strftime("%Y-%m-%d"))
                new_data = {'guid': entry.guid,
                            'author': dicc['author'],
                            'title': entry.title,
                            'published': entry.published,
                            'text': dicc['text'],
                            'summary': entry.summary,
                            'keywords': dicc['keywords'],
                            'image': dicc['image'],
                            'fuente': dicc['fuente'],
                            'url': dicc['link'],
                            'p_date': p_date,
                            'sentiment_summary': _summary,
                            'sentiment_title': _title}
                self.db.add_Financial_new(new_data=new_data, stock=self.stock)


    def read_finviz(self):
        # """
        # :return: pandas.DataFrame
        # """
        #
        # """Download VADER"""
        # try:
        #     nltk.data.find('vader_lexicon')
        # except LookupError:
        #     nltk.download('vader_lexicon', quiet=True)


        if self.viz:
            articles = full_scrap_finviz(stock_name=self.stock.name)
            for article in articles:
                print(article)
                if not self.fisrt_time:
                    info=article_information(tmp=article)
                    """Find url and skip if exists"""
                    new_link = self.df.loc[self.df['url'] == info['url']]
                    new_text=self.df.loc[self.df['text']==info['text']]
                    #new_title=df_database.loc[df_database['title']==info['title']]
                    #new_summary=df_database.loc[df_database['summary']==info['summary']]
                    #new_published=df_database.loc[df_database['published']==info['published']]
                    if len(new_link) > 0 and len(new_text)>0:
                        print('Esta noticia ya esta en la base de datos')
                        print('Tiene el link:')
                        print(new_link)
                        print('Y el texto :')
                        print(new_text)
                        continue
                dicc = scrap_url_article(article)
                """Get scrap of the article"""
                if dicc == None:
                    print('No saco nada del articulo')
                    continue
                summary = dicc['summary']
                title = dicc['title']
                published = dicc['date']

                """Analyze the sentiment"""
                sia = SentimentIntensityAnalyzer()
                _summary = sia.polarity_scores(summary)['compound']
                _title = sia.polarity_scores(title)['compound']
                # strftime
                """Parse the date"""
                p_date = '{}_%{}'.format(self.stock.name, str(published))
                new_data= {'guid':'No_guid',
                            'author': dicc['author'],
                            'title': title,
                            'published': published,
                            'text': dicc['text'],
                            'summary': summary,
                            'keywords': dicc['keywords'],
                            'image': dicc['image'],
                            'fuente': dicc['fuente'],
                            'url': dicc['link'],
                            'p_date':p_date,
                            'sentiment_summary':_summary,
                            'sentiment_title':_title}
                self.db.add_Financial_new(new_data=new_data,stock=self.stock)


    def read_NASDAQ(self):
        # """
        # :return: pandas.DataFrame
        # """
        #
        # """Download VADER"""
        # try:
        #     nltk.data.find('vader_lexicon')
        # except LookupError:
        #     nltk.download('vader_lexicon', quiet=True)

        if self.nasdaq:
                links=full_scrap_NASDAQ(stock=self.stock.name)
                for l in links:
                    print(l)
                    if not self.fisrt_time:
                        info = article_information(tmp=l)
                        """Find url and skip if exists"""
                        new_link = self.df.loc[self.df['url'] == info['url']]
                        new_text = self.df.loc[self.df['text'] == info['text']]
                        # new_title=df_database.loc[df_database['title']==info['title']]
                        # new_summary=df_database.loc[df_database['summary']==info['summary']]
                        # new_published=df_database.loc[df_database['published']==info['published']]
                        if len(new_link) > 0 and len(new_text) > 0:
                            print('Esta noticia ya esta en la base de datos')
                            print('Tiene el link:')
                            print(new_link)
                            print('Y el texto :')
                            print(new_text)
                            continue
                    #dicc = scrap_url_article(l)
                    """Get scrap of the article"""
                    #if dicc == None:
                    #    print('No saco nada del articulo')
                    #    continue
                    summary = info['summary']
                    title = info['title']
                    published = info['published']

                    """Analyze the sentiment"""
                    sia = SentimentIntensityAnalyzer()
                    _summary = sia.polarity_scores(summary)['compound']
                    _title = sia.polarity_scores(title)['compound']
                    # strftime
                    """Parse the date"""
                    p_date = '{}_%{}'.format(self.stock.name, str(published))
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

                    print(new_data)
                    self.db.add_Financial_new(new_data=new_data, stock=self.stock)

    # def summarize(self):
    #     """
    #     Summarize news by day and get the Stock Value
    #     :return: pandas.DataFrame, <int> number of requests made
    #     """
    #
    #     if self.wt_key is None:
    #         raise Exception('Please set the WorldTradingData API Key. '
    #                         'Get your key here: https://www.worldtradingdata.com')
    #
    #     """Read Financial_News CSV"""
    #     df = self.read_rss()
    #
    #     """Read Summary CSV"""
    #     df_sum = pandas.read_csv(os.path.join(self.DATA_FOLDER, self.summary_file), header=0, sep=';')
    #
    #     """Count Requests"""
    #     r_count = 0
    #
    #     for index, row in df.iterrows():
    #         """Parse the Date from CSV"""
    #         news_date = dt.datetime.strptime(row['published'], '%a, %d %b %Y %H:%M:%S +0000')
    #         check_date = self._get_check_date(news_date)
    #
    #         """Create ID for summary"""
    #         _id = '%s_%s' % (row['stock'], news_date.strftime("%Y-%m-%d"))
    #
    #         """Find id (SYMBOL_DATE) if exists, skip it"""
    #         sum_id = df_sum.loc[df_sum['id'] == _id]
    #         if len(sum_id) > 0:
    #             continue
    #
    #         """Get all Financial_News where p_date is the sum_id"""
    #         _df = df[df['p_date'] == _id]
    #
    #         """Make Median and AVG"""
    #         avg_summary, med_summary = self._median_avg('sentiment_summary', _df)
    #         avg_title, med_title = self._median_avg('sentiment_title', _df)
    #
    #         """Add new entry to DF"""
    #         _row = [
    #             _id,
    #             row['stock'],
    #             news_date.strftime("%Y-%m-%d %H:%M:%S"),
    #             check_date.strftime("%Y-%m-%d"),
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             'UNCHECKED',
    #             avg_summary,
    #             med_summary,
    #             avg_title,
    #             med_title
    #         ]
    #         df_sum.loc[len(df_sum)] = _row
    #
    #     """Update all 'UNCHECKED' columns"""
    #     _df_uc = df_sum[df_sum['change'] == 'UNCHECKED']
    #
    #     """Go through all unchecked"""
    #     for index_uc, row_uc in _df_uc.iterrows():
    #
    #         """If the check_day is today, skip it"""
    #         _date = dt.datetime.strptime(row_uc['check_day'], '%Y-%m-%d')
    #         c_date = dt.datetime(_date.year, _date.month, _date.day, 23, 59, 59)
    #         today = dt.datetime.now()
    #
    #         if c_date >= today:
    #             continue
    #
    #         params = {
    #             'symbol': row_uc['stock'],
    #             'date_from': row_uc['check_day'],
    #             'date_to': row_uc['check_day'],
    #             'api_token': self.wt_key
    #         }
    #
    #         r = requests.get(url=self.TRADING_URL, params=params)
    #
    #         """We made a request"""
    #         r_count += 1
    #
    #         """extracting data in json format"""
    #         data = r.json()
    #         #print(data.keys())
    #         """Extract open and close"""
    #         if 'history' in data.keys():
    #
    #             _open = float(data['history'][row_uc['check_day']]['open'])
    #             _close = float(data['history'][row_uc['check_day']]['close'])
    #             _high = float(data['history'][row_uc['check_day']]['high'])
    #             _low = float(data['history'][row_uc['check_day']]['low'])
    #             _volume = float(data['history'][row_uc['check_day']]['volume'])
    #
    #             if _open >= _close:
    #                 change = 'loss'
    #             else:
    #                 change = 'win'
    #
    #             df_sum.loc[df_sum['id'] == row_uc['id'], 'change'] = change
    #             df_sum.loc[df_sum['id'] == row_uc['id'], 'open'] = _open
    #             df_sum.loc[df_sum['id'] == row_uc['id'], 'close'] = _close
    #             df_sum.loc[df_sum['id'] == row_uc['id'], 'high'] = _high
    #             df_sum.loc[df_sum['id'] == row_uc['id'], 'low'] = _low
    #             df_sum.loc[df_sum['id'] == row_uc['id'], 'volume'] = _volume
    #
    #     df_sum.to_csv(os.path.join(self.DATA_FOLDER, self.summary_file), index=False, sep=';')
    #
    #     return df_sum, r_count
    #
    # @staticmethod
    # def _median_avg(column, t_df):
    #     """
    #     Return AVG and Median of a column
    #     :param column: Column Name
    #     :param t_df: pandas.DataFrame
    #     :return:
    #     """
    #
    #     avg = t_df[column].sum() / len(t_df)
    #     med = median(t_df[column])
    #
    #     return avg, med
    #
    # def _get_check_date(self, dt_check):
    #     """
    #     Check which day needs to be checked for a news date
    #     :param dt_check: datetime
    #     :return: dt.datetime
    #     """
    #
    #     """Get closing date"""
    #     dt_close = dt.datetime(dt_check.year, dt_check.month, dt_check.day, self.closing_hour, self.closing_minute, 0)
    #
    #     """If the CheckDate is later than CloseDate, add one day"""
    #     if dt_check > dt_close:
    #         dt_check += dt.timedelta(days=1)
    #
    #     """If the CheckDate is a Saturday, add 2 days"""
    #     if dt_check.weekday() == 5:
    #         dt_check += dt.timedelta(days=2)
    #
    #     """If the CheckDate is a Sunday, add 1 day"""
    #     if dt_check.weekday() == 6:
    #         dt_check += dt.timedelta(days=1)
    #
    #     """return date to check"""
    #     return dt_check
