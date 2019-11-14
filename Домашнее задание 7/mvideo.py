from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pprint import pprint
import time

# Запишем исходные данные
main_link = 'https://www.mvideo.ru/'

# Создадим экземпляр хромопшенс
chrome_options = Options()
chrome_options.add_argument('start-maximized')
# chrome_options.add_argument('--headless')
print('Создали экземпляр Хромопшенс')

# Запустим вэбдрайвер
driver = webdriver.Chrome(options=chrome_options)
driver.get(main_link)
assert "М.Видео - интернет-магазин цифровой и бытовой техники и электроники, низкие цены, большой каталог, отзывы." in driver.title
print('Запустили Вэбдрайвер')

# Подождем, пока появится кликабельный элемент
try:
    button = WebDriverWait(driver, 5).until(
                ec.element_to_be_clickable((By.CLASS_NAME, 'PushTip-button'))
    )
    button.send_keys(Keys.RETURN)
except Exception as e:
    # Если кнопка не найдена - понятно, что дальше продолжать не можем
    print(e)

# Находим и нажимаем последнюю кнопку в перечне Хитов продаж
last_button = len(driver.find_elements_by_xpath(
    '/html[1]/body[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/a'))
button = driver.find_element_by_xpath(
    f'/html[1]/body[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/a[{last_button}]')
button.click()

# Вычислим кол-во товаров в перечне Хитов продаж на сайте
n_hits = 0
while True:
    k_hits = len(driver.find_elements_by_xpath(
        '/html[1]/body[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/ul/li'))
    if n_hits >= k_hits:
        break
    n_hits = k_hits
    time.sleep(2)

# Сформируем список Хитов продаж для занесения в БД
print('Сформируем список Хитов продаж для занесения в БД')
hits = []
for i in range(k_hits):
    hit = {}
    link_to_li = f'//div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/ul/li[{i + 1}]'
    title = driver.find_element_by_xpath(f'{link_to_li}//h4').get_attribute('title')
    prc = driver.find_element_by_xpath(f'{link_to_li}//div[@class="c-pdp-price__current"]')
    price = int(''.join(filter(str.isdigit, prc.get_attribute('innerHTML'))))
    link = driver.find_element_by_xpath(f'{link_to_li}//h4/a').get_attribute('href')
    hit['title'] = title
    hit['price'] = price
    hit['link'] = link
    hits.append(hit)

pprint(hits)
print(f'Найдено {len(hits)} товаров в разделе "Хиты продаж"')
driver.quit()
print('Приложение завершило работу')
