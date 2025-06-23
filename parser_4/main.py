import json
import os

import csv
import re

import requests
from bs4 import BeautifulSoup
import lxml

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}


def get_mobile_pumps():
    i = 0
    while True:
        i += 1
        payloads = {'action': 'getFilteredProducts',
                    'params': f'id_category=19&id_manufacturer=0&id_supplier=0&page={i}&nb_items=12&controller_product_ids=&current_controller=category&page_name=category&orderBy=position&orderWay=asc&customer_groups=1&random_seed=25061413&layout=vertical&count_data=1&hide_zero_matches=1&dim_zero_matches=1&sf_position=0&include_group=0&compact=767&compact_offset=2&compact_btn=1&npp=12&default_sorting=position.asc&random_upd=1&reload_action=1&p_type=1&autoscroll=1&combination_results=1&oos_behaviour_=0&oos_behaviour=0&combinations_stock=0&new_days=&sales_days=&url_filters=1&url_sorting=1&url_page=1&dec_sep=.&tho_sep=&merged_attributes=0&merged_features=0&available_options%5Bm%5D%5B0%5D=1&sliders%5Bp%5D%5B0%5D%5Bfrom%5D=999&sliders%5Bp%5D%5B0%5D%5Bmin%5D=999.01&sliders%5Bp%5D%5B0%5D%5Bto%5D=8599&sliders%5Bp%5D%5B0%5D%5Bmax%5D=8599&no_submit='}

        json_data = json.dumps(
            requests.post('https://www.pinopumps.com/en/module/amazzingfilter/ajax?ajax=1', headers=headers,
                          data=payloads, timeout=10).json(), ensure_ascii=False)
        json_without_slash = json.loads(json_data)
        html_items = str(json_without_slash['product_list_html'])
        soup = BeautifulSoup(html_items, 'lxml')
        items = soup.find('div', class_='products').find('div').find('div', class_='row').text.strip()
        if not items:
            break
        with open(f'html/mobile_pumps_{i}.html', 'w', encoding='utf-8') as f:
            f.write(html_items)


def get_s_pumps():
    i = 0
    while True:
        i += 1
        payloads = {'action': 'getFilteredProducts',
                    'params': f'id_category=17&id_manufacturer=0&id_supplier=0&page={i}&nb_items=100&controller_product_ids=&current_controller=category&page_name=category&orderBy=name&orderWay=asc&customer_groups=1&random_seed=25061412&layout=vertical&count_data=1&hide_zero_matches=1&dim_zero_matches=1&sf_position=0&include_group=0&compact=767&compact_offset=2&compact_btn=1&npp=100&default_sorting=name.asc&random_upd=1&reload_action=1&p_type=1&autoscroll=1&combination_results=1&oos_behaviour_=0&oos_behaviour=0&combinations_stock=0&new_days=&sales_days=&url_filters=1&url_sorting=1&url_page=1&dec_sep=.&tho_sep=&merged_attributes=0&merged_features=0&available_options%5Bf%5D%5B3%5D=143%2C384%2C286%2C8%2C10403%2C148%2C312%2C166%2C9973%2C10106%2C6%2C208&available_options%5Bf%5D%5B2%5D=376%2C3%2C207%2C285%2C310%2C165%2C4179%2C4180%2C400%2C5%2C383%2C142%2C10357%2C393%2C10402%2C10088&available_options%5Bf%5D%5B104%5D=430%2C428%2C429%2C427&available_options%5Bf%5D%5B105%5D=448%2C449%2C450%2C451%2C452%2C7082%2C5049%2C453%2C454%2C455%2C7221%2C456%2C457%2C487%2C459%2C458%2C460%2C10105%2C461%2C10141%2C462%2C463%2C10367%2C11754%2C10401'}

        json_data = json.dumps(
            requests.post('https://shop.victorpumps.com/en/module/amazzingfilter/ajax?ajax=1', headers=headers,
                          data=payloads, timeout=10).json(), ensure_ascii=False)
        json_without_slash = json.loads(json_data)
        html_items = str(json_without_slash['product_list_html'])
        soup = BeautifulSoup(html_items, 'lxml')
        items = soup.find('div', class_='products').find('div', class_='row').text.strip()
        if not items:
            break
        with open(f'html/s_pumps_{i}.html', 'w', encoding='utf-8') as f:
            f.write(html_items)


