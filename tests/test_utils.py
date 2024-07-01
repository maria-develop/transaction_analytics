import unittest
from unittest.mock import mock_open, patch

import pandas as pd
import pytest
import requests

from src.utils import get_card_summary, get_currency_rates, get_data_file_path, get_stock_prices, get_top_transactions


# Фикстура для создания тестового DataFrame
@pytest.fixture
def transactions():
    return pd.DataFrame({
        'Номер карты': ['1234567890123456', '6543210987654321'],
        'Сумма операции': [1000, 1500],
        'Категория': ['еда', 'одежда'],
        'Описание': ['покупка еды', 'покупка одежды'],
        'Дата операции': pd.to_datetime(['2022-01-01', '2022-01-02'])
    })


def test_get_card_summary(transactions):
    """роверяет правильность работы функции get_card_summary с использованием фикстуры transactions."""
    result = get_card_summary(transactions)
    expected = [
        {'last_digits': '3456', 'total_spent': 1000.0, 'cashback': 10},
        {'last_digits': '4321', 'total_spent': 1500.0, 'cashback': 15}
    ]
    assert result == expected


def test_get_top_transactions(transactions):
    """Проверяет правильность работы функции get_top_transactions с использованием фикстуры transactions."""
    result = get_top_transactions(transactions)
    expected = [
        {
            "date": '02.01.2022',
            "amount": 1500,
            "category": 'одежда',
            "description": 'покупка одежды'
        },
        {
            "date": '01.01.2022',
            "amount": 1000,
            "category": 'еда',
            "description": 'покупка еды'
        }
    ]
    assert result == expected


@pytest.fixture
def sample_transactions():
    data = {
        "Дата операции": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06"],
        "Сумма операции": [200, 150, 50, 300, 100, 250],
        "Категория": ["Category1", "Category2", "Category3", "Category4", "Category5", "Category6"],
        "Описание": ["Description1", "Description2", "Description3", "Description4", "Description5", "Description6"]
    }
    return pd.DataFrame(data)


def test_get_top_transactions_success(sample_transactions):
    """Ожидается, что функция вернет топ-5 транзакций, отсортированных по сумме операции."""
    expected = [
        {"date": "04.01.2023", "amount": 300, "category": "Category4", "description": "Description4"},
        {"date": "06.01.2023", "amount": 250, "category": "Category6", "description": "Description6"},
        {"date": "01.01.2023", "amount": 200, "category": "Category1", "description": "Description1"},
        {"date": "02.01.2023", "amount": 150, "category": "Category2", "description": "Description2"},
        {"date": "05.01.2023", "amount": 100, "category": "Category5", "description": "Description5"}
    ]
    result = get_top_transactions(sample_transactions)
    assert result == expected


def test_get_top_transactions_missing_columns(sample_transactions):
    """Имитация ситуации, когда в DataFrame отсутствует необходимый столбец"""
    transactions = sample_transactions.drop(columns=['Категория'])
    result = get_top_transactions(transactions)
    expected = []
    assert result == expected


def test_get_top_transactions_invalid_dates(sample_transactions):
    """Имитация ситуации, когда в DataFrame содержатся некорректные даты"""
    sample_transactions.loc[0, 'Дата операции'] = 'invalid date'
    result = get_top_transactions(sample_transactions)
    expected = []
    assert result == expected


@patch('src.utils.requests.get')
@patch('builtins.open', new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
def test_get_currency_rates(mock_file, mock_get):
    """Использует patch для имитации открытия файла и вызова API"""
    mock_get.side_effect = [
        unittest.mock.Mock(status_code=200, json=lambda: {"rates": {"RUB": 75.0}}),
        unittest.mock.Mock(status_code=200, json=lambda: {"rates": {"RUB": 85.0}})
    ]
    result = get_currency_rates()
    expected = [
        [{"currency": "USD", "rate": 75.0}],
        [{"currency": "EUR", "rate": 85.0}]
    ]
    assert result == expected


@patch('builtins.open', new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
@patch('src.utils.requests.get')
def test_get_currency_rates_success(mock_get, mock_file):
    """Имитация успешного открытия файла и вызова API"""
    mock_get.side_effect = [
        unittest.mock.Mock(status_code=200, json=lambda: {"rates": {"RUB": 75.0}}),
        unittest.mock.Mock(status_code=200, json=lambda: {"rates": {"RUB": 85.0}})
    ]
    result = get_currency_rates()
    expected = [
        [{"currency": "USD", "rate": 75.0}],
        [{"currency": "EUR", "rate": 85.0}]
    ]
    assert result == expected


@patch('builtins.open', new_callable=mock_open)
def test_get_currency_rates_file_not_found(mock_file):
    """Проверка, что функция возвращает пустой список"""
    mock_file.side_effect = FileNotFoundError
    result = get_currency_rates()
    expected = []
    assert result == expected


@patch('builtins.open', new_callable=mock_open, read_data='invalid json')
def test_get_currency_rates_invalid_json(mock_file):
    """Имитация ситуации, когда файл содержит некорректный JSON"""
    result = get_currency_rates()
    expected = []
    assert result == expected


@patch('builtins.open', new_callable=mock_open, read_data='{"user_currencies": ["USD"]}')
def test_get_currency_rates_insufficient_currencies(mock_file):
    """митация ситуации, когда в файле содержится недостаточное количество валют"""
    result = get_currency_rates()
    expected = []
    assert result == expected


@patch('builtins.open', new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
@patch('src.utils.requests.get')
def test_get_currency_rates_request_exception(mock_get, mock_file):
    """Имитация ситуации, когда при вызове API происходит ошибка"""
    mock_get.side_effect = requests.RequestException
    result = get_currency_rates()
    expected = []
    assert result == expected


@patch('src.utils.requests.get')
@patch('builtins.open', new_callable=mock_open, read_data='{"user_stocks": ["AAPL", "GOOG"]}')
def test_get_stock_prices(mock_file, mock_get):
    """Использует patch для имитации открытия файла и вызова API"""
    mock_get.side_effect = [
        unittest.mock.Mock(status_code=200, json=lambda: {"Global Quote": {"05. price": "150.00"}}),
        unittest.mock.Mock(status_code=200, json=lambda: {"Global Quote": {"05. price": "2800.00"}})
    ]
    result = get_stock_prices()
    expected = [
        {"stock": "AAPL", "price": "150.00"},
        {"stock": "GOOG", "price": "2800.00"}
    ]
    assert result == expected


@patch('os.path.join', return_value='/mocked/path/data/filename')
def test_get_data_file_path(mock_join):
    """Использует patch для имитации функции os.path.join"""
    result = get_data_file_path('filename')
    expected = '/mocked/path/data/filename'
    assert result == expected
