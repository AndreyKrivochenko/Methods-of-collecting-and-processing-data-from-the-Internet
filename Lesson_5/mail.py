from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import time


class GetMail:
    def __init__(self, driver: webdriver, client: MongoClient):
        self.__driver = driver
        self.__db = client['MailRu']
        self.__links = set()
        self.__collection = self.__db.mail
        self.__driver.get('https://www.mail.ru/')

    def print_mails(self):
        for mail in self.__collection.find({}):
            pprint(mail)

    def __save_the_mail(self, mail: dict):
        self.__collection.insert_one(mail)

    def login(self, username: str, password: str):
        self.__driver.find_element(By.CLASS_NAME, 'email-input').send_keys(username)
        self.__driver.find_element(By.XPATH, "//button[@data-testid='enter-password']").click()
        self.__driver.find_element(By.CLASS_NAME, 'password-input').send_keys(password)
        self.__driver.find_element(By.XPATH, "//button[@data-testid='login-to-mail']").click()

    def __get_mail_links(self):
        last_elem = None

        # Код ниже я бы не запускал, будет долго, он собирает ссылки на все письма (540 писем), для проверки можно
        # раскомментировать цикл for
        while True:
            emails = self.__driver.find_elements(By.XPATH, '//a[contains(@class, "js-letter-list-item")]')

            for mail in emails:
                self.__links.add(mail.get_attribute('href'))

            if last_elem == emails[-1]:
                break
            else:
                last_elem = emails[-1]

            actions = ActionChains(driver)
            actions.move_to_element(last_elem)
            actions.perform()
            time.sleep(2)
        # for _ in range(2):
        #     emails = self.__driver.find_elements(By.XPATH, '//a[contains(@class, "js-letter-list-item")]')
        #
        #     for mail in emails:
        #         self.__links.add(mail.get_attribute('href'))
        #
        #     actions = ActionChains(self.__driver)
        #     actions.move_to_element(emails[-1])
        #     actions.perform()
        #     time.sleep(2)
        return self.__links

    def get_mails(self):
        self.__get_mail_links()
        for link in self.__links:
            mail = dict()
            self.__driver.get(link)
            mail['contact'] = self.__driver.find_element(By.CLASS_NAME, 'letter-contact').get_attribute('title')
            mail['body'] = self.__driver.find_element(By.CLASS_NAME, 'letter-body').text
            mail['subject'] = self.__driver.find_element(By.CLASS_NAME, 'thread-subject').text
            mail['date'] = self.__driver.find_element(By.CLASS_NAME, 'letter__date').text
            self.__save_the_mail(mail=mail)


if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("start-maximized")

    driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
    driver.implicitly_wait(10)

    client = MongoClient('127.0.0.1', 27017)

    mails = GetMail(driver=driver, client=client)
    mails.login('study.ai_172@mail.ru', 'NextPassword172#')
    mails.get_mails()
    mails.print_mails()
