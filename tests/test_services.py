import json

import pytest

from src.services import analyze_cashback_categories


# Фикстура для примера транзакций
@pytest.fixture
def transactions():
    return [
        {"Дата операции": "2023-06-15 12:34:56", "Категория": "Продукты", "Кешбэк": 10},
        {"Дата операции": "2023-06-15 12:34:56", "Категория": "Продукты", "Кешбэк": 5},
        {"Дата операции": "2023-06-16 12:34:56", "Категория": "Развлечения", "Кешбэк": 15},
        {"Дата операции": "2023-07-15 12:34:56", "Категория": "Продукты", "Кешбэк": 7}
    ]


def test_analyze_cashback_categories_correct_data(transactions):
    """Тест для проверки корректного подсчета кэшбэка за июнь 2023 года"""
    result = analyze_cashback_categories(transactions, 2023, 6)
    expected_result = {
        "Продукты": 15,
        "Развлечения": 15
    }
    assert json.loads(result) == expected_result


def test_analyze_cashback_categories_empty_result(transactions):
    """Тест для проверки случая, когда нет транзакций за указанный месяц и год"""
    result = analyze_cashback_categories(transactions, 2022, 5)
    expected_result = {}
    assert json.loads(result) == expected_result


def test_analyze_cashback_categories_partial_month(transactions):
    """Тест для проверки подсчета кэшбэка за июль 2023 года (должна быть только одна транзакция)"""
    result = analyze_cashback_categories(transactions, 2023, 7)
    expected_result = {
        "Продукты": 7
    }
    assert json.loads(result) == expected_result


def test_analyze_cashback_categories_no_transactions():
    """Тест для проверки случая, когда список транзакций пуст"""
    transactions = []
    result = analyze_cashback_categories(transactions, 2023, 6)
    expected_result = {}
    assert json.loads(result) == expected_result


def test_analyze_cashback_categories_invalid_date_format():
    """Тест для проверки случая с некорректным форматом даты"""
    transactions = [
        {"Дата операции": "2023/06/15 12:34:56", "Категория": "Продукты", "Кешбэк": 10},
    ]
    with pytest.raises(ValueError):
        analyze_cashback_categories(transactions, 2023, 6)
