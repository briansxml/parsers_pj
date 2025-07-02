import csv
import os
import re

import requests
from bs4 import BeautifulSoup
import lxml

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}


def get_psautomation(lang='en'):
    with open('ps-automation.csv' if lang != 'ru' else 'ps-automation_ru.csv', 'w', newline='',
              encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow((
            '_CATEGORY_',
            '_NAME_',
            '_DESCRIPTION_',
            '_IMAGE_',
            '_IMAGES_',
            '_ATTRIBUTES_',
            '_DOWNLOADS_',
            '_SKU_',
            '_URL_')
        )

    # with open('page.html', 'w', encoding='utf-8') as f:
    #     f.write(requests.get('https://www.ps-automation.com/?lang=en', headers=headers).text)
    # with open('page.html', 'r', encoding='utf-8') as f:
    #     src = f.read()
    # soup = BeautifulSoup(src, 'lxml')
    # categories = [i['href'] for i in soup.find('ul', class_='sub-menu elementor-nav-menu--dropdown').find_all('a')]
    # for i in categories:
    #     if i != 'https://www.ps-automation.com/product-configurator/?lang=en':
    #         res = requests.get(i, headers=headers)
    #         with open(f'categories/{i.split("/")[-2]}.html', 'w', encoding='utf-8') as f:
    #             f.write(res.text)
    for i in os.listdir('categories'):
        with open(f'categories/{i}', 'r', encoding='utf-8') as f:
            src = f.read()
        soup = BeautifulSoup(src, 'lxml')
        if lang == 'ru':
            products = [
                i['href'].replace('=en', '=ru') if i['href'].startswith('https') else 'https://www.ps-automation.com' +
                                                                                      i['href'].replace('=en', '=ru')
                for
                i in soup.find_all('a', class_='elementor-button elementor-button-link elementor-size-sm')[1:]]
        else:
            products = [i['href'] if i['href'].startswith('https') else 'https://www.ps-automation.com' + i['href'] for
                        i in soup.find_all('a', class_='elementor-button elementor-button-link elementor-size-sm')[1:]]
        category = soup.find('title').string.split(' - ')[0] if lang != 'ru' else \
            BeautifulSoup(requests.get(f'https://www.ps-automation.com/products/{i[:-5]}/?lang=ru').text, 'lxml').find(
                'title').string.split(' - ')[0]
        for j in products:
            src = requests.get(j, headers=headers).text
            soup = BeautifulSoup(src, 'lxml')
            title = soup.find_all('h2', class_=re.compile('elementor-heading-title'))[1].string.strip()
            if len(soup.find_all('div', class_=re.compile('elementor-widget elementor-widget-text-editor'))) == 3 or (
                    len(soup.find_all('div', class_=re.compile(
                            'elementor-widget elementor-widget-text-editor'))) == 4 and soup.find('table')):
                description = soup.find_all('div', class_=re.compile('elementor-widget elementor-widget-text-editor'))[
                    1].text.strip().replace('\n', ' ')
            else:
                description = soup.find_all('div', class_=re.compile('elementor-widget elementor-widget-text-editor'))[
                    2].text.strip().replace('\n', ' ')
            img = soup.find_all('div', class_=re.compile('elementor-widget elementor-widget-image'))[3].find('img')[
                'data-src']
            attr = []
            if soup.find('table'):
                names = [i.string for i in
                         soup.find('div', class_='elementor-container elementor-column-gap-no').find_all('b')]
                for row in soup.find('table').find_all('tr'):
                    parametrs = [k.text.strip() for k in row.find_all('td')]
                    attr.append(
                        f'TECHNICAL DATA | {parametrs[0]} | {parametrs[1]} | {parametrs[2]} | {parametrs[3]} | {parametrs[4]}' if lang != 'ru' else f'ТЕХНИЧЕСКИЕ Данные | {parametrs[0]} | {parametrs[1]} | {parametrs[2]} | {parametrs[3]} | {parametrs[4]}')
            downloads = []
            downloads_cards = soup.find('section', {'data-class': re.compile('elementor-download-content')})
            if downloads_cards:
                for k in downloads_cards.find_all('div', class_=re.compile(
                        'elementor-column elementor-col-33 elementor-top-column elementor-element')):
                    if 'There are no downloads for this category yet' in k.text or 'Для этой категории пока нет загрузок' in k.text:
                        continue
                    card_name = k.find('h2').string.strip()
                    for row in k.find_all('div', class_='elementor-row')[1:]:
                        name = row.find_all('p')[0].string.strip()
                        date = row.find_all('p')[1].string.strip()
                        download = row.find('a')['href']
                        downloads.append(f'{card_name} | {name} | {date} | {download}')

            print(f'Category: {category}')
            print(f'Title: {title}')
            print(f'Description: {description}')
            print(f'Image: {img}')
            print(f'Attributes: {", ".join(attr)}')
            print(f'Downloads: {", ".join(downloads)}')
            print(f'SKU: {j.split("/")[-2]}')
            print(f'URL: {j}')
            print()

            with open('ps-automation.csv' if lang != 'ru' else 'ps-automation_ru.csv', 'a', newline='',
                      encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow((
                    category,
                    title,
                    description,
                    img,
                    img,
                    "\n".join(attr),
                    "\n".join(downloads),
                    j.split("/")[-2],
                    j)
                )


if __name__ == '__main__':
    if not os.path.isdir('categories'):
        os.mkdir('categories')
    get_psautomation()
    get_psautomation('ru')
