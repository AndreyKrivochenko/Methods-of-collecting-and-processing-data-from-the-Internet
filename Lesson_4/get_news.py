import pymongo
import requests
from lxml import html
from pprint import pprint
from pymongo import MongoClient, errors


class News:
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/97.0.4692.99 Safari/537.36'}
        self.dom = html.fromstring(self.get_response_text(self.url))
        self.client = MongoClient('127.0.0.1', 27017)
        self.db = self.client['News']

    def get_response_text(self, url):
        response = requests.get(url, headers=self.headers)
        return response.text

    @staticmethod
    def print_news(collection):
        for news in collection.find({}):
            pprint(news)

    @staticmethod
    def save_the_news(collection, news: dict):
        try:
            collection.insert_one(news)
        except errors.DuplicateKeyError:
            pass


class LentaNews(News):
    def __init__(self, url):
        super(LentaNews, self).__init__(url)
        self.collection = self.db.lenta
        self.collection.create_index([('url', pymongo.DESCENDING)], name='url_index', unique=True)

    def get_the_news(self, link: str):
        the_news = {}
        dom = html.fromstring(self.get_response_text(link))
        the_news['url'] = link
        the_news['time'] = dom.xpath('//time[contains(@class, "topic-header__time")]/text()')[0]
        the_news['name'] = dom.xpath('//h1//text()')[0]
        the_news['source'] = 'Lenta.Ru'
        self.save_the_news(self.collection, the_news)

    def get_all_news(self):
        list_links = self.dom.xpath('//a[contains(@class, "_topnews")]/@href')
        for link in list_links:
            if link.startswith('http'):
                continue
            self.get_the_news(f'https://lenta.ru/{link}')


class MailNews(News):
    def __init__(self, url):
        super(MailNews, self).__init__(url)
        self.collection = self.db.mail
        self.collection.create_index([('url', pymongo.DESCENDING)], name='url_index', unique=True)

    def get_the_news(self, link: str):
        the_news = {}
        dom = html.fromstring(self.get_response_text(link))
        the_news['url'] = link
        the_news['time'] = dom.xpath('//div[contains(@class, "article")]//@datetime')[0]
        the_news['name'] = dom.xpath('//h1/text()')[0]
        the_news['source'] = dom.xpath(
            '//div[contains(@class, "breadcrumbs_article")]//a[contains(@class, "link")]//text()'
        )[0]
        self.save_the_news(self.collection, the_news)

    def get_all_news(self):
        list_link = self.dom.xpath(
            '//div[contains(@class ,"daynews__item")]/a/@href | //ul[@data-module="TrackBlocks"]//a/@href'
        )
        for link in list_link:
            self.get_the_news(link)


if __name__ == '__main__':
    lenta = LentaNews('https://lenta.ru/')
    lenta.get_all_news()
    mail = MailNews('https://news.mail.ru/')
    mail.get_all_news()
    lenta.print_news(lenta.collection)
    mail.print_news(mail.collection)
