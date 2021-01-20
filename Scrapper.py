
import pandas
import requests
import time
from goose3 import Goose
import newspaper
import random
from lxml.html.clean import Cleaner
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from newspaper import Config, Article, Source
from bs4 import BeautifulSoup as bs
import re

def full_scrap_finviz(stock_name):
    finviz_URL = 'https://finviz.com/quote.ashx?t={}'.format(stock_name)
    chrome_driver = webdriver.Chrome(executable_path="D:/Browser_drivers/chromedriver.exe")
    chrome_driver.get(finviz_URL)
    time.sleep(3)
    page = bs(chrome_driver.page_source, 'html.parser')
    links=[]
    table=page.find('table',id='news-table').find_all('a',class_='tab-link-news')
    #print(len(table))
    for t in table:
        links.append(t.get('href'))
    chrome_driver.quit()
    return links

def full_scrap_NASDAQ(stock,MAX_VALUE=None):
    source='https://www.nasdaq.com'
    nasdaq_URL='https://www.nasdaq.com/market-activity/stocks/{}/news-headlines'.format(stock)
    #driver = webdriver.Chrome(executable_path="D:/Browser_drivers/chromedriver.exe")
    driver=webdriver.Firefox(executable_path="D:/Browser_drivers/geckodriver.exe")
    driver.implicitly_wait(30)
    #driver.add_cookie()
    driver.get(nasdaq_URL)
    time.sleep(3)
    links=[]
    if MAX_VALUE == None:
        buttons=driver.find_elements_by_class_name('pagination__page')
        MAX_VALUE=int(buttons[-1].text)

    print(MAX_VALUE)
    contador = 1
    while contador<=MAX_VALUE:
        try:
            #print(contador)
            # wait 10 seconds before looking for element
            element=WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.XPATH,"//button[@class='pagination__page pagination__page--active' and @data-page='{}']".format(contador))))
            # time.sleep(5)
            #print('el clickeable la pagina')
            element.click()
            #print('pasa por la pagina {}'.format(contador))
            # driver.implicitly_wait(30)
            page = bs(driver.page_source, 'lxml')
            body = page.find('body')
            # print(body)
            headline_link = body.find_all('a', class_='quote-news-headlines__link')
            # print(len(headline_link))
            for link in headline_link:
                url=source+link.get('href')
                #print(url)
                if url not in links:
                    links.append(url)

            if contador>=MAX_VALUE:
                break
            contador+=1
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,"//button[@class='pagination__page' and @data-page='{}']".format(contador)))).click()

        except Exception as ex:
            print(ex)
            print('se fue al except')
            if contador<2:
                prueba = driver.find_element_by_id('_evidon_banner')
                #print(prueba.text)
                cookie_button=prueba.find_element_by_id("_evidon-decline-button")
                #print(cookie_button.text)
                cookie_button.click()
            time.sleep(random.randint(0,50))

            # else quit
    driver.quit()
    #print(len(links))
    return links
