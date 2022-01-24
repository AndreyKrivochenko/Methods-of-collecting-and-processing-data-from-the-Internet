import requests
from bs4 import BeautifulSoup
import pandas as pd
import json


def get_compensations(compensation):
    if compensation:
        compensation = [
            item.strip() for item in compensation.getText().replace('\u202f', '').split('–')
        ]
        if len(compensation) == 1:
            compensation = [
                item.strip() for item in compensation[0].replace('&nbsp;', '').replace('\xa0', ' ').split('—')
            ]
    if compensation and compensation[0] != 'По договорённости':
        if len(compensation) > 1:
            min_val = int(compensation[0].replace(' ', ''))
            max_val = int(compensation[1].rsplit(maxsplit=1)[0].replace(' ', ''))
            currency = compensation[1].rsplit(maxsplit=1)[1]
        else:
            compensation = compensation[0].split(maxsplit=1)
            if compensation[0] == 'от':
                min_val = int(compensation[1].rsplit(maxsplit=1)[0].replace(' ', ''))
                max_val = None
            else:
                min_val = None
                max_val = int(compensation[1].rsplit(maxsplit=1)[0].replace(' ', ''))
            currency = compensation[1].rsplit(maxsplit=1)[1]
    else:
        min_val = None
        max_val = None
        currency = None
    return min_val, max_val, currency


def get_jobs_hh(vacancy_name: str) -> list:
    hh = []
    i = 0

    while True:
        url = 'https://barnaul.hh.ru/search/vacancy'
        params = {
            'area': 113,
            'text': vacancy_name,
            'schedule': 'remote',
            'search_field': 'name&search_field=company_name&search_field=description',
            'page': i
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}

        response = requests.get(url, params=params, headers=headers)

        dom = BeautifulSoup(response.text, 'html.parser')

        vacancy_list = dom.find_all('div', {'class': 'vacancy-serp-item'})

        for vac in vacancy_list:
            vacancy_data = {'compensation': {}}

            link_name = vac.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
            vacancy_data['site'] = 'hh.ru'
            vacancy_data['name'] = link_name.getText()
            vacancy_data['url'] = link_name.get('href').split('?')[0]
            compensation = vac.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})

            vacancy_data['compensation']['min'], vacancy_data['compensation']['max'], vacancy_data['compensation'][
                'currency'] = get_compensations(compensation)

            hh.append(vacancy_data)

        btn_next = dom.find('a', {'data-qa': 'pager-next'})

        if btn_next:
            i += 1
        else:
            break
    return hh


def get_jobs_superjob(vacancy_name: str) -> list:
    # https: // russia.superjob.ru / vacancy / search /?keywords = python & page = 1
    superjob = []
    i = 1

    while True:
        url = 'https://russia.superjob.ru'
        params = {
            'keywords': vacancy_name,
            'page': i
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}

        response = requests.get(url + '/vacancy/search/', params=params, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        vacancy_list = dom.find_all('div', {'class': 'f-test-vacancy-item'})

        for vac in vacancy_list:
            vacancy_data = {'compensation': {}}
            link_name = vac.find('a', {'class': 'icMQ_'})
            vacancy_data['site'] = 'superjob.ru'
            vacancy_data['name'] = link_name.getText()
            vacancy_data['url'] = url + link_name.get('href').split('?')[0]
            compensation = vac.find('span', {'class': 'f-test-text-company-item-salary'}).find('span')
            vacancy_data['compensation']['min'], vacancy_data['compensation']['max'], vacancy_data['compensation'][
                'currency'] = get_compensations(compensation)

            superjob.append(vacancy_data)

        btn_next = dom.find('a', {'rel': 'next'})
        if btn_next:
            i += 1
        else:
            break

    return superjob


if __name__ == '__main__':
    jobs = []
    vacancy = 'django'
    hh_jobs = get_jobs_hh(vacancy)
    jobs.extend(hh_jobs)
    sj_jobs = get_jobs_superjob(vacancy)
    jobs.extend(sj_jobs)

    with open('jobs.json', 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=4)

    with open('jobs.json', 'r', encoding='utf-8') as f:
        json_data = json.load(fp=f)

    pd.options.display.max_rows = 200
    pd.options.display.max_columns = 5
    pd.options.display.width = 2000
    df = pd.DataFrame(data=json_data, columns=('name', 'compensation', 'site', 'url'))
    print(df)
