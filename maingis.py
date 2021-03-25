import csv
import re
import sqlite3
import time
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HEADERS = {
    'user-agent': 'значение'
}
HOST = 'https://2gis.ru/moscow/'  # здесь меняем домен при необходимости

DOMENS = ['.ru', '.рф', '.com', '.org', '.net', '.su', '.tel', '.pro']
conn = sqlite3.connect('names_2gis.db')
CSV_HEADERS = ['Название лида', 'Рубрика', 'Адрес', 'Кол-во филиалов', 'Рабочий телефон', 'Рабочий e-mail', 'Корпоративный сайт']
file_name = '2gis.csv'  # здесь можно поменять название файла csv


def selen(dr, url, pages, sess):
    dr.get(url)
    WebDriverWait(dr, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, '_euwdl0'))).click()
    rubrika = WebDriverWait(dr, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, '_1gsdvil7'))).get_attribute('value')
    print(rubrika)
    for i in range(pages):
        time.sleep(1)
        links = dr.find_elements_by_css_selector('a._vhuumw')
        for a in links:
            if re.search('/firm', a.get_attribute('href')):
                parse(a.get_attribute('href'), sess, rubrika)
        if i > 0:
            dr.find_elements_by_css_selector('div._n5hmn94')[1].click()
        else:
            dr.find_element_by_css_selector('div._n5hmn94').click()
    return


def parse(url, sess, category):
    time.sleep(1)
    resp = sess.get(url)
    if resp.status_code == 200:
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        inf = []
        lid_name = soup.find('h1', class_='_1r7sat2').text
        res = is_in_base(lid_name)
        if res == 'y':
            return
        print(lid_name)
        inf.append(lid_name)
        inf.append(category)
        address = 'Отсутствует'
        address1 = soup.find_all('span', class_='_er2xx9')
        for adr in address1:
            try:
                address = adr.find('a', class_='_ke2cp9k').text.replace('\u200b', '')
            except:
                pass
        print(address)
        inf.append(address)
        filial = None
        for add in address1:
            if re.search('филиал', add.text):
                filial = add.text.replace('\u200b', '').split()[0]
                print(filial)
        inf.append(filial)
        try:
            tel = soup.find('div', class_='_b0ke8').find('a', class_='_ke2cp9k').get('href').replace('tel:', '')
            print(tel)
        except:
            tel = None
        inf.append(tel)
        a_s = soup.find_all('a', class_='_ke2cp9k')
        mail = None
        for a in a_s:
            if re.search('mailto', a.get('href')):
                mail = a.get('href')
        inf.append(mail)
        divs = soup.find_all('div', class_='_49kxlr')
        site = None
        for div in divs:
            try:
                vhuumw = div.find('a', class_='_vhuumw').text
                for domen in DOMENS:
                    if re.search(domen, vhuumw):
                        print(vhuumw)
                        site = vhuumw
                        break
            except AttributeError:
                pass
        inf.append(site)
        if inf is not []:
            w_to_cvs(inf)
    else:
        print(resp.status_code)
    return


def is_in_base(name1):
    cur = conn.cursor()
    cur.execute("SELECT Name FROM Nazvaniye")
    names = cur.fetchall()
    for name in names:
        if name[0] == name1:
            return 'y'
    cur.execute("INSERT INTO Nazvaniye VALUES (?, ?)", (name1, name1))
    conn.commit()
    return 'no'


def add_headers_to_cvs():
    try:
        with open(file_name, 'r+') as file:
            file_reader = csv.reader(file)
            i = 0
            for row in file_reader:
                i += 1
            if i == 0:
                file_writer = csv.writer(file, delimiter=';')
                file_writer.writerows([CSV_HEADERS])
    except FileNotFoundError:
        file = open(file_name, 'w')
        file_writer = csv.writer(file, delimiter=';')
        file_writer.writerows([CSV_HEADERS])
        file.close()
    return


def w_to_cvs(array):
    with open(file_name, "a", newline='') as file:  # тут можно поменять название csv файла
        writer = csv.writer(file, delimiter=';')
        print(array)
        writer.writerows([array])


if __name__ == '__main__':
    driver = webdriver.Chrome(
        executable_path='сюда полный путь до хромдрайвера')
    link = input('Введите ссылку:')
    quantity = int(input('Введите кол-во страниц:'))
    session = requests.session()
    session.headers = HEADERS
    add_headers_to_cvs()
    selen(driver, link, quantity, session)

