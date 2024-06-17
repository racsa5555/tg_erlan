import requests
import json
import pprint
import time
import uuid
from pytz import timezone
from datetime import datetime,timedelta
from selenium import webdriver
from bs4 import BeautifulSoup as BS
from core.db import SessionLocal
from models.models import ParsedNews,SmiSource
from crud import create_news,get_or_create_smi_source



options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')

MONTH = {'января':1,
         'февраля':2,
         'марта':3,
         'апреля':4,
         'мая':5,
         'июня':6,
         'июля':7,
         'августа':8,
         'сентября':9,
         'октября':10,
         'ноября':11,
         'декабря':12}

def format_str_date(date_str):
    month = date_str.split()[1].lower()
    month_int = MONTH.get(month)
    day = date_str.split()[0]
    year = date_str.split()[2]
    date_str = f"{day}.{month_int}.{year}"
    date_format = "%d.%m.%Y"
    date_obj = datetime.strptime(date_str, date_format)
    return date_obj

def get_bs(url):
    response = requests.get(url)
    bs = BS(response.text,'html.parser')
    return bs

def get_need_times(times):
    time_now = datetime.now()
    threshold = timedelta(hours=2)
    res = []
    for time in times:
        if time_now - time <= threshold:
            res.append(time)
    return res


def get_interfax():
    result = []
    URL = 'https://www.interfax.ru/business/'
    smi_source = get_or_create_smi_source(URL)
    bs = get_bs(URL)
    base_url = 'https://www.interfax.ru'
    block = bs.find(class_ = 'leftside')
    time_elements = block.find_all('time')
    data = {}
    for el in time_elements:
        datetime_str = el['datetime']
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
        url = base_url + el.parent.find('a').get('href')
        data.setdefault(datetime_obj,url)
    times = get_need_times(data.keys())
    data_2 = dict(filter(lambda item: item[0] in times,data.items()))
    for time,link in data_2.items():
        bs = get_bs(link)
        title = bs.find('h1').text
        # print(title)
        try:
            title = title.encode('iso-8859-1').decode('windows-1251')
        except UnicodeEncodeError:
            title = title
        block = bs.find('article',{'itemprop': 'articleBody'})
        p_list = block.find_all('p')
        body_html = []
        for p in p_list:
            try:
                decoded_text = p.text.encode('iso-8859-1').decode('windows-1251')
                p.string = decoded_text  # Изменение текста внутри тега
                body_html.append(str(p))  
            except:
                body_html.append(str(p))
        body_str = ''.join(body_html)
        body = body_str
        time_publish = time.strftime("%Y-%m-%d %H:%M:%S")
        obj = ParsedNews(time_publish=time_publish,
                         title=title,
                         body=body,
                         source=link,
                         smi_source = smi_source)
        result.append(obj)
    # print(result)
    return result

# d = get_interfax()
# print(d)


def get_bankiru():
    URL = 'https://www.banki.ru/news/lenta/main/'
    smi_source = get_or_create_smi_source(URL)
    base_url = 'https://www.banki.ru'
    # driver = webdriver.Remote(
    # command_executor='http://localhost:4444/wd/hub',options = options)
    driver= webdriver.Chrome()

    driver.get(URL)
    time.sleep(3)
    html_content = driver.page_source
    bs = BS(html_content,'html.parser')
    bs2 = bs.find(class_ = 'NewsItemstyled__StyledNewsList-sc-jjc7yr-0 bfxqfY')
    blocks = bs2.find_all(class_ = 'NewsItemstyled__StyledItem-sc-jjc7yr-3 cCaQDP')
    data = {}
    date_str = bs2.find(class_ = 'NewsItemstyled__StyledNewsDate-sc-jjc7yr-1 klQjwz').text
    date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
    for el in blocks:
        time_ = el.find(class_ = 'NewsItemstyled__StyledInfoText-sc-jjc7yr-4 NewsItemstyled__StyledItemTime-sc-jjc7yr-5 cTGQyI hIxGhY').text
        time_obj = datetime.strptime(time_, "%H:%M").time()
        datetime_obj = datetime.combine(date_obj, time_obj)
        href = el.find('a').get('href')
        url = base_url + href
        data.setdefault(datetime_obj,url)
    # print(data)
    times = get_need_times(data.keys())
    data_2 = dict(filter(lambda item: item[0] in times,data.items()))
    # print(data_2)
    result = []
    for t,link in data_2.items():
        bs = get_bs(link)
        title = bs.find('h1').text
        block = bs.find('div',{'itemprop': 'articleBody'})
        p_list = block.find_all('p')
        p_list = [str(p) for p in p_list]
        body = ''.join(p_list)
        obj = ParsedNews(time_publish=t,
                         title=title,
                         body=body,
                         source=link,
                         smi_source = smi_source)
        result.append(obj)
    return result
        