def full_scrap_investing(stock_name,MAX_VALUE=None):
    source='https://www.investing.com'
    #nasdaq_URL='https://www.nasdaq.com/market-activity/stocks/{}/news-headlines'.format(stock)
    #driver = webdriver.Chrome(executable_path="D:/Browser_drivers/chromedriver.exe")
    driver=webdriver.Firefox(executable_path="D:/Browser_drivers/geckodriver.exe")
    driver.implicitly_wait(30)
    #driver.add_cookie()
    driver.get(source)
    time.sleep(3)
    searcher=driver.find_element_by_xpath("//input[@class='searchText arial_12 lightgrayFont js-main-search-bar']")
    searcher.send_keys(stock_name)
    stock_buttons = searcher.find_elements_by_xpath("//a[@class='row js-quote-row-template js-quote-item']")
    WebDriverWait(stock_buttons[0], 2000).until(EC.element_to_be_clickable((By.XPATH,"//a[@class='row js-quote-row-template js-quote-item']"))).click()


    #print(stock_buttons[0])
    #stock_button=stock_buttons[0]
    #print(stock_button.)
    #stock_button.click()
    #WebDriverWait(stock_buttons[0],20).until()
    time.sleep(20)
    button=driver.find_element_by_link_text('Financial_News & Analysis')

    button.click()
    news_url=driver.current_url
    print(news_url)
    last_part=re.search('(?<={})'.format(source),news_url)
    print(last_part)
    links=[]
    if MAX_VALUE == None:
        buttons=driver.find_elements_by_class_name('pagination')
        title=buttons.get_attribute('title')
        print(title)
        #MAX_VALUE=

    print(MAX_VALUE)
    contador = 1
    while contador<=MAX_VALUE:
        try:
            #print(contador)
            # wait 10 seconds before looking for element
            element=WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.XPATH,"//button[@class='pagination sectected']")))
            # time.sleep(5)
            #print('el clickeable la pagina')
            element.click()
            #print('pasa por la pagina {}'.format(contador))
            # driver.implicitly_wait(30)
            page = bs(driver.page_source, 'lxml')
            body = page.find('body')
            # print(body)
            headline_article = body.find_all('article', class_='js-article-item articleItem ')
            # print(len(headline_link))
            for article in headline_article:
                link=article.find('a', class_='title')
                url=source+link.get('href')
                print(url)
                if url not in links:
                    links.append(url)

            if contador>=MAX_VALUE:
                break
            contador+=1
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,"//a[@class='pagination' href='{}/{}]".format(last_part,contador)))).click()

        except Exception as ex:
            print(ex)
            print('se fue al except')
            if contador<2:
                prueba = driver.find_element_by_id('_evidon_banner')
                #print(prueba.text)
                cookie_button=prueba.find_element_by_id("_evidon-decline-button")
                #print(cookie_button.text)
                cookie_button.click()
            time.sleep(random.randint(0,50))

            # else quit
    driver.quit()
    #print(len(links))

def convert_proxies(filename):
    f = open(filename, "r")
    proxies_array=[]
    for line in f.readlines():
        line=line.split('\n')
        proxies_array.append(line[0])
    f.close()
    return proxies_array


def goose_article_information(tmp):
    g=Goose({'browser_user_agent': 'Mozilla', 'parser_class':'lxml'})
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
    }
    g.config.http_headers=headers
    while True:
        try:
            article = g.extract(url=tmp)
            #print('supera el aricle')
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
        return None
    meta__description_gosse = article.meta_description
    authors_gooose = article.authors
    date_goose = article.publish_date
    meta_keywords_goose = article.meta_keywords
    info_goose = article.infos
    image_goose = article.top_image
    #aditional_data_gosse = article.additional_data
    final_url_goose = article.final_url
    final_url_goose_split = final_url_goose.split('/')
    source_article = final_url_goose_split[2]
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
            final_url_goose = article.final_url
            url.append(final_url_goose_split)
            final_url_goose_split = final_url_goose.split('/')
            source_article = final_url_goose_split[2]
            fuente.append(source_article)

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
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
    }
    #headers = {'content-type': 'application/json'}
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
            #print('2')
            cleaner.javascript = True
            #print('3')
            cleaner.style = True
            #print('4')
            article = newspaper.Article(url=url,config=config)
            #print('5')
            article.download()
            #print('6')
            if contador>3:
                return None,None,None
            #html = minify(article.html)
            #print('7')
            #html = cleaner.clean_html(html)
            #print('8')
            article.parse()
            #print('9')
            bool=False
            #print('el valor que no esta banneado es {}'.format(proxie_ports))
            article.nlp()
            #date = article.publish_date
            authors=article.authors
            image=article.top_image
            keywords = article.keywords
            return image,keywords,authors

        except Exception as ex:

            print(ex.args)
            contador+=1
            #if len(https_ip_addresses) == 1:
            #    return None
            #print('el valor que esta banneado es {}'.format(proxie_ports))
            #https_ip_addresses.remove(proxie_ports)
            ##Web scrapping method ### Sirve para que parezca mas humano scraper
            time_request = random.randint(0, 50)
            print('DORMIRA POR {} SEGUNDOS'.format(time_request))
            time.sleep(time_request)


#full_scrap_investing(stock_name='AAPL')