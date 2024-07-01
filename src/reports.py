import datetime
import json
import logging
import os
from typing import Any, Callable, Optional

import pandas as pd

from config import LOGS_DIR

logger = logging.getLogger("reports")
logger.setLevel(logging.INFO)


log_file = os.path.join(LOGS_DIR, "reports.log")
print(log_file)


file_handler = logging.FileHandler(log_file)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] | Any = None)\
        -> pd.DataFrame | Any:
    """Получение информации о расходах по категориям за последние три месяца."""
    logger.info("Начало обработки транзакций по категории")
    try:
        if date is None:
            date = datetime.datetime.now()
            logger.debug(f"Используется текущая дата: {date}")
        else:
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            logger.debug(f"Используется дата из параметра: {date}")

        start_date = date - datetime.timedelta(days=90)
        logger.debug(f"Период начала для фильтрации: {start_date}")

        filtered_transactions = transactions[
            (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= date)]
        logger.debug(f"Количество транзакций после фильтрации по дате: {len(filtered_transactions)}")

        category_transactions = filtered_transactions[filtered_transactions["Категория"] == category]
        logger.debug(f"Количество транзакций после фильтрации по категории: {len(category_transactions)}")

        logger.info("Обработка транзакций по категории завершена")
        return category_transactions
    except Exception as e:
        logger.error(f"Ошибка при обработке транзакций по категории: {e}")
        return pd.DataFrame()  # Возвращаем пустой DataFrame в случае ошибки


def report_decorator(file_name: str = 'report.json') -> Callable:
    """Декоратор для сохранения отчета в файл."""

    def decorator(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: dict) -> Any:
            logger.info(f"Начало выполнения функции {func.__name__} с декоратором для сохранения отчета")
            try:
                result = func(*args, **kwargs)
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                logger.info(f"Начало выполнения функции {func.__name__} с декоратором для сохранения отчета")
                return result
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета в файл {file_name}: {e}")
                return None  # Возвращаем None в случае ошибки

        return wrapper

    return decorator
