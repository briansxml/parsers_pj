import csv
import re

import requests
from bs4 import BeautifulSoup
import lxml

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}


def get_erichhahn(lang):
    if lang == 'ru':
        name_csv = 'erichhahn_ru.csv'
    elif lang == 'tr':
        name_csv = 'erichhahn_tr.csv'
    else:
        name_csv = 'erichhahn.csv'
    with open(name_csv, 'w', newline='',
              encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow((
            '_CATEGORY_',
            '_NAME_',
            '_DESCRIPTION_',
            '_IMAGE_',
            '_IMAGES_',
            '_ATTRIBUTES_',
            '_SKU_',
            '_URL_')
        )
    with open('products.html', 'w', encoding='utf-8') as f:
        f.write(requests.get(f'https://www.erichhahn.com.tr/{lang}/', headers=headers).text)
    with open('products.html', 'r', encoding='utf-8') as f:
        src = f.read()
    soup = BeautifulSoup(src, 'lxml')
    categories = [i for i in soup.find('ul', class_=re.compile('w-nav-list level_1')).find('li', class_=re.compile('columns_3 mobile-drop-by_arrow')).find('li', class_=re.compile('w-nav-item level_2')).find_all('a',
                                                                                                        class_='w-nav-anchor level_3')]
    for category_tag in categories:
        category = category_tag.text
        for product in category_tag.parent.find_all('a', class_='w-nav-anchor level_4'):
            url = product['href']
            src = requests.get(product['href']).text
            soup = BeautifulSoup(src, 'lxml')
            title = soup.find('h3').text
            description = soup.find_all('section', class_='l-section wpb_row height_small')[1].find('div',
                                                                                                    class_=re.compile(
                                                                                                        'wpb_column vc_column_container animate_afl')).text
            image = soup.find_all('section', class_='l-section wpb_row height_small')[1].find('div', class_=re.compile(
                'wpb_column vc_column_container animate_afr')).find('img')['src']
            banner = soup.find('meta', {'property': 'og:image'})['content']
            if banner.startswith('//'):
                banner = banner.replace('//', 'https://')
            images = [image, banner]
            if len(soup.find_all('section', class_='l-section wpb_row height_small')[2].find_all('div',
                                                                                                 class_='vc_col-sm-6 wpb_column vc_column_container')) == 2:
                description += soup.find_all('section', class_='l-section wpb_row height_small')[2].find('div',
                                                                                                         class_='vc_col-sm-6 wpb_column vc_column_container').text
            attr = [f'{i.text.strip()} | {j.text.strip()}' for i, j in zip(
                soup.find_all('section', class_='l-section wpb_row height_small')[2].find_all('span',
                                                                                              class_='w-tabs-item-title'),
                soup.find_all('section', class_='l-section wpb_row height_small')[2].find_all('div',
                                                                                              class_='w-tabs-section-content'))]
            attr = [i.replace('\n', ' ') for i in attr]
            data_id = soup.find('table')['data-footable_id']
            query_h = {'action': 'wp_ajax_ninja_tables_public_action', 'table_id': data_id, 'target_action': 'get-all-data',
                       'default_sorting': 'old_first', 'skip_rows': 0, 'limit_rows': 0, 'ninja_table_public_nonce': 'b352d06193'}
            table = requests.get('https://www.erichhahn.com.tr/wp-admin/admin-ajax.php', headers=headers,
                                 params=query_h).json()
            for j in table:
                table_list = list(j['value'].items())
                if len(j['value']) > 3:
                    name = table_list[0][1]
                    parameters = table_list[1:-1]
                    for i in parameters:
                        attr.append(f'{i[0].upper()} | {name} | {i[1]}')
                else:
                    attr.append(f'{table_list[0][1]} | {table_list[1][1]}')
            if len(soup.find_all("div", class_="w-tabs-list-h")[1].find_all("a", class_=re.compile("w-tabs-item"))) > 2:
                names = [name.text for name in soup.find_all("div", class_="w-tabs-list-h")[1].find_all("a", class_=re.compile("w-tabs-item"))[2:]]
                content = [i.text for i in soup.find_all("div", class_="w-tabs-list-h")[1].find_all("div", class_=re.compile("w-tabs-section-content-h"))[2:]]
                attr.extend([f'{i} | {j}' for i, j in zip(names, content)])

            print(f'Category: {category}')
            print(f'Title: {title}')
            print(f'Description: {description}')
            print(f'Image: {image}')
            print(f'Images: {", ".join(images)}')
            print(f'Attributes: {", ".join(attr)}')
            print(f'SKU: {url.split("/")[-2]}')
            print(f'URL: {url}')
            print()

            with open(name_csv, 'a', newline='',
                      encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow((
                    category,
                    title,
                    description,
                    image,
                    ", ".join(images),
                    "\n".join(attr),
                    url.split("/")[-2],
                    url)
                )

    # products.extend([i['href'] for i in soup.find('li', id='menu-item-16').find('li', id='menu-item-200').find_all('a', class_='w-nav-anchor level_3')])


if __name__ == '__main__':
    # get_erichhahn('en')
    get_erichhahn('ru')
    get_erichhahn('tr')
