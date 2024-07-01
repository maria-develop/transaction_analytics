import pytest

from src.transaction_filter import count_transactions_by_category, filter_transactions_by_description


# Фикстура для примера транзакций
@pytest.fixture
def transactions():
    return [
        {"description": "Coffee shop"},
        {"description": "Grocery store"},
        {"description": "Bookstore purchase"},
        {"description": "Gas station"},
        {"description": "Restaurant dinner"}
    ]


def test_filter_transactions_by_description_no_match(transactions):
    """Тест для проверки фильтрации транзакций по описанию, когда нет совпадений"""
    search_string = "electronics"
    result = filter_transactions_by_description(transactions, search_string)
    expected_result = []
    assert result == expected_result


def test_count_transactions_by_category(transactions):
    """Тест для проверки подсчета транзакций по категориям"""
    categories = ["Coffee", "Grocery", "Bookstore", "Gas", "Restaurant"]
    result = count_transactions_by_category(transactions, categories)
    expected_result = {
        "Coffee": 1,
        "Grocery": 1,
        "Bookstore": 1,
        "Gas": 1,
        "Restaurant": 1
    }
    assert result == expected_result


def test_count_transactions_by_category_multiple_matches(transactions):
    """Тест для проверки подсчета транзакций по категориям с множественными совпадениями"""
    transactions_with_multiple_matches = transactions + [
        {"description": "Grocery shopping"},
        {"description": "Gas refill"}
    ]
    categories = ["Coffee", "Grocery", "Bookstore", "Gas", "Restaurant"]
    result = count_transactions_by_category(transactions_with_multiple_matches, categories)
    expected_result = {
        "Coffee": 1,
        "Grocery": 2,
        "Bookstore": 1,
        "Gas": 2,
        "Restaurant": 1
    }
    assert result == expected_result


def test_count_transactions_by_category_no_match(transactions):
    """Тест для проверки случая, когда ни одна транзакция не попадает в указанные категории"""
    categories = ["Electronics", "Clothing"]
    result = count_transactions_by_category(transactions, categories)
    expected_result = {}
    assert result == expected_result