# print(get_bankiru())

def get_vedomosti():
    URL = 'https://www.vedomosti.ru/'
    smi_source = get_or_create_smi_source(URL)
    base_url = 'https://www.vedomosti.ru'
    # driver = webdriver.Remote(
    # command_executor='http://localhost:4444/wd/hub',options = options)
    driver = webdriver.Chrome()
    driver.get(URL)
    time.sleep(4)
    html_content = driver.page_source
    bs = BS(html_content,'html.parser')
    block = bs.find(class_ = 'waterfall__transition')
    news = block.find_all('li',class_ = 'waterfall__item')
    date_str = bs.find(class_ = 'waterfall__date').text
    date_obj = format_str_date(date_str)
    data = {}
    for n in news:
        time_ = n.find(class_ = 'waterfall__item-meta').text.split()[0]
        time_obj = datetime.strptime(time_, "%H:%M").time()
        datetime_obj = datetime.combine(date_obj, time_obj)
        url = base_url + n.find('a').get('href')
        data.setdefault(datetime_obj,url)
        # print(data)
    times = get_need_times(data.keys())
    data_2 = dict(filter(lambda item: item[0] in times,data.items()))
    res = []
    for t,link in data_2.items():
        html_content = requests.get(link).text
        bs = BS(html_content,'html.parser')
        title = bs.find('h1').text
        block = bs.find(class_ = 'article-boxes-list article__boxes')
        p_list = block.find_all('p')
        p_list = [str(p) for p in p_list]
        body = ''.join(p_list)
        obj = ParsedNews(time_publish=t,
                         title=title,
                         body=body,
                         source=link,
                         smi_source = smi_source)
        res.append(obj)
    return res

# print(get_vedomosti())


def get_rbc_ru():
    URL = 'https://quote.rbc.ru/'
    smi_source = get_or_create_smi_source(URL)
    response = requests.get(URL)
    bs = BS(response.text,'html.parser')
    block = bs.find(class_ = 'js-news-feed-list')
    news = block.find_all('a',class_ = 'news-feed__item js-visited js-news-feed-item js-yandex-counter')
    date_obj = datetime.now().date()
    # print(date_obj)
    data = {}
    k = 0
    for n in news:
        try:
            if n.find('span', class_ = 'news-feed__item__date-text').text.split(', ')[0].split()[0] == str(date_obj.day):
                    
                    time_str = n.find('span', class_ = 'news-feed__item__date-text').text.split()[-1]
                    k +=1   
                    time_obj = datetime.strptime(time_str, "%H:%M").time()
                    datetime_obj = datetime.combine(date_obj, time_obj)
                    url = n.get('href')
                    data.setdefault(datetime_obj,url)
                    if k == 10:
                        break
        except AttributeError:
            continue
                    
    times = get_need_times(data.keys())
    data_2 = dict(filter(lambda item: item[0] in times,data.items()))
    res = []
    for t,link in data_2.items():
        # driver = webdriver.Remote(
        # command_executor='http://localhost:4444/wd/hub',options = options)
        driver = webdriver.Chrome()

        driver.get(link)
        time.sleep(2)
        html_content = driver.page_source

        bs = BS(html_content,'html.parser')
        try:
            title = bs.find('h1').text
            block = bs.find(class_ = 'article__text article__text_free js-article-text overflow-visible')
            p_list = block.find_all('p')
        except:
            continue
        p_list = [str(p) for p in p_list]
        body = ''.join(p_list)
        obj = ParsedNews(time_publish=t,
                         title=title,
                         body=body,
                         source=link,
                         smi_source = smi_source)
        res.append(obj)
    # driver.quit()
    return res
    
# print(get_rbc_ru())


