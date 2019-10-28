from pprint import pprint
from datetime import datetime
from lxml import html
import requests
header={'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 '
          'Safari/537.36'}

def requests_to_mail():
    main_link='https://mail.ru/'
    req=requests.get(main_link, headers=header)
    root=html.fromstring(req.text)
    news_list=[]

    #Распарсим главную новость
    title=root.xpath("//div[@class='news-item o-media "
                       "news-item_media news-item_main']//h3/text()")
    if title:
        link=root.xpath("//div[@class='news-item o-media news-item_media "
                          "news-item_main']//a/@href")
        news_dict=dict()
        news_dict['site']=main_link
        news_dict['title']=title[0].replace(u'\xa0', u' ')
        news_dict['link']=link[0]
        news_dict['time']=datetime.now().strftime("%d-%m-%Y %H:%M")
        news_list.append(news_dict)
    else:
        print('Main news not found on mail.ru')

    #Распарсим остальные новости
    titles=root.xpath("//div[@class='news-item__inner']/a[not(contains(@class,"
                        " 'i-color-black i-inline'))]/text()")
    if len(titles)>0:
        links=root.xpath("//div[@class='news-item__inner']/a[not(contains"
                           "(@class, 'i-color-black i-inline'))]/@href")
        for i in range(len(links)):
            news_dict=dict()
            news_dict['site']=main_link
            news_dict['title']=titles[i].replace(u'\xa0', u' ')
            news_dict['link']=links[i]
            news_dict['time']=datetime.now().strftime("%d-%m-%Y %H:%M")
            news_list.append(news_dict)
    else:
        print('News not found on mail.ru')

    #Выведем результат на экран
    pprint(news_list)


def requests_to_lenta():
    main_link='https://lenta.ru/'
    req=requests.get(main_link, headers=header)
    root=html.fromstring(req.text)
    news_list=[]

    #Распарсим главную новость
    title=root.xpath("//div[@class='first-item']//h2/a/text()")
    if title:
        link=root.xpath("//div[@class='first-item']//h2/a/@href")
        news_dict=dict()
        news_dict['site']=main_link
        news_dict['title']=title[0].replace(u'\xa0', u' ')
        news_dict['link']=link[0]
        news_dict['time']=root.xpath("//div[@class='first-item']//h2/a/time/text()")
        news_list.append(news_dict)
    else:
        print('Main news not found on lenta.ru')

    #Распарсим остальные новости
    titles=root.xpath("//section[@class='row b-top7-for-main js-top-seven']"
                      "//div[@class='item']//a/text()")
    if len(titles)>0:
        links=root.xpath("//section[@class='row b-top7-for-main js-top-seven']"
                         "//div[@class='item']//a/@href")
        for i in range(len(links)):
            news_dict=dict()
            news_dict['site']=main_link
            news_dict['title']=titles[i].replace(u'\xa0', u' ')
            news_dict['link']=links[i]
            news_dict['time']=datetime.now().strftime("%d-%m-%Y %H:%M")
            news_list.append(news_dict)
    else:
        print('News not found on lenta.ru')

    #Выведем результат на экран
    pprint(news_list)


requests_to_mail()
requests_to_lenta()


