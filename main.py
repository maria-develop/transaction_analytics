from typing import Any

import pandas as pd

from src.reports import report_decorator, spending_by_category
from src.services import analyze_cashback_categories
from src.utils import get_data_file_path
from src.views import generate_main_page_response


def main() -> Any:
    transactions_path = get_data_file_path('transactions.xlsx')
    transactions = pd.read_excel(transactions_path, engine='openpyxl')
    date_str = "2022-01-01 12:00:00"  # Example date
    response = generate_main_page_response(transactions, date_str)
    print(response)
    return analyze_cashback_categories, spending_by_category, report_decorator  # вывод логов


if __name__ == '__main__':
    main()
