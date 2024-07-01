import datetime
import json
import logging
import os
from typing import Any

import pandas as pd

from config import LOGS_DIR
# import requests
from src.utils import get_card_summary, get_currency_rates, get_stock_prices, get_top_transactions

logger = logging.getLogger("views")
logger.setLevel(logging.INFO)


log_file = os.path.join(LOGS_DIR, "views.log")
print(log_file)


file_handler = logging.FileHandler(log_file)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def convert_dates(obj: Any) -> Any:
    """Рекурсивное преобразование объектов datetime в строки."""
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    return obj


def generate_main_page_response(transactions: pd.DataFrame | Any, date_str: str | Any) -> str | Any:
    """Генерация ответа в формате JSON для главной страницы."""
    logger.info("Начало генерации ответа для главной страницы")
    try:
        # Определение текущего месяца и года
        now = datetime.datetime.now()
        start_date = datetime.datetime(now.year, now.month, 1)

        # greeting = get_greeting(now)

        # Преобразование столбцов с датами в формат datetime, если это еще не сделано
        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], errors='coerce')

        # Фильтрация транзакций по дате (с начала текущего месяца)
        transactions = transactions[transactions['Дата операции'] >= start_date]

        # Логирование отфильтрованных транзакций
        logger.debug(f"Фильтрованные транзакции: {transactions}")

        # Преобразование столбцов с датами в строковый формат
        transactions = transactions.copy()
        for col in transactions.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns:
            transactions[col] = transactions[col].astype(str)

        logger.debug(f"Транзакции после преобразования дат: {transactions.head()}")

        cards_summary = get_card_summary(transactions)
        logger.debug(f"Сводка по картам: {cards_summary}")

        top_transactions = get_top_transactions(transactions)
        logger.debug(f"Топ-5 транзакций: {top_transactions}")

        currency_rates = get_currency_rates()
        logger.debug(f"Курсы валют: {currency_rates}")

        stock_prices = get_stock_prices()
        logger.debug(f"Котировки акций: {stock_prices}")

        # Определение текущего месяца и года
        now = datetime.datetime.now()
        # start_date = datetime.datetime(now.year, now.month, 1)

        greeting = get_greeting(now)

        response = {
            "greeting": greeting,
            "cards": cards_summary,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices
        }

        # Преобразуем все даты в строки перед сериализацией
        response = convert_dates(response)

        logger.info("Ответ для главной страницы успешно сгенерирован")
        return json.dumps(response, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка при генерации ответа для главной страницы: {e}")
        return json.dumps({"error": "Ошибка генерации ответа для главной страницы"}, ensure_ascii=False, indent=4)


def get_greeting(date: datetime.datetime) -> str:
    """Приветственные сообщения в зависимости от времени суток."""
    logger.info(f"Определение приветствия для времени: {date}")
    if 6 <= date.hour < 12:
        greeting = "Доброе утро"
    elif 12 <= date.hour < 18:
        greeting = "Добрый день"
    elif 18 <= date.hour < 22:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"
    logger.debug(f"Приветствие: {greeting}")
    return greeting
