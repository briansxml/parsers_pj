import csv
import os
import re
from itertools import product

import requests
from bs4 import BeautifulSoup
import lxml

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}


def get_verderliquids():
    # with open('catalogs.html', 'w', encoding='utf-8') as f:
    #     f.write(requests.get('https://www.verderliquids.com/int/en/verder-pumps-hygienic-industrial', headers=headers).text)
    # with open('catalogs.html', 'r', encoding='utf-8') as f:
    #     soup = BeautifulSoup(f, 'lxml')
    #     catalogs = ['https://www.verderliquids.com' + i.find('a')['href'] for i in soup.find_all('article')]
    # for i in catalogs:
    #     with open(f'categories/{i.split("/")[-1]}.html', 'w', encoding='utf-8') as f:
    #         f.write(requests.get(i, headers=headers).text)
    # for i in os.listdir('categories'):
    #     with open(f'categories/{i}', 'r', encoding='utf-8') as f:
    #         soup = BeautifulSoup(f, 'lxml')
    #         subcategories = ['https://www.verderliquids.com' + i.find('a')['href'] for i in soup.find('section').find_all('article')]
    #     for i in subcategories:
    #         with open(f'subcategories/{i.split("/")[-1]}.html', 'w', encoding='utf-8') as f:
    #             f.write(requests.get(i, headers=headers).text)

    with open('verderliquids.csv', 'w', newline='', encoding='utf-8') as csvfile:
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

    for i in os.listdir('subcategories'):
        with open(f'subcategories/{i}', 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')
            products = []
            for k in soup.find('div', class_='list-brand-table').find_all('tr', class_=False):
                if not k.find('a'):
                    continue
                products_list = 'https://www.verderliquids.com' + k.find('a')['href']
                products.append(products_list)
        for j in products:
            page = requests.get(j, headers=headers).text
            soup = BeautifulSoup(page, 'lxml')
            category = " | ".join(
                [i.find('span').string for i in soup.find_all('li', {'itemprop': 'itemListElement'})[2:-1]])
            title = soup.find('div', class_='ce-bodytext').find('header').text.strip()
            description = soup.find('div', class_='ce-bodytext').find('p').text.strip()
            if not soup.find('div', class_='swiper-wrapper'):
                continue
            images = ['https://www.verderliquids.com' + i['src'] for i in
                      soup.find('div', class_='swiper-wrapper').find_all('img')]
            url = soup.find('link', {'rel': 'canonical'})['href']
            attr = []
            for k in soup.find('ul', class_='h-full').find_all('li', class_=re.compile('js-tabcontent'))[0].find_all(
                    'tr')[1:]:
                property_row = f'Properties | {k.find_all("td")[0].string.strip() if k.find_all("td")[0].string else None} | {k.find_all("td")[1].string.strip() if k.find_all("td")[1].string else None}'
                if not k.find_all("td")[0].string or not k.find_all("td")[1].string:
                    continue
                attr.append(property_row)
            downloads = []
            for k in soup.find('ul', class_='h-full').find_all('li', class_=re.compile('js-tabcontent'))[2].find_all(
                    'a'):
                downloads.append(f'{k.string.strip()} | {"https://www.verderliquids.com" + k["href"]}')
            attr = [i.replace("\xa0", " ") for i in attr]

            print(f'Category: {category}')
            print(f'Title: {title}')
            print(f'Description: {description}')
            print(f'Image: {images[0]}')
            print(f'Images: {", ".join(images)}')
            print(f'Attributes: {", ".join(attr)}')
            print(f'Downloads: {", ".join(downloads)}')
            print(f'SKU: {url.split("/")[-1]}')
            print(f'URL: {url}')
            print()

            with open('verderliquids.csv', 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow((
                    category,
                    title,
                    description,
                    images[0],
                    ", ".join(images),
                    '\n'.join(attr),
                    ", ".join(downloads),
                    url.split("/")[-1],
                    url)
                )


if __name__ == '__main__':
    if not os.path.isdir('categories'):
        os.mkdir('categories')
    if not os.path.isdir('subcategories'):
        os.mkdir('subcategories')
    get_verderliquids()
