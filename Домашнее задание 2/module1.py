from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import time

headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

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
                    salary_min=0
                    salary_max=0
                else:
                    salary=salary.getText().replace(u'\xa0', u' ')
                    salaries=salary.split('-')
                    salary_min=salaries[0]
                    if len(salaries)>1:
                        salary_max=salaries[1]
                    else:
                        salary_max=''
                job_data['name'] = job_name
                job_data['salary_min'] = salary_min
                job_data['salary_max'] = salary_max
                job_data['link'] = job_link
                job_data['site'] = main_link
                jobs.append(job_data)
        time.sleep(1)
        next_btn_block=parsed_html.find('a',{'class':'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
        next_btn_link=next_btn_block['href']
        html = requests.get(main_link+next_btn_link,headers=headers).text
        parsed_html = bs(html,'lxml')

    pprint(jobs)



def superjob(main_link, search_str, n_str):
    #n_str - кол-во просматриваемых страниц
    html = requests.get(main_link+'/vacancy/search/?keywords='+search_str+'&geo%5Bc%5D%5B0%5D=1',headers=headers).text
    parsed_html = bs(html,'lxml')

    jobs = []
    for i in range(n_str):
        jobs_block = parsed_html.find('div',{'class':'_1ID8B'})
        jobs_list = jobs_block.findChildren(recursive=True)
        for job in jobs_list:
            job_data={}
            req=job.find('div',{'class':'_3syPg _1_bQo _2FJA4'})
            if req!=None:
                main_info = req.findChild()
                try:
                    job_link = main_info['href']
                except:
                    job_link = ''
                job_name = main_info.getText()
                salary = job.find('span',{'class':'_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'})
                if not salary:
                    salary_min=0
                    salary_max=0
                else:
                    salary=salary.getText().replace(u'\xa0', u' ')
                    salaries=salary.split('-')
                    salary_min=salaries[0]
                    if len(salaries)>1:
                        salary_max=salaries[1]
                    else:
                        salary_max=''
                job_data['name'] = job_name
                job_data['salary_min'] = salary_min
                job_data['salary_max'] = salary_max
                job_data['link'] = job_link
                job_data['site'] = main_link
                jobs.append(job_data)
        time.sleep(1)
        next_btn_block=parsed_html.find('a',{'rel':'next'})
        next_btn_link=next_btn_block['href']
        html = requests.get(main_link+next_btn_link,headers=headers).text
        parsed_html = bs(html,'lxml')

    pprint(jobs)


hh('https://ufa.hh.ru','Python',3)
superjob('https://www.superjob.ru','Python',3)