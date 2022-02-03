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

driver.get('https://www.mvideo.ru/')

elem = driver.find_element(By.CLASS_NAME, 'logo')
elem.send_keys(Keys.PAGE_DOWN)

# elem = driver.find_elements(By.XPATH, '//mvid-carousel[@class="ng-star-inserted"]')
# elem[1].send_keys(Keys.PAGE_DOWN)
print()
