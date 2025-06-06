import re
import sys

import requests
import csv
import json
import html
from bs4 import BeautifulSoup

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
           'Cache-Control': 'max-age=0', 'Connection': 'close', 'Host': 're-store.ru',
           'Referer': 're-store.ru/', 'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}


def goproshka_get():
    src = requests.get('https://goproshka.ru/collection/ekshn-kamery').text

    soup = BeautifulSoup(src, 'lxml')
    items = soup.find('script', string=re.compile('items')).string
    items_json = json.loads(items[items.find('[', 13):items.rfind(']') + 1])
    with open('test.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')

        writer.writerow(
            (
                'ссылка на товар', 'наименование товара', 'цена товара', 'описание товара', 'ссылки на фотографии'
            )
        )
    for item in items_json:
        item_content = requests.get(f'https://goproshka.ru/products_by_id/{item["item_id"]}.json').json()
        product = item_content["products"][0]
        soup = BeautifulSoup(str(product['short_description']), 'lxml')
        description = soup.find().text
        description = description.replace('¹', '')
        description = description.replace('″', '')
        description = description.replace('º', '')
        description = description.replace('⬤', '')
        description = description.replace('×', '')
        images = [i['original_url'] for i in product["images"][:5]]
        with open('test.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            try:
                writer.writerow(
                    (
                        f'https://goproshka.ru{product["url"]}',
                        product["title"],
                        product["price_min"],
                        description if description else '',
                        ",".join(images)
                    )
                )
            except Exception as e:
                print(description)
                print(f'https://goproshka.ru{product["url"]}')
                print(e)
                sys.exit()


def restore_get():
    # with open('rustore.html', 'w', encoding='utf-8') as f:
    #     f.write(requests.get('https://re-store.ru/igry-i-konsoli/igrovye-pristavki/', headers=headers).text)
    pages = ['https://re-store.ru/igry-i-konsoli/igrovye-pristavki', 'https://re-store.ru/kompyutery-noutbuki/apple',
             'https://re-store.ru/akustika/brand_jbl']
    for page in pages[1:]:
        page_pagin = 0
        while True:
            page_pagin += 1
            src = requests.get(f'{page}/?page={page_pagin}', headers=headers).text
            soup = BeautifulSoup(src, 'lxml')
            items = soup.find_all('script', {'data-skip-moving': 'true', 'type': 'application/javascript'})[0].string
            items_json = json.loads(items[items.find('{'):items.rfind('}') + 1].replace("\\", ''))
            items_list = items_json['catalog']['listing']['items']
            if not items_list:
                break
            for item in items_list:
                r = requests.get(f'https://re-store.ru{item["linkedProducts"][0]["link"]}', headers=headers).text
                soup = BeautifulSoup(r, 'lxml')
                content_item = soup.find('script', {'data-skip-moving': 'true', 'type': 'application/javascript'}).string
                content_json = json.loads(content_item[content_item.find('{'):content_item.find("');")].replace("\\", ''))
                # with open('restore-page.json', 'w', encoding='utf-8') as f:
                #     json.dump(items_json, f, ensure_ascii=False, indent=4)
                # break
                images = [i['image']['desktop2x'] for i in content_json["gallery"]]
                with open('test.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile, delimiter=';')
                    writer.writerow(
                        (
                            f'https://re-store.ru{item["linkedProducts"][0]["link"]}',
                            item["linkedProducts"][0]["name"],
                            item["linkedProducts"][0]["price"]["special"]["price"],
                            content_json["tabs"]["content"][0]['description']['text'].replace('‑', ''),
                            ", ".join(images)
                        )
                    )


if __name__ == '__main__':
    # goproshka_get()
    restore_get()
