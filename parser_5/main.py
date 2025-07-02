import base64
import csv
import os
import re

import requests
import lxml
from bs4 import BeautifulSoup
from requests import JSONDecodeError

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}

proxies = {
    'https': 'socks5h://127.0.0.1:1080',
    'http': 'socks5h://127.0.0.1:1080',
}


def get_ariarmaturen_ru():
    # payload = {
    # "legacy_eID": "ajaxCallAriProductDatabase",
    # "tx_capps_pi1[uid-locale]": "4",
    # "tx_capps_pi1[select-type]": "",
    # "tx_capps_pi1[baureiheUrlParam]": ""
    # }
    # categories = requests.post('https://www.ari-armaturen.com/ru/izdelija', headers=headers, proxies=proxies, data=payload).json()['html_navigation']
    # soup = BeautifulSoup(categories, 'lxml')
    # for item in soup.find_all('li'):
    #     with open(f'categories/{item["pdb-id"]}.html', 'w', encoding='utf-8') as f:
    #         payload = {
    #             "legacy_eID": "ajaxCallAriProductDatabase",
    #             "tx_capps_pi1[uid-locale]": "4",
    #             "tx_capps_pi1[select-type]": "produktkategorie",
    #             "tx_capps_pi1[select-id]": f"{item['pdb-id']}",
    #             "tx_capps_pi1[exec-time]": "1750178574471",
    #             "tx_capps_pi1[baureiheUrlParam]": ""
    #         }
    #
    #         html_page = requests.post(
    #             'https://www.ari-armaturen.com/ru/izdelija',
    #             headers=headers, proxies=proxies, data=payload).json()
    #         f.write(html_page['html_navigation'])
    subcategories = {}

    for i in os.listdir('categories'):
        with open(f'categories/{i}', 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')
            subcategories[i.split('.')[0]] = [i['pdb-id'] for i in soup.find_all('li')]
    #
    # for i in subcategories:
    #     for j in subcategories[i]:
    #         payload = {
    #             "legacy_eID": "ajaxCallAriProductDatabase",
    #             "tx_capps_pi1[uid-locale]": "4",
    #             "tx_capps_pi1[select-type]": "baureihe",
    #             "tx_capps_pi1[select-id]": f"{j}",
    #             "tx_capps_pi1[get-category]": f"[\"{i}\",\"{j}\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\"]",
    #             "tx_capps_pi1[baureiheUrlParam]": ""
    #         }
    #
    #         with open(f'subcategories/{j}.html', 'w', encoding='utf-8') as f:
    #             html_page = requests.post(
    #                 'https://www.ari-armaturen.com/ru/izdelija',
    #                 headers=headers, proxies=proxies, data=payload).json()
    #             f.write(html_page['html_navigation'])
    checked_ids = []

    with open('ari-armaturen_ru.csv', 'w', newline='', encoding='utf-8') as csvfile:
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
            '_OPTIONS_',
            '_URL_')
        )

    for i in subcategories:
        for j in subcategories[i]:
            with open(f'subcategories/{j}.html', 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'lxml')
                payload = {
                    "legacy_eID": "ajaxCallAriProductDatabase",
                    "tx_capps_pi1[uid-locale]": "4",
                    "tx_capps_pi1[select-type]": "produktkategorie",
                    "tx_capps_pi1[select-id]": f"{i}",
                    "tx_capps_pi1[exec-time]": "1750256545297",
                    "tx_capps_pi1[baureiheUrlParam]": ""
                }
                orig_page_1 = BeautifulSoup(requests.post(
                    f'https://www.ari-armaturen.com/ru/izdelija',
                    headers=headers, proxies=proxies, data=payload).json()['html_navigation'], 'lxml')
                payload = {
                    "legacy_eID": "ajaxCallAriProductDatabase",
                    "tx_capps_pi1[uid-locale]": "4",
                    "tx_capps_pi1[select-type]": "",
                    "tx_capps_pi1[baureiheUrlParam]": ""
                }
                orig_page_2 = BeautifulSoup(requests.post(
                    f'https://www.ari-armaturen.com/ru/izdelija',
                    headers=headers, proxies=proxies, data=payload).json()['html_navigation'], 'lxml')
                for k in soup.find('div', attrs={'id': 'collapseTwo'}).find_all('li'):
                    if k['pdb-id'] in checked_ids:
                        continue
                    checked_ids.append(k['pdb-id'])
                    payload = {
                        "legacy_eID": "ajaxCallAriProductDatabase",
                        "tx_capps_pi1[uid-locale]": "4",
                        "tx_capps_pi1[get-baureihe]": f"[\"{i}\",\"{j}\",\"{k['pdb-id']}\",null,null,null,null,null,\"\",\"\",\"\"]",
                        "tx_capps_pi1[baureiheUrlParam]": f"{k['pdb-id']}"
                    }
                    try:
                        html_page = requests.post('https://www.ari-armaturen.com/ru/izdelija', headers=headers,
                                                  proxies=proxies,
                                                  data=payload).json()
                    except JSONDecodeError:
                        continue
                    soup_content = BeautifulSoup(html_page['html_content'], 'lxml')
                    soup_header = BeautifulSoup(html_page['html_header'], 'lxml')
                    page = 0
                    valve_list = []
                    while True:
                        page += 1
                        payload = {
                            "legacy_eID": "ajaxCallAriProductDatabase",
                            "tx_capps_pi1[uid-locale]": "4",
                            "tx_capps_pi1[get-baureihe]": "[\"1\",\"17\",\"470\",null,null,null,null,null,\"\",\"\",\"\"]",
                            "tx_capps_pi1[pagination-type]": "ventile",
                            "tx_capps_pi1[pagination-page]": f"{page}",
                            "tx_capps_pi1[pagination-pagecount]": "100",
                            "tx_capps_pi1[pagination-page-previous]": "1",
                            "tx_capps_pi1[select-type]": "",
                            "tx_capps_pi1[select-matrix]": f"[\"{i}\",\"{j}\",\"{k['pdb-id']}\",null,null,null,null,null,\"\",\"\",\"\"]",
                            "tx_capps_pi1[select-template-type]": "",
                            "tx_capps_pi1[select-ansicht-key]": "",
                            "tx_capps_pi1[select-cad-key]": "",
                            "tx_capps_pi1[baureiheUrlParam]": f"{k['pdb-id']}"
                        }
                        html_valve = requests.post('https://www.ari-armaturen.com/ru/izdelija', headers=headers,
                                                   proxies=proxies, data=payload)
                        if html_valve.status_code == 500:
                            break
                        valve_list.append(base64.b64decode(html_valve.json()['table']).decode("utf-8"))
                    attr = []
                    for pr in soup_content.find('tbody').find_all('tr'):
                        if pr.find_all('td')[0].string and pr.find_all('td')[1].string:
                            attr.append(
                                f"Данные изделия | {pr.find_all('td')[0].string.strip().replace(':', '')} | {pr.find_all('td')[1].string.strip()}")

                    options = []
                    valve_html = f'<table class="table table-striped"><thead><tr><th>Фигура</th><th>PN (НД)</th><th>DN (Ду)</th><th>Материал</th><th>Соединение</th><th>Форма</th><th>Температура / корпус</th></tr></thead><tbody>{"".join(valve_list)}</tbody></table>'
                    valve_soup = BeautifulSoup(valve_html, 'lxml')

                    for row in valve_soup.find('tbody').find_all('tr'):
                        for parametr, name in zip(row.find_all('td')[:-1], valve_soup.find('thead').find_all('th')):
                            if name.string and parametr.string and f"select|{name.string.strip()}|{parametr.string.strip()}|1|100|1|+|0.0000|+|0|+|0.00000000" not in options:
                                options.append(f"select|{name.string.strip()}|{parametr.string.strip()}|1|100|1|+|0.0000|+|0|+|0.00000000")

                    downloads = []
                    checked_urls_data = []
                    for row in soup_content.find('div', id='Datenblätter').find('tbody').find_all('tr'):
                        parametrs = []
                        for parametr in row.find_all('td'):
                            if not parametr.find('a'):
                                parametrs.append(parametr.string.strip() if parametr.string else '')
                            else:
                                if parametr.find('a')['href'] not in checked_urls_data:
                                    parametrs.append(parametr.find('a')['href'].strip())
                                    checked_urls_data.append(parametr.find('a')['href'].strip())
                                else:
                                    parametrs = None
                            if parametrs and len(parametrs) == 3:
                                downloads.append(' | '.join(parametrs))

                    checked_urls_instruction = []
                    for row in soup_content.find('div', id='Betriebsanleitungen').find('tbody').find_all('tr'):
                        parametrs = []
                        for parametr in row.find_all('td'):
                            if not parametr.find('a'):
                                parametrs.append(parametr.string.strip() if parametr.string else '')
                            else:
                                if parametr.find('a')['href'] not in checked_urls_instruction:
                                    parametrs.append(parametr.find('a')['href'].strip())
                                    checked_urls_instruction.append(parametr.find('a')['href'].strip())
                                else:
                                    parametrs = None
                        if parametrs and len(parametrs) == 3:
                            downloads.append(' | '.join(parametrs))

                    for row in soup_content.find('div', id='Prüfungen').find('tbody').find_all('tr'):
                        parametrs = []
                        parametr = row.find('td')
                        name = soup_content.find('div', id='Prüfungen').find('thead').find('th')
                        if parametr and name:
                            parametrs.append(f"{name.string.strip()} | {parametr.string.strip()}")
                        attr.append(f"Особенности изделия | {' | '.join(parametrs)}")

                    attr = [i.replace('\n', ' ') for i in attr]
                    images = [i['href'] for i in soup_header.find('div', class_='owl-carousel').find_all('a')]

                    if soup_content.find('div', {'id': 'Datenblätter'}).find('tbody').find('tr'):
                        title = soup_content.find('div', {'id': 'Datenblätter'}).find('tbody').find('tr').find(
                            'td').string
                    else:
                        title = soup_header.find('div', class_='col-md-12').find('h1').string
                    print(
                        f'Category: {orig_page_2.find("ul", {"id": "search_init_choice"}).find("li", id=i).find("a").string} | {orig_page_1.find("div", class_="panel panel-default collapseOne").find("li", id=j).find("a").string}')
                    print(
                        f"Title: {title}")
                    print(
                        f"Description: {soup_header.find('div', class_='col-md-12').find('div').string}")
                    print(f'Image: {images[0]}')
                    print(f'Images: {", ".join(images)}')
                    print(f"Attributes: {', '.join(attr)}")
                    print(f"Downloads: {', '.join(downloads)}")
                    print(f'SKU: {k["pdb-id"]}')
                    print(f'Options: {", ".join(options)}')
                    print(f'URL: https://www.ari-armaturen.com{k.find("a")["href"]}')
                    print()

                    with open('ari-armaturen_ru.csv', 'a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile, delimiter=';')
                        writer.writerow((
                            f'{orig_page_2.find("ul", {"id": "search_init_choice"}).find("li", id=i).find("a").string} | {orig_page_1.find("div", class_="panel panel-default collapseOne").find("li", id=j).find("a").string}',
                            title,
                            soup_header.find('div', class_='col-md-12').find('div').string,
                            images[0],
                            ', '.join(images),
                            '\n'.join(attr),
                            '\n'.join(downloads),
                            k["pdb-id"],
                            '\n'.join(options),
                            f'https://www.ari-armaturen.com{k.find("a")["href"]}')
                        )


def get_ariarmaturen():
    # payload = {
    # "legacy_eID": "ajaxCallAriProductDatabase",
    # "tx_capps_pi1[uid-locale]": "0",
    # "tx_capps_pi1[select-type]": "",
    # "tx_capps_pi1[baureiheUrlParam]": ""
    # }
    # categories = requests.post('https://www.ari-armaturen.com/products', headers=headers, proxies=proxies, data=payload).json()['html_navigation']
    # soup = BeautifulSoup(categories, 'lxml')
    # for item in soup.find_all('li'):
    #     with open(f'categories/{item["pdb-id"]}.html', 'w', encoding='utf-8') as f:
    #         payload = {
    #             "legacy_eID": "ajaxCallAriProductDatabase",
    #             "tx_capps_pi1[uid-locale]": "0",
    #             "tx_capps_pi1[select-type]": "produktkategorie",
    #             "tx_capps_pi1[select-id]": f"{item['pdb-id']}",
    #             "tx_capps_pi1[exec-time]": "1750178574471",
    #             "tx_capps_pi1[baureiheUrlParam]": ""
    #         }
    #
    #         html_page = requests.post(
    #             'https://www.ari-armaturen.com/products',
    #             headers=headers, proxies=proxies, data=payload).json()
    #         f.write(html_page['html_navigation'])
    subcategories = {}

    for i in os.listdir('categories'):
        with open(f'categories/{i}', 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')
            subcategories[i.split('.')[0]] = [i['pdb-id'] for i in soup.find_all('li')]
    #
    # for i in subcategories:
    #     for j in subcategories[i]:
    #         payload = {
    #             "legacy_eID": "ajaxCallAriProductDatabase",
    #             "tx_capps_pi1[uid-locale]": "0",
    #             "tx_capps_pi1[select-type]": "baureihe",
    #             "tx_capps_pi1[select-id]": f"{j}",
    #             "tx_capps_pi1[get-category]": f"[\"{i}\",\"{j}\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\"]",
    #             "tx_capps_pi1[baureiheUrlParam]": ""
    #         }
    #
    #         with open(f'subcategories/{j}.html', 'w', encoding='utf-8') as f:
    #             html_page = requests.post(
    #                 'https://www.ari-armaturen.com/products',
    #                 headers=headers, proxies=proxies, data=payload).json()
    #             f.write(html_page['html_navigation'])
    checked_ids = []

    with open('ari-armaturen.csv', 'w', newline='', encoding='utf-8') as csvfile:
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
            '_OPTIONS_',
            '_URL_')
        )

    for i in subcategories:
        for j in subcategories[i]:
            with open(f'subcategories/{j}.html', 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'lxml')
                payload = {
                    "legacy_eID": "ajaxCallAriProductDatabase",
                    "tx_capps_pi1[uid-locale]": "0",
                    "tx_capps_pi1[select-type]": "produktkategorie",
                    "tx_capps_pi1[select-id]": f"{i}",
                    "tx_capps_pi1[exec-time]": "1750256545297",
                    "tx_capps_pi1[baureiheUrlParam]": ""
                }
                orig_page_1 = BeautifulSoup(requests.post(
                    f'https://www.ari-armaturen.com/products',
                    headers=headers, proxies=proxies, data=payload).json()['html_navigation'], 'lxml')
                payload = {
                    "legacy_eID": "ajaxCallAriProductDatabase",
                    "tx_capps_pi1[uid-locale]": "0",
                    "tx_capps_pi1[select-type]": "",
                    "tx_capps_pi1[baureiheUrlParam]": ""
                }
                orig_page_2 = BeautifulSoup(requests.post(
                    f'https://www.ari-armaturen.com/products',
                    headers=headers, proxies=proxies, data=payload).json()['html_navigation'], 'lxml')
                for k in soup.find('div', attrs={'id': 'collapseTwo'}).find_all('li'):
                    if k['pdb-id'] in checked_ids:
                        continue
                    checked_ids.append(k['pdb-id'])
                    payload = {
                        "legacy_eID": "ajaxCallAriProductDatabase",
                        "tx_capps_pi1[uid-locale]": "0",
                        "tx_capps_pi1[get-baureihe]": f"[\"{i}\",\"{j}\",\"{k['pdb-id']}\",null,null,null,null,null,\"\",\"\",\"\"]",
                        "tx_capps_pi1[baureiheUrlParam]": f"{k['pdb-id']}"
                    }
                    html_page = requests.post('https://www.ari-armaturen.com/products', headers=headers,
                                              proxies=proxies,
                                              data=payload).json()
                    soup_content = BeautifulSoup(html_page['html_content'], 'lxml')
                    soup_header = BeautifulSoup(html_page['html_header'], 'lxml')
                    page = 0
                    valve_list = []
                    while True:
                        page += 1
                        payload = {
                            "legacy_eID": "ajaxCallAriProductDatabase",
                            "tx_capps_pi1[uid-locale]": "0",
                            "tx_capps_pi1[get-baureihe]": "[\"1\",\"17\",\"470\",null,null,null,null,null,\"\",\"\",\"\"]",
                            "tx_capps_pi1[pagination-type]": "ventile",
                            "tx_capps_pi1[pagination-page]": f"{page}",
                            "tx_capps_pi1[pagination-pagecount]": "100",
                            "tx_capps_pi1[pagination-page-previous]": "1",
                            "tx_capps_pi1[select-type]": "",
                            "tx_capps_pi1[select-matrix]": f"[\"{i}\",\"{j}\",\"{k['pdb-id']}\",null,null,null,null,null,\"\",\"\",\"\"]",
                            "tx_capps_pi1[select-template-type]": "",
                            "tx_capps_pi1[select-ansicht-key]": "",
                            "tx_capps_pi1[select-cad-key]": "",
                            "tx_capps_pi1[baureiheUrlParam]": f"{k['pdb-id']}"
                        }
                        html_valve = requests.post('https://www.ari-armaturen.com/products', headers=headers,
                                                   proxies=proxies, data=payload)
                        if html_valve.status_code == 500:
                            break
                        valve_list.append(base64.b64decode(html_valve.json()['table']).decode("utf-8"))
                    attr = []
                    for pr in soup_content.find('tbody').find_all('tr'):
                        if pr.find_all('td')[0].string and pr.find_all('td')[1].string:
                            attr.append(f"Product data | {pr.find_all('td')[0].string.strip().replace(':', '')} | {pr.find_all('td')[1].string.strip()}")
                    options = []
                    valve_html = f'<table class="table table-striped"><thead><tr><th>Figure</th><th>PN</th><th>DN</th><th>Material</th><th>Connection</th><th>Form</th><th>Temp./*body</th></tr></thead><tbody>{"".join(valve_list)}</tbody></table>'
                    valve_soup = BeautifulSoup(valve_html, 'lxml')

                    for row in valve_soup.find('tbody').find_all('tr'):
                        for parametr, name in zip(row.find_all('td')[:-1], valve_soup.find('thead').find_all('th')):
                            if name.string and parametr.string and f"select|{name.string.strip()}|{parametr.string.strip()}|1|100|1|+|0.0000|+|0|+|0.00000000" not in options:
                                options.append(f"select|{name.string.strip()}|{parametr.string.strip()}|1|100|1|+|0.0000|+|0|+|0.00000000")

                    downloads = []
                    checked_urls_data = []
                    for row in soup_content.find('div', id='Datenblätter').find('tbody').find_all('tr'):
                        parametrs = []
                        for parametr in row.find_all('td'):
                            if not parametr.find('a'):
                                parametrs.append(parametr.string.strip() if parametr.string else '')
                            else:
                                if parametr.find('a')['href'] not in checked_urls_data:
                                    parametrs.append(parametr.find('a')['href'].strip())
                                    checked_urls_data.append(parametr.find('a')['href'].strip())
                                else:
                                    parametrs = None
                            if parametrs and len(parametrs) == 3:
                                downloads.append(' | '.join(parametrs))

                    checked_urls_instruction = []
                    for row in soup_content.find('div', id='Betriebsanleitungen').find('tbody').find_all('tr'):
                        parametrs = []
                        for parametr in row.find_all('td'):
                            if not parametr.find('a'):
                                parametrs.append(parametr.string.strip() if parametr.string else '')
                            else:
                                if parametr.find('a')['href'] not in checked_urls_instruction:
                                    parametrs.append(parametr.find('a')['href'].strip())
                                    checked_urls_instruction.append(parametr.find('a')['href'].strip())
                                else:
                                    parametrs = None
                        if parametrs and len(parametrs) == 3:
                            downloads.append(' | '.join(parametrs))

                    for row in soup_content.find('div', id='Prüfungen').find('tbody').find_all('tr'):
                        parametrs = []
                        parametr = row.find('td')
                        name = soup_content.find('div', id='Prüfungen').find('thead').find('th')
                        if parametr and name:
                            parametrs.append(f"{name.string.strip()} | {parametr.string.strip()}")
                        attr.append(f"Product details | {' | '.join(parametrs)}")

                    attr = [i.replace('\n', ' ') for i in attr]
                    images = [i['href'] for i in soup_header.find('div', class_='owl-carousel').find_all('a')]

                    if soup_content.find('div', {'id': 'Datenblätter'}).find('tbody').find('tr'):
                        title = soup_content.find('div', {'id': 'Datenblätter'}).find('tbody').find('tr').find(
                            'td').string
                    else:
                        title = soup_header.find('div', class_='col-md-12').find('h1').string
                    print(
                        f'Category: {orig_page_2.find("ul", {"id": "search_init_choice"}).find("li", id=i).find("a").string} | {orig_page_1.find("div", class_="panel panel-default collapseOne").find("li", id=j).find("a").string}')
                    print(
                        f"Title: {title}")
                    print(
                        f"Description: {soup_header.find('div', class_='col-md-12').find('div').string}")
                    print(f'Image: {images[0]}')
                    print(f'Images: {", ".join(images)}')
                    print(f"Attributes: {', '.join(attr)}")
                    print(f"Downloads: {', '.join(downloads)}")
                    print(f'SKU: {k["pdb-id"]}')
                    print(f'Options: {", ".join(options)}')
                    print(f'URL: https://www.ari-armaturen.com{k.find("a")["href"]}')
                    print()

                    with open('ari-armaturen.csv', 'a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile, delimiter=';')
                        writer.writerow((
                            f'{orig_page_2.find("ul", {"id": "search_init_choice"}).find("li", id=i).find("a").string} | {orig_page_1.find("div", class_="panel panel-default collapseOne").find("li", id=j).find("a").string}',
                            title,
                            soup_header.find('div', class_='col-md-12').find('div').string,
                            images[0],
                            ', '.join(images),
                            '\n'.join(attr),
                            '\n'.join(downloads),
                            k["pdb-id"],
                            '\n'.join(options),
                            f'https://www.ari-armaturen.com{k.find("a")["href"]}')
                        )


if __name__ == '__main__':
    if not os.path.isdir('categories'):
        os.mkdir('categories')
    if not os.path.isdir('subcategories'):
        os.mkdir('subcategories')
    get_ariarmaturen()
    get_ariarmaturen_ru()
