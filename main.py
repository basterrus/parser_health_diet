import csv
import json
import random
from time import sleep
import requests
from bs4 import BeautifulSoup
import lxml

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/88.0.4324.150 Safari/537.36',
    'accept': '*/*'
}

url = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'


def load_main_page():
    req = requests.get(url=url, headers=headers)
    src = req.text

    with open(f'data/index.html', 'w', encoding='utf-8') as file:
        file.write(src)
    print(f'Основная страницы сохранена!!')


def open_main_page_save_json():
    with open(f'data/index.html', 'r', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    index_all_href = soup.find_all(class_='mzr-tc-group-item-href')
    # Получем все ссылки
    all_href_dict = {}
    for item in index_all_href:
        item_name = item.text
        item_href = 'https://health-diet.ru' + item.get('href')

        all_href_dict[item_name] = item_href

        with open(f'data/all_href.json', 'w', encoding='utf-8') as file:
            json.dump(all_href_dict, file, indent=4, ensure_ascii=False)

    print(f'Ссылки с онсновной страницы сохранены в файйл _data/all_href.json_')


def load_json_and_load_data():
    with open(f'data/all_href.json', 'r', encoding='utf-8') as file:
        all_categories = json.load(file)

    iteration_count = int(len(all_categories)) - 1
    count = 0

    for category_name, category_href in all_categories.items():

        rep = [' ', ',', '-', "'"]
        for item in rep:
            if item in category_name:
                category_name = category_name.replace(item, '_')

        req = requests.get(url=category_href, headers=headers)
        src = req.text

        with open(f'data/{count}_{category_name}.html', 'w', encoding='utf-8') as file:
            file.write(src)

        with open(f'data/{count}_{category_name}.html', 'r', encoding='utf-8') as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')

        alert_block = soup.find(class_='uk-alert-danger')
        if alert_block is not None:
            continue

        table_head = soup.find(class_='uk-overflow-container').find('tr').find_all('th')

        product = table_head[0].text
        calories = table_head[1].text
        proteins = table_head[2].text
        fats = table_head[3].text
        carbohydrates = table_head[4].text

        with open(f'data/{count}_{category_name}.csv', 'w', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    product,
                    calories,
                    proteins,
                    fats,
                    carbohydrates
                )
            )

        product_data = soup.find(class_='uk-overflow-container').find('tbody').find_all('tr')

        product_info = []

        for item in product_data:
            product_tds = item.find_all('td')

            title = product_tds[0].find('a').text
            calories = product_tds[1].text
            proteins = product_tds[2].text
            fats = product_tds[3].text
            carbohydrates = product_tds[4].text

            product_info.append(
                {
                    "Title": title,
                    "Calories": calories,
                    "Proteins": proteins,
                    "Fats": fats,
                    "Carbohydrates": carbohydrates
                }
            )

            with open(f'data/{count}_{category_name}.csv', 'a', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    (
                        title,
                        calories,
                        proteins,
                        fats,
                        carbohydrates
                    )
                )

        with open(f"data/{count}_{category_name}.json", "a", encoding="utf-8") as file:
            json.dump(product_info, file, indent=4, ensure_ascii=False)

        count += 1
        print(f"# Итерация {count}. {category_name} записан...")
        iteration_count = iteration_count - 1

        if iteration_count == 0:
            print("Работа завершена")
            break

        print(f"Осталось итераций: {iteration_count}")
        sleep(random.randrange(1, 3))


load_main_page()
open_main_page_save_json()
load_json_and_load_data()
