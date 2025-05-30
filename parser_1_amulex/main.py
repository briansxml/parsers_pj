import requests
from bs4 import BeautifulSoup

# Парсер всех шаблонов документов с сайта amulex.ru

def get_docs():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 YaBrowser/25.4.0.0 Safari/537.36'
    }

    with open('test.html', 'r', encoding='utf-8') as f:
        src = f.read()

    soup = BeautifulSoup(src, 'lxml')
    items_cards = soup.find_all('li', {'class': 'items__item', 'data-id': False})

    for j, i in enumerate(items_cards):
        id_item = i['data-id']
        name_item = i.find('h5', class_='items__item-title').text.strip()
        name_item = name_item.replace('/', ' ')
        url = f"https://amulex.ru/docs/docx/{id_item}.docx"
        req = requests.get(url, headers=headers)
        response = req.content

        with open(f"docx/{name_item}_{id_item}.docx", "wb") as f:
            f.write(response)
            print(f"Скачано {j + 1} из {len(items_cards)}. ({name_item}, {id_item})")


if __name__ == '__main__':
    get_docs()