def get_moex():
    URL = 'https://www.moex.com/ru/news/'
    smi_source = get_or_create_smi_source(URL)
    base_url = 'https://www.moex.com'
    # driver = webdriver.Remote(
    # command_executor='http://localhost:4444/wd/hub',options = options)
    driver = webdriver.Chrome()

    driver.get(URL)
    time.sleep(3)
    html_content = driver.page_source

    bs = BS(html_content,'html.parser')
    block = bs.find(class_ = 'new-moex-news-list')
    news = block.find_all(class_ = 'new-moex-news-list__record')
    data = {}
    for n in news:
        date_str = n.find(class_ = 'new-moex-news-list__date').text.strip()
        date_format = "%d.%m.%Y"
        date_obj = datetime.strptime(date_str, date_format)
        time_str = n.find(class_ = 'new-moex-news-list__time').text.strip()
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        datetime_obj = datetime.combine(date_obj, time_obj)
        url = base_url + n.find('a',class_ = 'new-moex-news-list__link').get('href')
        data.setdefault(datetime_obj,url)
    times = get_need_times(data.keys())
    data_2 = dict(filter(lambda item: item[0] in times,data.items()))   
    res = []
    for t,link in data_2.items():
        # driver = webdriver.Remote(
        # command_executor='http://localhost:4444/wd/hub',options = options)
        driver = webdriver.Chrome()

        driver.get(link)
        time.sleep(2)
        html_content = driver.page_source
        bs = BS(html_content,'html.parser')
        title = bs.find('h1').text
        p_list = bs.find(class_ = 'news_text').find_all('p')
        p_list = [str(p) for p in p_list]
        body = ''.join(p_list)
        obj = ParsedNews(time_publish=t,
                         title=title,
                         body=body,
                         source=link,
                         smi_source = smi_source)
        res.append(obj)
    # driver.quit()
    return res

# print(get_moex())


def get_komersant_economic():
    URL = 'https://www.kommersant.ru/rubric/3?from=burger'
    smi_source = get_or_create_smi_source(URL)
    bs = get_bs(URL)
    block = bs.find(class_ = 'rubric_lenta')
    news = block.find_all(class_ = 'uho rubric_lenta__item js-article')
    data = {}
    for n in news:
        url = n.get('data-article-url')
        date_str = n.find('p',class_ = 'uho__tag rubric_lenta__item_tag hide_mobile').text.split(', ')[0].strip()
        date_format = "%d.%m.%Y"
        date_obj = datetime.strptime(date_str, date_format)
        time_str = n.find(class_ = 'uho__tag rubric_lenta__item_tag hide_mobile').text.split(', ')[1].strip()
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        datetime_obj = datetime.combine(date_obj, time_obj)
        data.setdefault(datetime_obj,url)
    times = get_need_times(data.keys())
    data_2 = dict(filter(lambda item: item[0] in times,data.items()))
    res = []
    for t,link in data_2.items():
        response = requests.get(link)
        bs = BS(response.text,'html.parser')
        title = bs.find('h1').text
        p_list = bs.find(class_ = 'article_text_wrapper js-search-mark').find_all('p')
        p_list = [str(p) for p in p_list]
        body = ''.join(p_list)
        obj = ParsedNews(time_publish=t,
                         title=title,
                         body=body,
                         source=link,
                         smi_source = smi_source)

        res.append(obj)
    return res


def get_komersant_finance():
    URL = 'https://www.kommersant.ru/finance?from=burger'
    smi_source = get_or_create_smi_source(URL)
    bs = get_bs(URL)
    block = bs.find(class_ = 'rubric_lenta')
    news = block.find_all(class_ = 'uho rubric_lenta__item js-article')
    data = {}
    for n in news:
        url = n.get('data-article-url')
        date_str = n.find('p',class_ = 'uho__tag rubric_lenta__item_tag hide_mobile').text.split(', ')[0].strip()
        date_format = "%d.%m.%Y"
        date_obj = datetime.strptime(date_str, date_format)
        time_str = n.find(class_ = 'uho__tag rubric_lenta__item_tag hide_mobile').text.split(', ')[1].strip()
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        datetime_obj = datetime.combine(date_obj, time_obj)
        data.setdefault(datetime_obj,url)
    times = get_need_times(data.keys())
    data_2 = dict(filter(lambda item: item[0] in times,data.items()))
    res = []
    for t,link in data_2.items():
        response = requests.get(link)
        bs = BS(response.text,'html.parser')
        title = bs.find('h1').text
        p_list = bs.find(class_ = 'article_text_wrapper js-search-mark').find_all('p')
        p_list = [str(p) for p in p_list]
        body = ''.join(p_list)
        obj = ParsedNews(time_publish=t,
                         title=title,
                         body=body,
                         source=link,
                         smi_source = smi_source)

        res.append(obj)
    return res


