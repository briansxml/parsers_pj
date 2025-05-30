import time
import json
import logging
import random
from datetime import datetime
import requests
from bs4 import BeautifulSoup
# from google_play_scraper import search as gp_search
from logging import FileHandler

# 🔧 Настройки
KEYWORDS = ["Telegram", "WhatsApp"]
INTERVAL = 12000  # Базовая пауза между циклами (в секундах)
DELAY_RANGE = (2, 6)  # Задержка между запросами (секунды)

# 📝 Логирование
log_handler = FileHandler('parser.log', encoding='utf-8')
logging.basicConfig(
    handlers=[log_handler],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# 📲 Telegram-уведомление
def send_telegram_message(message):
    token = '6927527203:AAHnOj-4ddQkgYb94FNfBcFiMJ02mZZHMcY'
    chat_id = '451073723'
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    try:
        requests.post(url, data=payload, timeout=10)
        logging.info("📲 Отправлено в Telegram.")
    except Exception as e:
        logging.error(f"❌ Ошибка Telegram: {e}")


# 🔍 Поиск в Google Play
def search_google_play(keyword, num_results=8):
    try:
        results = gp_search(keyword, lang='ru', country='ru')
        apps = []
        for app in results[:num_results]:
            apps.append({
                'platform': 'Google Play',
                'keyword': keyword,
                'title': app.get('title', ''),
                'developer': app.get('developer', ''),
                'url': f"https://play.google.com/store/apps/details?id={app.get('appId', '')}"
            })
        return apps
    except Exception as e:
        logging.error(f"❌ Google Play ошибка для '{keyword}': {e}")
        return []

# 🔍 Поиск в App Store через iTunes Search API
def search_app_store(keyword, country='US', num_results=8):
    url = 'https://itunes.apple.com/search'
    params = {
        'term': keyword,
        'country': country,
        'media': 'software',
        'limit': num_results
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        apps = []
        for app in data.get('results', []):
            apps.append({
                'platform': 'App Store',
                'keyword': keyword,
                'title': app.get('trackName', ''),
                'developer': app.get('artistName', ''),
                'url': app.get('trackViewUrl', '')
            })
        return apps
    except Exception as e:
        logging.error(f"❌ App Store ошибка для '{keyword}': {e}")
        return []


# 🔍 Поиск в RuStore
def search_rustore(keyword, num_results=5):
    search_url = f"https://apps.rustore.ru/search?query={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        app_list = soup.find('ul', {'data-testid': "appslist"})
        app_cards = app_list.find_all('li')
        apps = []
        for card in app_cards[:num_results]:
            title_tag = card.find('p', {'itemprop': 'name'}).text
            link = "https://apps.rustore.ru" + card.find('a')['href']
            r = requests.get(link, headers=headers, timeout=10)
            soup_dev = BeautifulSoup(r.text, 'lxml')
            dev_info = soup_dev.find('div', {'data-testid': "developerInfo"}).find('div')
            dev_name = dev_info.find('div', {'data-testid': False})
            developer_tag = dev_name.text if dev_name else dev_info.find('a', {'data-testid': 'link'}).text
            apps.append({
                'platform': 'RuStore',
                'keyword': keyword,
                'title': title_tag.strip() if title_tag else '',
                'developer': developer_tag.strip() if developer_tag else '',
                'url': link
            })
        return apps
    except Exception as e:
        logging.error(f"❌ RuStore ошибка для '{keyword}': {e}")
        return []


# 📂 Загрузка известных приложений
def load_known_app_ids():
    try:
        with open('known_apps.json', 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except:
        return set()


# 💾 Сохранение известных приложений
def save_known_app_ids(app_ids):
    with open('known_apps.json', 'w', encoding='utf-8') as f:
        json.dump(list(app_ids), f, ensure_ascii=False, indent=2)


# 🚀 Основная логика
def run_parser():
    all_results = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"🚀 Запуск парсера — {timestamp}")
    print(f"\n📅 {timestamp} — старт парсинга\n")

    for keyword in KEYWORDS:
        print(f"🔎 Ключ: {keyword}")

        gp = search_google_play(keyword)
        time.sleep(random.uniform(*DELAY_RANGE))

        ios = search_app_store(keyword)
        time.sleep(random.uniform(*DELAY_RANGE))

        ru = search_rustore(keyword)
        time.sleep(random.uniform(*DELAY_RANGE))

        all_results.extend(gp + ios + ru)

    new_results = []
    known_ids = load_known_app_ids()
    new_ids = set()

    for app in all_results:
        unique_id = f"{app['platform']}::{app['url']}"
        if unique_id not in known_ids:
            new_results.append(app)
            new_ids.add(unique_id)

    if not new_results:
        logging.info("🟡 Нет новых приложений.")
        return

    data_to_save = {
        'timestamp': timestamp,
        'results': new_results
    }
    try:
        with open("results.json", "a", encoding='utf-8') as f:
            f.write(json.dumps(data_to_save, ensure_ascii=False, indent=2))
            f.write("\n\n")
        logging.info(f"✅ Сохранено {len(new_results)} новых приложений.")
    except Exception as e:
        logging.error(f"❌ Ошибка при сохранении JSON: {e}")

    save_known_app_ids(known_ids.union(new_ids))

    message = f"📱 <b>Новые приложения за {timestamp}</b>\n"
    for app in new_results:
        message += f"\n<b>{app['platform']}</b>: {app['title']} ({app['developer']})\n{app['url']}\n"
    send_telegram_message(message)

    print(f"📩 Отправлено {len(new_results)} новых приложений в Telegram.")


# 🔁 Бесконечный цикл
def main_loop():
    while True:
        run_parser()
        extra_delay = random.uniform(*DELAY_RANGE)
        total_pause = INTERVAL + extra_delay
        print(f"⏳ Пауза {int(total_pause) // 600} мин ({int(total_pause)} сек)...\n")
        time.sleep(total_pause)


if __name__ == "__main__":
    main_loop()
