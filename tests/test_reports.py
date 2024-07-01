import datetime
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.reports import report_decorator, spending_by_category


@pytest.fixture
def patched_datetime():
    with patch('src.reports.datetime') as mock_datetime:
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 6, 1)
        mock_datetime.datetime.strptime = datetime.datetime.strptime
        yield mock_datetime


@pytest.fixture
def sample_transactions():
    # Replace this with your sample transactions data creation logic
    transactions = pd.DataFrame({
        'Date': ['2023-05-01', '2023-05-02', '2023-05-03'],
        'Category': ['Food', 'Shopping', 'Transport'],
        'Amount': [100.0, 200.0, 50.0],
    })
    return transactions


def test_spending_by_category_exception(sample_transactions):
    """Проверка обработки исключений"""
    with patch('src.reports.datetime') as mock_datetime:
        mock_datetime.datetime.now.side_effect = Exception("Test Exception")

        result = spending_by_category(sample_transactions, "Food")
        expected = pd.DataFrame()

        pd.testing.assert_frame_equal(result, expected)


@pytest.fixture
def mock_func():
    # Простая функция для тестирования
    def mock_function():
        return {"result": "success"}
    return mock_function


def test_report_decorator_exception_handling():
    """Проверяет, что декоратор правильно обрабатывает исключения, выбрасываемые декорированной функцией"""
    file_name = 'test_report.json'
    decorator = report_decorator(file_name)

    # Функция, которая выбрасывает исключение
    def func_with_exception():
        raise ValueError("Test exception")

    # Вызываем функцию с декоратором, которая вызывает исключение
    with patch('builtins.open', mock_open()):
        decorated_func = decorator(func_with_exception)
        result = decorated_func()

        # Проверяем, что функция вернула None из-за ошибки
        assert result is None
