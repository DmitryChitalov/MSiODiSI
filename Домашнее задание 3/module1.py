from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import time
import re
from pymongo import MongoClient
import random

#headers = {#'accept':'*/*',
#            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

headers = {'User-agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36'}

def hh(main_link, search_str, n_str):
    #n_str - кол-во просматриваемых страниц
    html = requests.get(main_link+'/search/vacancy?clusters=true&enable_snippets=true&text='+search_str+'&showClusters=true',headers=headers).text
    parsed_html = bs(html,'lxml')

    jobs = []
    for i in range(n_str):
        jobs_block = parsed_html.find('div',{'class':'vacancy-serp'})
        jobs_list = jobs_block.findChildren(recursive=False)
        for job in jobs_list:
            job_data={}
            req=job.find('span',{'class':'g-user-content'})
            if req!=None:
                main_info = req.findChild()
                job_name = main_info.getText()
                job_link = main_info['href']
                salary = job.find('div',{'class':'vacancy-serp-item__compensation'})
                if not salary:
                    salary_min=None
                    salary_max=None
                else:
                    salary=salary.getText().replace(u'\xa0', u'')
                    salaries=salary.split('-')
                    salaries[0] = re.sub(r'[^0-9]', '', salaries[0])
                    salary_min=int(salaries[0])
                    if len(salaries)>1:
                        salaries[1] = re.sub(r'[^0-9]', '', salaries[1])
                        salary_max=int(salaries[1])
                    else:
                        salary_max=None
                job_data['name'] = job_name
                job_data['salary_min'] = salary_min
                job_data['salary_max'] = salary_max
                job_data['link'] = job_link
                job_data['site'] = main_link
                jobs.append(job_data)
        time.sleep(random.randint(1,10))
        next_btn_block=parsed_html.find('a',{'class':'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
        next_btn_link=next_btn_block['href']
        html = requests.get(main_link+next_btn_link,headers=headers).text
        parsed_html = bs(html,'lxml')

    #pprint(jobs)
    jobs_db.insert_many(jobs)
    return jobs



def superjob(main_link, search_str, n_str):
    #n_str - кол-во просматриваемых страниц
    base_url=main_link+'/vacancy/search/?keywords='+search_str+'&geo%5Bc%5D%5B0%5D=1'
    jobs = []
    session = requests.Session()
    for i in range(n_str):
        request = session.get(base_url, headers=headers)
        if request.status_code == 200:
            soup = bs(request.content, 'lxml')
            divs = soup.find_all('div', {'class':'_3zucV _2GPIV f-test-vacancy-item i6-sc _3VcZr'})
            for div in divs:
                title = div.find('div', {'class': '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).text
                href = div.find('div', {'class': '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).findParent()['href']
                salary = div.find('span', {'class': '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'}).text
                salary=salary.replace(u'\xa0', u'')
                if '—' in salary:
                    salary_min = salary.split('—')[0]
                    salary_min = re.sub(r'[^0-9]', '', salary_min)
                    salary_max = salary.split('—')[1]
                    salary_max = re.sub(r'[^0-9]', '', salary_max)
                    salary_min = int(salary_min)
                    salary_max = int(salary_max)
                elif 'от' in salary:
                    salary_min = salary[2:]
                    salary_min = re.sub(r'[^0-9]', '', salary_min)
                    salary_min = int(salary_min)
                    salary_max = None
                elif 'договорённости' in salary:
                    salary_min = None
                    salary_max = None
                elif 'до' in salary:
                    salary_min = None
                    salary_max = salary[2:]
                    salary_max = re.sub(r'[^0-9]', '', salary_max)
                    salary_max = int(salary_max)
                else:
                    salary_min = int(re.sub(r'[^0-9]', '', salary))
                    salary_max = int(re.sub(r'[^0-9]', '', salary))

                jobs.append({
                    'title': title,
                    'href': 'https://www.superjob.ru'+href,
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'link': main_link
                })
            base_url = main_link + \
                       soup.find('a', {'class': 'icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-dalshe'})['href']
            time.sleep(random.randint(1,10))
        else:
            print('Ошибка')

    #pprint(jobs)
    jobs_db.insert_many(jobs)
    return jobs

def insert_data_to_db(search_str, n_str):
    jobs_db.delete_many({})
    jobs_db.insert_many(hh('https://ufa.hh.ru', search_str, n_str))
    jobs_db.insert_many(superjob('https://www.superjob.ru', search_str, n_str))

def find_salaries_greater_than(salary_greater_than):
    return jobs_db.find({'salary_greater_than': {'$gte': salary_greater_than}})

client = MongoClient('localhost',27017)
db = client['jobs_db']
jobs_db = db.jobs_db
search_str='Python'
salary_greater_than=65000
n_str=2

#hh('https://ufa.hh.ru',search_str,n_str)
#superjob('https://www.superjob.ru',search_str,n_str)

insert_data_to_db(search_str, n_str)
records_db=find_salaries_greater_than(salary_greater_than)

for rec in records_db:
    pprint(rec)

count = jobs_db.count()
print('Кол-во записей в БД:', count)