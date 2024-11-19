import pytest
import requests
from bs4 import BeautifulSoup
import csv
from unittest.mock import MagicMock

# Импортируем функции из нашего основного скрипта
from solution import (
    fetch_page_content,
    parse_animal_names,
    count_animals_by_letter,
    save_counts_to_csv,
    create_session
)


# Фикстуры для тестов
@pytest.fixture
def sample_html_page():
    """Возвращает пример HTML-страницы с категорией животных"""
    return """
    <div class="mw-category-group">
        <ul>
            <li><a href="/wiki/Аист">Аист</a></li>
            <li><a href="/wiki/Барс">Барс</a></li>
            <li><a href="/wiki/Волк">Волк</a></li>
        </ul>
    </div>
    <a href="/wiki/Категория:Животные_по_алфавиту?pagefrom=..." class="mw-nextlink">Следующая страница</a>
    """


@pytest.fixture
def sample_html_last_page():
    """Возвращает пример последней HTML-страницы категории"""
    return """
    <div class="mw-category-group">
        <ul>
            <li><a href="/wiki/Ящерица">Ящерица</a></li>
        </ul>
    </div>
    """


@pytest.fixture
def mock_session():
    """Создает мок-объект сессии requests"""
    session = MagicMock()
    session.get.return_value.status_code = 200
    return session


# Тесты для fetch_page_content
def test_fetch_page_content_success(mock_session):
    """Проверяет успешное получение содержимого страницы"""
    url = "https://ru.wikipedia.org/wiki/test"
    mock_session.get.return_value.text = "<html><body>Test content</body></html>"

    result = fetch_page_content(url, mock_session)
    assert isinstance(result, BeautifulSoup)
    assert "Test content" in str(result)


def test_fetch_page_content_retry_on_failure(mock_session):
    """Проверяет механизм повторных попыток при ошибке"""
    url = "https://ru.wikipedia.org/wiki/test"
    mock_session.get.side_effect = [
        requests.exceptions.ConnectionError(),
        requests.exceptions.ConnectionError(),
        MagicMock(text="<html><body>Success</body></html>", status_code=200)
    ]

    result = fetch_page_content(url, mock_session)
    assert isinstance(result, BeautifulSoup)
    assert mock_session.get.call_count == 3


# Тесты для count_animals_by_letter
def test_count_animals_by_letter():
    """Проверяет подсчет животных по первой букве"""
    animals = ["Аист", "Антилопа", "Барс", "Волк", "Ворон"]
    result = count_animals_by_letter(animals)

    assert result == {"А": 2, "Б": 1, "В": 2}
    assert sum(result.values()) == 5


def test_count_animals_by_letter_empty_input():
    """Проверяет подсчет при пустом входном списке"""
    result = count_animals_by_letter([])
    assert result == {}


# Тесты для save_counts_to_csv
def test_save_counts_to_csv(tmp_path):
    """Проверяет сохранение результатов в CSV-файл"""
    test_data = {"А": 2, "Б": 1, "В": 3}
    test_file = tmp_path / "test_beasts.csv"

    save_counts_to_csv(test_data, str(test_file))

    assert test_file.exists()
    with open(test_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)
        assert len(data) == 3
        assert data[0] == ["А", "2"]
        assert data[1] == ["Б", "1"]
        assert data[2] == ["В", "3"]


# Тесты для create_session
def test_create_session():
    """Проверяет создание сессии с настроенными retry-параметрами"""
    session = create_session()
    assert isinstance(session, requests.Session)

    # Проверяем, что адаптеры установлены
    assert "http://" in session.adapters
    assert "https://" in session.adapters

    # Проверяем параметры retry
    adapter = session.adapters["https://"]
    assert adapter.max_retries.total == 5
    assert adapter.max_retries.backoff_factor == 1
    assert set(adapter.max_retries.status_forcelist) == {500, 502, 503, 504, 404}


# Тест на обработку ошибок
def test_fetch_page_content_max_retries_exceeded(mock_session):
    """Проверяет, что функция вызывает исключение после превышения максимального числа попыток"""
    url = "https://ru.wikipedia.org/wiki/test"
    mock_session.get.side_effect = requests.exceptions.ConnectionError()

    with pytest.raises(requests.exceptions.ConnectionError):
        fetch_page_content(url, mock_session)

    assert mock_session.get.call_count == 3  # Проверяем, что было сделано 3 попытки


# Дополнительные тесты для проверки граничных случаев
def test_count_animals_by_letter_special_characters():
    """Проверяет обработку специальных символов в именах животных"""
    animals = ["!Кот", "@Собака", "#Мышь"]
    result = count_animals_by_letter(animals)
    assert result == {"!": 1, "@": 1, "#": 1}


def test_parse_animal_names_malformed_html(mock_session):
    """Проверяет обработку некорректного HTML"""
    url = "https://ru.wikipedia.org/wiki/test"
    mock_session.get.return_value.text = "<malformed>><html>"

    animals, next_url = parse_animal_names(url, mock_session)
    assert animals == []
    assert next_url is None