def get_applications():
    i = 0
    while True:
        i += 1
        payloads = {'action': 'getFilteredProducts',
                    'params': f'id_category=20&id_manufacturer=0&id_supplier=0&page={i}&nb_items=100&controller_product_ids=&current_controller=category&page_name=category&orderBy=position&orderWay=asc&customer_groups=1&random_seed=25061412&layout=vertical&count_data=1&hide_zero_matches=1&dim_zero_matches=1&sf_position=0&include_group=0&compact=767&compact_offset=2&compact_btn=1&npp=100&default_sorting=name.asc&random_upd=1&reload_action=1&p_type=1&autoscroll=1&combination_results=1&oos_behaviour_=0&oos_behaviour=0&combinations_stock=0&new_days=&sales_days=&url_filters=1&url_sorting=1&url_page=1&dec_sep=.&tho_sep=&merged_attributes=0&merged_features=0&available_options%5Bf%5D%5B110%5D=749%2C748&available_options%5Bf%5D%5B109%5D=9956%2C788%2C9939%2C755%2C790%2C753%2C11618%2C11364%2C760%2C9941%2C9953%2C9944%2C9947%2C11367%2C9948%2C9949%2C791%2C751%2C786%2C11365%2C9954%2C785%2C11366%2C754%2C9946%2C756%2C9938%2C9942%2C9940%2C787%2C9958%2C758%2C792%2C9936%2C793%2C794%2C9955%2C757%2C750%2C759%2C789%2C9950%2C9951%2C11363'}

        json_data = json.dumps(
            requests.post('https://shop.victorpumps.com/en/module/amazzingfilter/ajax?ajax=1', headers=headers,
                          data=payloads, timeout=10).json(), ensure_ascii=False)
        json_without_slash = json.loads(json_data)
        html_items = str(json_without_slash['product_list_html'])
        soup = BeautifulSoup(html_items, 'lxml')
        items = soup.find('div', class_='products').find('div', class_='row').text.strip()
        if not items:
            break
        with open(f'html/applications_{i}.html', 'w', encoding='utf-8') as f:
            f.write(html_items)


def write_to_csv():
    html_files = os.listdir('html')

    with open('test.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow((
            '_CATEGORY_',
            '_NAME_',
            '_DESCRIPTION_',
            '_IMAGE_',
            '_IMAGES_',
            '_ATTRIBUTES_',
            '_SKU_',
            '_OPTIONS_',
            '_URL_')
        )
    for file in html_files:
        with open(f'html/{file}', 'r', encoding='utf-8') as f:
            src = f.read()
        soup = BeautifulSoup(src, 'lxml')
        items = soup.find_all('div', class_=re.compile('ajax_block_product'))
        for item in items:
            item_page_url = item.find('a', class_='thumbnail product-thumbnail')['href']
            # with open(f'html/applications_test.html', 'r', encoding='utf-8') as f:
            #     item_page = f.read()
            item_page = requests.get(item_page_url).text
            soup = BeautifulSoup(item_page, 'lxml')
            script_data = soup.find('script', string=re.compile('var prestashop')).text
            data_json = json.loads(script_data[script_data.index('var prestashop') + 17:script_data.rfind('}') + 1])
            images = [i['data-image-large-src'] for i in
                      soup.find('div', class_='product-thumb-images').find_all('img')]
            options = soup.find('div', class_='seocombination')
            attributes = soup.find_all('tbody')
            attr = []
            for i in attributes:
                for j in i.find_all('tr')[1:]:
                    attr.append(
                        f"{i.find_all('tr')[0].text.strip()} | {j.find_all('td')[0].text.strip()} | {re.sub(' +', ' ', j.find_all('td')[1].text.strip())}")

            print(f"Category: {data_json['breadcrumb']['links'][1]['title']}")
            print(f"Name: {data_json['page']['meta']['title']}")
            print(f"Description: {data_json['page']['meta']['description']}")
            print(
                f"Options: {', '.join([i.string.strip() for i in options.find_all('a')])}" if options else f"Options: None")
            print(f"Attributes: {', '.join(attr)}")
            print(f"Reference: {soup.find('span', {'itemprop': 'sku'}).string}")
            print(f"Image: {soup.find('meta', {'property': 'og:image'})['content']}")
            print(f"Images: {', '.join(images)}")
            print(f"URL: {item_page_url}")
            print()

            with open('test.csv', 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow((
                    data_json['breadcrumb']['links'][1]['title'],
                    data_json['page']['meta']['title'],
                    data_json['page']['meta']['description'],
                    soup.find('meta', {'property': 'og:image'})['content'],
                    ', '.join(images),
                    '\n'.join(attr),
                    soup.find('span', {'itemprop': 'sku'}).string,
                    ', '.join([i.string.strip() for i in options.find_all('a')]) if options else None,
                    item_page_url)
                )


if __name__ == '__main__':
    if not os.path.isdir('html'):
        os.mkdir('html')
    # get_mobile_pumps()
    # get_applications()
    # get_s_pumps()
    write_to_csv()
