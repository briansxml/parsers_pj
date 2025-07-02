import csv
import re

import requests
from bs4 import BeautifulSoup
import lxml

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}


def get_siefertrigonal():
    # with open('page.html', 'w', encoding='utf-8') as f:
    #     f.write(requests.get('https://siefer-trigonal.de', headers=headers).text)
    with open('page.html', 'r', encoding='utf-8') as f:
        src = f.read()
    soup = BeautifulSoup(src, 'lxml')
    products = [i.find('a')['href'] for i in
                soup.find('li', id='menu-item-1528').find('ul', class_='sub-menu').find_all('li')[1:]]

    with open('siefertrigonal.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow((
            '_NAME_',
            '_DESCRIPTION_',
            '_IMAGE_',
            '_IMAGES_',
            '_ATTRIBUTES_',
            '_SKU_',
            '_URL_')
        )

    for i in products:
        page = requests.get(i, headers=headers).text
        soup = BeautifulSoup(page, 'lxml')
        name = soup.find('div', class_=re.compile('fusion-title-1')).find_all('h1')[1].string[
               len('The Siefer Trigonal® machine '):-len(' (heating/cooling jacket)')]
        description = [i.text for i in soup.find('div', class_='fusion-text fusion-text-1').find_all('p')[:-1]]
        image = soup.find('span', class_=re.compile('fusion-imageframe')).find('a')['href']
        url = soup.find('link', rel='canonical')['href']
        attr = []
        for j in \
        soup.find('div', id='produkte_technische_daten').find_all('div', class_=re.compile('fusion-layout-column'))[
            2].find('tbody').find_all('tr'):
            params = [k.string for k in j.find_all('td')]
            names = [k.text for k in soup.find('div', id='produkte_technische_daten').find_all('div', class_=re.compile(
                'fusion-layout-column'))[2].find('thead').find_all('th')]
            attr.append(
                f'{soup.find("div", id="produkte_technische_daten").find_all("div", class_=re.compile("fusion-layout-column"))[0].text} | {names[1]} | {params[0]} | {params[1]}')
            attr.append(
                f'{soup.find("div", id="produkte_technische_daten").find_all("div", class_=re.compile("fusion-layout-column"))[0].text} | {names[2]} | {params[0]} | {params[2]}')
        for j in soup.find('div', id='produkte_technische_daten').find_all('div', class_=re.compile('fusion-layout-column'))[
            3].find_all('li'):
            attr.append(f'{soup.find("div", id="produkte_technische_daten").find_all("div", class_=re.compile("fusion-layout-column"))[1].text} | {j.string}')
        attr = [i.replace("\n", "") for i in attr]

        print(f'Title: {name}')
        print(f"Description: {' '.join(description)}")
        print(f"Image: {image}")
        print(f"Attributes: {', '.join(attr)}")
        print(f"SKU: {url.split('/')[-2]}")
        print(f"URL: {url}")
        print()

        with open('siefertrigonal.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow((
                name,
                ' '.join(description),
                image,
                image,
                '\n'.join(attr),
                url.split('/')[-2],
                url)
            )


if __name__ == '__main__':
    get_siefertrigonal()
