"""
1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные
о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from pprint import pprint


# Запишем исходные данные
main_link = 'https://mail.ru/'
login = 'study.ai_172@mail.ru'
password = 'Password172'
print('Считали исходные данные')

# Создадим экземпляр хромопшенс
chrome_options = Options()
chrome_options.add_argument('start-maximized')
# chrome_options.add_argument('--headless')
print('Создали экземпляр Хромопшенс')

# Запустим вэбдрайвер
driver = webdriver.Chrome(options=chrome_options)
driver.get(main_link)
assert "Mail.ru: почта, поиск в интернете, новости, игры" in driver.title
print('Запустили Вэбдрайвер')

# Пройдем авторизацию
# Введем логин
elem = driver.find_element_by_id('mailbox:login')
elem.send_keys(login)
elem.send_keys(Keys.RETURN)
assert "Mail.ru: почта, поиск в интернете, новости, игры" in driver.title
print('Ввели логин')
time.sleep(2)

# Введем пароль
elem = driver.find_element_by_id('mailbox:password')
elem.send_keys(password)
elem.send_keys(Keys.RETURN)
time.sleep(2)
assert "Почта Mail.ru" in driver.title
print('Ввели пароль')

button = WebDriverWait(driver, 5).until(
    ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Рассылки'))
)
button.click()
time.sleep(2)

pages = 1
n_letters = 0
while True:
    try:
        print(f'Открыли {pages} страницу')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        k_letters = driver.find_elements_by_class_name('js-letter-list-item')
        if n_letters == k_letters:
            break
        n_letters = k_letters
        pages += 1
    except Exception as e:
        # print(e)
        print(f'Обработано {pages} страниц')
        break

time.sleep(2)
letters = driver.find_elements_by_class_name('js-letter-list-item')
try:
    letters_list = []
    for letter in letters:
        letter_data = {}
        letter_data['sender'] = letter.find_element_by_class_name('ll-crpt').get_attribute('title')
        letter_data['subject'] = letter.find_element_by_class_name('ll-sj__normal').text
        letter_data['text'] = letter.find_element_by_class_name('ll-sp__normal').text
        letter_data['link'] = letter.get_attribute('href')
        letters_list.append(letter_data)
except Exception as e:
    print(e)
    driver.quit()

pprint(letters_list)
driver.quit()
print('Приложение завершило работу')
