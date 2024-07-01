import re
from collections import Counter


def filter_transactions_by_description(transactions: list[dict], search_string: str) -> list[dict]:
    """Фильтрация транзакций по описанию."""
    pattern = re.compile(search_string, re.IGNORECASE)
    filtered_transactions = [transaction for transaction in transactions if pattern.search(transaction.get(
        "description", ""))]
    return filtered_transactions


def count_transactions_by_category(transactions: list[dict], categories: list[str]) -> dict[str, int]:
    """Подсчет транзакций по категориям."""
    category_count: Counter[str] = Counter()

    for transaction in transactions:
        description = transaction.get("description", "")
        for category in categories:
            if category in description:
                category_count[category] += 1
                break

    return dict(category_count)
