import requests
from lxml import html
from pprint import pprint
from pymongo import MongoClient


class News:
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/97.0.4692.99 Safari/537.36'}
        self.dom = html.fromstring(self.get_response_text(self.url))
        self.client = MongoClient('127.0.0.1', 27017)

    def get_response_text(self, url):
        response = requests.get(url, headers=self.headers)
        return response.text


class LentaNews(News):
    def __init__(self, url):
        super(LentaNews, self).__init__(url)
        self.db = self.client['News']

    def get_the_news(self, link):
        the_news = {}
        dom = html.fromstring(self.get_response_text(link))
        the_news['url'] = link
        the_news['time'] = dom.xpath('//time[contains(@class, "topic-header__time")]/text()')[0]
        print(the_news)

    def get_all_news(self):
        list_links = self.dom.xpath('//a[contains(@class, "_topnews")]/@href')
        for link in list_links:
            if link.startswith('http'):
                continue
            self.get_the_news(f'https://lenta.ru/{link}')


if __name__ == '__main__':
    lenta = LentaNews('https://lenta.ru/')
    lenta.get_all_news()
