from textwrap import indent
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json


def get_compensations(compensation):
    if compensation:
        compensation = [item.strip() for item in compensation.getText().replace('\u202f', '').split('–')]
        if len(compensation) > 1:
            min_val = int(compensation[0])
            max_val = int(compensation[1].split()[0])
            currency = compensation[1].split()[1]
        else:
            compensation = compensation[0].split()
            if compensation[0] == 'от':
                min_val = int(compensation[1])
                max_val = None
            else:
                min_val = None
                max_val = int(compensation[1])
            currency = compensation[2]
    else:
        min_val = None
        max_val = None
        currency = None
    return min_val, max_val, currency


vacancy = 'python'

jobs = []
i = 0

while True:
    url = 'https://barnaul.hh.ru/search/vacancy'
    params = {
        'area': 113,
        'text': vacancy,
        'schedule': 'remote',
        'search_field': 'name',
        'search_field': 'company_name',
        'search_field': 'description',
        'page': i,
        'hhtmFrom': 'vacancy_search_list'
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}

    response = requests.get(url, params=params, headers=headers)

    dom = BeautifulSoup(response.text, 'html.parser')

    vacancy_list = dom.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancy_list:
        vacancy_data = {}
        vacancy_data['compensation'] = {}

        link_name = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        vacancy_data['name'] = link_name.getText()
        vacancy_data['url'] = link_name.get('href').split('?')[0]
        compensation = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})

        vacancy_data['compensation']['min'], vacancy_data['compensation']['max'], vacancy_data['compensation']['currency'] = get_compensations(compensation)
        

        jobs.append(vacancy_data)
    
    btn_next = dom.find('a', {'data-qa': 'pager-next'})

    if btn_next:
        i += 1
    else:
        break

with open('jobs.json', 'w', encoding='utf-8') as f:
    json.dump(jobs, f, indent=4)

pprint(len(jobs))