def get_bks_express():
    URL = 'https://bcs-express.ru/'
    smi_source = get_or_create_smi_source(URL)
    # driver = webdriver.Remote(
    # command_executor='http://localhost:4444/wd/hub',options = options)
    driver = webdriver.Chrome()
    driver.get(URL)
    time.sleep(3)
    html_content = driver.page_source

    bs = BS(html_content,'html.parser')
    news = bs.find_all(class_ = 'GP6k')
    data = {}
    for n in news:
        day = n.find(class_ = 'H1Ik').text.split()[0]
        if day == 'Сегодня':
            time_str = n.find(class_ = 'H1Ik').text.split()[-1]
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            date_obj = datetime.now().date()
            datetime_obj = datetime.combine(date_obj, time_obj)
            url = n.find('a',class_ = 'WQEp').get('href')
            data.setdefault(datetime_obj,url)
    times = get_need_times(data.keys())
    data_2 = dict(filter(lambda item: item[0] in times,data.items()))
    res = []
    for t,link in data_2.items():
        # driver = webdriver.Remote(
        # command_executor='http://localhost:4444/wd/hub',options = options)
        driver = webdriver.Chrome()

        driver.get(link)
        time.sleep(2)
        html_content = driver.page_source
        # driver.quit()
        bs = BS(html_content,'html.parser')
        title = bs.find('h1').text
        block = bs.find(class_ = 'YjHz Y3Iz RkGZ')
        p_list = block.find_all('p')
        p_list = [str(p) for p in p_list]
        body = ''.join(p_list)
        obj = ParsedNews(time_publish=t,
                         title=title,
                         body=body,
                         source=link,
                         smi_source = smi_source)

        res.append(obj)
    return res

# print(get_bks_express())


def get_finam():
    URL = 'https://www.finam.ru/'
    smi_source = get_or_create_smi_source(URL)
    base_url = 'https://www.finam.ru/'
    driver = webdriver.Chrome()
    driver.set_window_size(1920,1080)
    driver.get(URL)
    time.sleep(2)
    html_content = driver.page_source
    bs = BS(html_content,'html.parser')
    block = bs.find(class_ = 'HomeDesktop__newsListContainer--13P')
    news = block.find_all(class_ = 'NewsItem__root--1p_')
    date_obj = datetime.now().date()
    data = {}
    for n in news[8]:
        try:
            time_str = n.find(class_ = 'Item__date--3Qz').text
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            datetime_obj = datetime.combine(date_obj, time_obj)
            url = base_url + n.find('xpath',".//a[text()='читать далее']").get('href')
            print(datetime_obj,url)
            data.setdefault(datetime_obj,url)
        except:
            print(n)
            continue
    times = get_need_times(data.keys())
    # print(data)
    data_2 = dict(filter(lambda item: item[0] in times,data.items()))
    res = []
    for t,link in data_2.items():
        driver = webdriver.Chrome()
        driver.get(link)
        time.sleep(2)
        html_content = driver.page_source
        bs = BS(html_content,'html.parser')
        title = bs.find('h1').text
        p_list = bs.find(class_ = 'mt2x p-margin font-xl').find_all('p')
        p_list = [str(p) for p in p_list]
        body = ''.join(p_list)
        obj = ParsedNews(time_publish=t,
                         title=title,
                         body=body,
                         source=link,
                         smi_source = smi_source)

        res.append(obj)
    return res
        

# print(get_finam())

def start_get_news():
    funcs = [get_interfax,get_bankiru,get_rbc_ru,get_vedomosti,get_moex,get_komersant_economic,get_komersant_finance,get_bks_express]
    for x in funcs:
        db = SessionLocal()
        mas = x()
        for obj in mas:
            create_news(db,obj)
        db.close()

# start_get_news()






print(datetime.now().strftime("%H:%M"))


    
    





    


    



