from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time


chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
driver.implicitly_wait(10)

driver.get('https://www.mail.ru/')

elem = driver.find_element(By.CLASS_NAME, 'email-input')
elem.send_keys('study.ai_172@mail.ru')
elem = driver.find_element(By.XPATH, "//button[@data-testid='enter-password']")
elem.click()
elem = driver.find_element(By.CLASS_NAME, 'password-input')
elem.send_keys('NextPassword172#')
elem = driver.find_element(By.XPATH, "//button[@data-testid='login-to-mail']")
elem.click()

emails = driver.find_elements(By.XPATH, '//a[contains(@class, "js-letter-list-item")]')
for mail in emails:
    print(mail.get_attribute('href'))

print()