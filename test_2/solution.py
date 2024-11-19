import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import csv
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session():
    """
    Создает сессию requests с механизмом повторных попыток
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=5,  # количество повторных попыток
        backoff_factor=1,  # фактор задержки между попытками
        status_forcelist=[500, 502, 503, 504, 404],  # коды ошибок для повторных попыток
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_page_content(url, session, max_retries=3):
    """
    Получает содержимое страницы по указанному URL с механизмом повторных попыток.

    :param url: URL страницы
    :param session: Сессия requests
    :param max_retries: Максимальное количество попыток
    :return: Объект BeautifulSoup с содержимым страницы
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }

    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except (requests.RequestException, ConnectionResetError) as e:
            if attempt == max_retries - 1:  # если это последняя попытка
                raise
            print(f"Попытка {attempt + 1} не удалась: {str(e)}")
            time.sleep(5 * (attempt + 1))  # увеличиваем время ожидания с каждой попыткой

    raise Exception("Превышено максимальное количество попыток")


def parse_animal_names(url, session):
    """
    Парсит имена животных со страницы.

    :param url: URL страницы с категорией животных
    :param session: Сессия requests
    :return: Список имён животных и ссылка на следующую страницу
    """
    soup = fetch_page_content(url, session)
    animals = [a.text for a in soup.select('#mw-pages .mw-category.mw-category-columns  li a')]

    next_page = soup.find('a', string='Следующая страница')
    next_page_url = None
    if next_page and 'href' in next_page.attrs:
        next_page_url = f"https://ru.wikipedia.org{next_page['href']}"

    return animals, next_page_url


def collect_all_animals(url='https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту'):
    """
    Собирает полный список животных, переходя по всем страницам категории.

    :param url: URL страницы с категорией животных
    :return: Полный список имён животных
    """
    all_animals = []
    current_url = url
    page_count = 1
    session = create_session()

    while current_url:
        print(f"Обработка страницы {page_count}...")
        try:
            animals, next_url = parse_animal_names(current_url, session)
            all_animals.extend(animals)
            print(f"Найдено животных на странице: {len(animals)}")
            current_url = next_url
            page_count += 1


        except Exception as e:
            print(f"Ошибка при обработке страницы {current_url}: {e}")
            print("Ожидание 30 секунд перед повторной попыткой...")
            time.sleep(10)
            # Пробуем создать новую сессию
            session = create_session()
            continue

    return all_animals


def save_intermediate_results(animals, filename):
    """
    Сохраняет промежуточные результаты в файл.

    :param animals: Список животных
    :param filename: Имя файла для сохранения
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for animal in animals:
            f.write(animal + '\n')


def count_animals_by_letter(animal_list):
    """
    Считает количество животных по первой букве их имени.

    :param animal_list: Список имён животных
    :return: Словарь с подсчетом животных по буквам
    """
    animal_counts = defaultdict(int)
    for animal in animal_list:
        if animal.strip():  # Проверяем, что строка не пустая
            first_letter = animal[0].upper()
            animal_counts[first_letter] += 1
    return dict(animal_counts)


def save_counts_to_csv(animal_counts, filename='beasts.csv'):
    """
    Сохраняет данные о подсчёте животных по буквам в CSV-файл.

    :param animal_counts: Словарь с подсчётом животных по буквам
    :param filename: Имя файла для сохранения
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for letter, count in sorted(animal_counts.items()):
            writer.writerow([letter, count])


def main():
    """
    Основная функция для запуска полной процедуры: сбор животных, подсчёт, сохранение.
    """
    url = 'https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту'
    print("Сбор всех животных...")

    try:
        all_animals = collect_all_animals(url)
        print(f"Найдено {len(all_animals)} животных.")

        print("Подсчёт животных по буквам...")
        animal_counts = count_animals_by_letter(all_animals)

        print("Сохранение результатов в файл...")
        save_counts_to_csv(animal_counts)
        print("Готово! Результаты сохранены в beasts.csv")

    except Exception as e:
        print(f"Произошла критическая ошибка: {e}")
        # Если есть промежуточные результаты, сохраняем их
        if 'all_animals' in locals() and all_animals:
            print("Сохранение промежуточных результатов...")
            save_intermediate_results(all_animals, 'animals_intermediate_error.txt')
            animal_counts = count_animals_by_letter(all_animals)
            save_counts_to_csv(animal_counts, 'beasts_intermediate.csv')
            print("Промежуточные результаты сохранены.")


if __name__ == '__main__':
    main()
