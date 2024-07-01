import datetime
import json
import logging
from unittest.mock import patch

import pandas as pd
import pytest

from src.views import generate_main_page_response, get_greeting


@pytest.fixture
def mock_transactions():
    return pd.DataFrame({
        'Дата операции': ['2024-06-01', '2024-06-02', '2024-06-03'],
        'Категория': ['Food', 'Shopping', 'Transport'],
        'Сумма операции': [100.0, 200.0, 50.0],
        'Описание': ['Coffee shop', 'Grocery store', 'Gas station']
    })


@patch('src.views.get_card_summary')
@patch('src.views.get_top_transactions')
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
@patch('src.views.get_greeting')
def test_generate_main_page_response_basic(mock_get_greeting, mock_get_stock_prices,
                                           mock_get_currency_rates, mock_get_top_transactions,
                                           mock_get_card_summary, mock_transactions):
    """Проверяет базовый сценарий работы функции без ошибок"""
    mock_get_greeting.return_value = "Добрый день"
    mock_get_card_summary.return_value = {"total_spent": 350.0}
    mock_get_top_transactions.return_value = [
        {"date": "01.06.2024", "amount": 200.0, "category": "Shopping", "description": "Grocery store"},
        {"date": "02.06.2024", "amount": 100.0, "category": "Food", "description": "Coffee shop"}
    ]
    mock_get_currency_rates.return_value = {"USD": 72.5, "EUR": 85.2}
    mock_get_stock_prices.return_value = {"AAPL": 140.0, "GOOG": 2500.0}

    # Успешный вызов функции
    response = generate_main_page_response(mock_transactions, "2024-06-01")
    expected_response = {
        "greeting": "Добрый день",
        "cards": {"total_spent": 350.0},
        "top_transactions": [
            {"date": "01.06.2024", "amount": 200.0, "category": "Shopping", "description": "Grocery store"},
            {"date": "02.06.2024", "amount": 100.0, "category": "Food", "description": "Coffee shop"}
        ],
        "currency_rates": {"USD": 72.5, "EUR": 85.2},
        "stock_prices": {"AAPL": 140.0, "GOOG": 2500.0}
    }
    assert json.loads(response) == expected_response


@patch('src.views.get_card_summary')
@patch('src.views.get_top_transactions')
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
@patch('src.views.get_greeting')
def test_generate_main_page_response_empty_data(mock_get_greeting, mock_get_stock_prices,
                                                mock_get_currency_rates, mock_get_top_transactions,
                                                mock_get_card_summary):
    """Проверяет, что функция корректно обрабатывает пустой DataFrame в качестве входных данных
     и возвращает ожидаемое сообщение об ошибке"""
    # Пустой DataFrame в качестве входных данных
    mock_transactions = pd.DataFrame()
    response = generate_main_page_response(mock_transactions, "2024-06-01")
    expected_response = {"error": "Ошибка генерации ответа для главной страницы"}
    assert json.loads(response) == expected_response


@patch('src.views.get_card_summary')
@patch('src.views.get_top_transactions')
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
@patch('src.views.get_greeting')
def test_generate_main_page_response_logging(mock_get_greeting, mock_get_stock_prices,
                                             mock_get_currency_rates, mock_get_top_transactions,
                                             mock_get_card_summary, mock_transactions, caplog):
    """Проверяет, что сообщения логирования правильно записываются в лог при выполнении функции"""
    mock_get_greeting.return_value = "Добрый день"
    mock_get_card_summary.return_value = {"total_spent": 350.0}
    mock_get_top_transactions.return_value = [
        {"date": "01.06.2024", "amount": 200.0, "category": "Shopping", "description": "Grocery store"},
        {"date": "02.06.2024", "amount": 100.0, "category": "Food", "description": "Coffee shop"}
    ]
    mock_get_currency_rates.return_value = {"USD": 72.5, "EUR": 85.2}
    mock_get_stock_prices.return_value = {"AAPL": 140.0, "GOOG": 2500.0}

    # Успешный вызов функции
    with caplog.at_level(logging.DEBUG):
        generate_main_page_response(mock_transactions, "2024-06-01")


@patch('src.views.get_card_summary')
@patch('src.views.get_top_transactions')
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
@patch('src.views.get_greeting')
def test_generate_main_page_response_exception_handling(mock_get_greeting, mock_get_stock_prices,
                                                        mock_get_currency_rates, mock_get_top_transactions,
                                                        mock_transactions, caplog):
    """Проверяется, что функция корректно логирует ошибку и возвращает ожидаемое сообщение об ошибке"""
    # Функция выбрасывает исключение
    mock_get_greeting.side_effect = Exception("Test exception")
    response = generate_main_page_response(mock_transactions, "2024-06-01")
    expected_response = {"error": "Ошибка генерации ответа для главной страницы"}
    assert json.loads(response) == expected_response

    # Проверка наличия ошибки в логах
    assert "Ошибка при генерации ответа для главной страницы" in caplog.text


@patch('src.views.datetime')
def test_get_greeting(mock_datetime):
    """Устанавливаем мок для datetime.now"""
    mock_datetime.now.return_value = datetime.datetime(2024, 6, 1, 10, 0, 0)

    # Вызываем функцию и проверяем результат для разных времен суток
    assert get_greeting(datetime.datetime(2024, 6, 1, 8, 0, 0)) == "Доброе утро"
    assert get_greeting(datetime.datetime(2024, 6, 1, 14, 0, 0)) == "Добрый день"
    assert get_greeting(datetime.datetime(2024, 6, 1, 20, 0, 0)) == "Добрый вечер"
    assert get_greeting(datetime.datetime(2024, 6, 1, 2, 0, 0)) == "Доброй ночи"
