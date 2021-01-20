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
from Database.Manage_database import Manage_StockDatabase
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
from multiprocessing.dummy import Pool as ThreadPool

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



def article_information(tmp,stock_name):
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
    # if title_goose == 'Access to this page has been denied.' or text_goose == None:
    #     print('sale por falta de acceso')
    #     return
    summary_gosse = article.meta_description
    authors_goose = article.authors
    date_goose = article.publish_date
    meta_keywords_goose = article.meta_keywords
    info_goose = article.infos
    image_goose = article.top_image
    aditional_data_gosse = article.additional_data
    final_url_goose = article.final_url
    final_url_goose_split = final_url_goose.split('/')
    source_article = final_url_goose_split[2]
    #fuente.append(source_article)
    # print(info_goose['opengraph'])

    goose_result_dicc = {'author': authors_goose,
                         'title': title_goose,
                         'published': date_goose,
                         'text': text_goose,
                         'summary': summary_gosse,
                         'keywords': meta_keywords_goose,
                         'image': image_goose,
                         'fuente': source_article,
                         'url': final_url_goose,
                         'info': info_goose}
    """Analyze the sentiment"""
    sia = SentimentIntensityAnalyzer()
    _summary = sia.polarity_scores(summary_gosse)['compound']
    _title = sia.polarity_scores(title_goose)['compound']
    # strftime
    """Parse the date"""
    p_date = '{}_%{}'.format(stock_name, str(date_goose))
    new_data = {'guid': 'No_guid',
                'author': authors_goose,
                'title': title_goose,
                'published': date_goose,
                'text': text_goose,
                'summary': summary_gosse,
                'keywords': meta_keywords_goose,
                'image': image_goose,
                'fuente': source_article,
                'url': final_url_goose,
                'p_date': p_date,
                'sentiment_summary': _summary,
                'sentiment_title': _title}


    #print(new_data)

    return new_data


def multi_articles_scraps(stock):
    article_list=full_scrap_NASDAQ(stock.name)
    pool = ThreadPool(4)
    # Open the urls in their own threads
    # and return the results
    results = pool.map(article_information(stock_name=stock.name), article_list)
    print(results)
    # close the pool and wait for the work to finish
    pool.close()
    pool.join()
    return results
    #pool2=ThreadPool(6)
    #new_database=Manage_StockDatabase()
    #data_bases=pool2.map(new_database.add_Financial_new(stock=stock))


new_database=Manage_StockDatabase()
stocks=new_database.session.query(Stock).all()

big_pool=ThreadPool(10)
big_results=big_pool.map(multi_articles_scraps,stocks)

print(len(big_results))
for r in big_results:
    print(len(r))
    print(r)