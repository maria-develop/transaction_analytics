import json
import logging
import os
from typing import Any

import pandas as pd
import requests

from config import LOGS_DIR

from dotenv import load_dotenv


logger = logging.getLogger("utils")
logger.setLevel(logging.INFO)


log_file = os.path.join(LOGS_DIR, "utils.log")
print(log_file)


file_handler = logging.FileHandler(log_file)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_card_summary(transactions: pd.DataFrame | Any) -> list[dict] | Any:
    """Получение сводки расходов и кэшбэка по карте."""
    logger.info("Начало получения сводки расходов и кэшбэка по карте")
    summary = []
    for card, group in transactions.groupby("Номер карты"):
        total_spent = group["Сумма операции"].sum()
        cashback = total_spent // 100
        summary.append({
            "last_digits": card[-4:],
            "total_spent": round(total_spent, 2),
            "cashback": cashback
        })
        logger.info(f"Карта {card[-4:]!r}: потрачено {total_spent}, кэшбэк {cashback}")
    logger.info("Сводка расходов и кэшбэка по карте получена")
    return summary


def get_top_transactions(transactions: pd.DataFrame) -> list[dict]:
    """Получение топ-5 транзакций по сумме."""
    # top_transactions = transactions.nlargest(5, 'Сумма операции')

    # Преобразование топ-5 транзакций в нужный формат
    # top_transactions_list = [
    #     {
    #         "date": row['Дата операции'].strftime("%d.%m.%Y"),
    #         "amount": row['Сумма операции'],
    #         "category": row['Категория'],
    #         "description": row['Описание']
    #     }
    #     for _, row in top_transactions.iterrows()
    # ]
    #
    # return top_transactions_list

    logger.info("Начало получения топ-5 транзакций по сумме")

    required_columns = ['Дата операции', 'Сумма операции', 'Категория', 'Описание']
    missing_columns = [col for col in required_columns if col not in transactions.columns]

    if missing_columns:
        logger.error(f"Отсутствуют необходимые столбцы: {missing_columns}")
        return []

    try:
        # Преобразование столбца 'Дата операции' в datetime
        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], errors='coerce')

        # Проверка на наличие недопустимых дат
        if transactions['Дата операции'].isnull().any():
            logger.error("Некоторые даты не удалось преобразовать. Проверьте данные.")
            return []

        # Получение топ-5 транзакций по сумме
        top_transactions = transactions.nlargest(5, 'Сумма операции')
        logger.debug(f"Топ-5 транзакций: {top_transactions}")

        # Преобразование топ-5 транзакций в нужный формат
        top_transactions_list = [
            {
                "date": row['Дата операции'].strftime("%d.%m.%Y"),
                "amount": row['Сумма операции'],
                "category": row['Категория'],
                "description": row['Описание']
            }
            for _, row in top_transactions.iterrows()
        ]

        logger.info("Топ-5 транзакций по сумме получены")
        return top_transactions_list
    except Exception as e:
        logger.error(f"Ошибка при получении топ-5 транзакций: {e}")
        return []

    # top_transactions_list = top_transactions.to_dict(orient='records')
    # Преобразование Timestamp в строку
    # for transaction in top_transactions_list:
    #     if isinstance(transaction['Дата операции'], pd.Timestamp):
    #         transaction['Дата операции'] = transaction['Дата операции'].strftime('%Y-%m-%d %H:%M:%S')
    #
    # return top_transactions_list


def get_currency_rates() -> list[list[dict[str, Any]] | list[dict[str, Any]]]:
    """Получение курсов валют из API."""
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_settings.json"), "r") as file:
            parsed_data = json.load(file)
        logger.info("Файл user_settings.json успешно загружен")
        # print(parsed_data)
        if "user_currencies" not in parsed_data or len(parsed_data["user_currencies"]) < 2:
            logger.info("Файл user_settings.json успешно загружен")
            # print("Ошибка: Неверный формат user_settings.json")
            return []

        info_0 = parsed_data["user_currencies"][0]
        info_1 = parsed_data["user_currencies"][1]
        logger.debug(f"Валюты для запроса: {info_0}, {info_1}")
        # print(info_0, info_1)

        response_usd = requests.get(f"https://api.exchangerate-api.com/v4/latest/{info_0}")
        data_us = response_usd.json()
        response_eur = requests.get(f"https://api.exchangerate-api.com/v4/latest/{info_1}")
        data_eu = response_eur.json()

        currency_usd = [{"currency": info_0, "rate": value} for key, value in data_us["rates"].items() if key in "RUB"]
        currency_eur = [{"currency": info_1, "rate": value} for key, value in data_eu["rates"].items() if key in "RUB"]
        logger.info("Курсы валют успешно получены")
        return [currency_usd, currency_eur]

    except FileNotFoundError:
        # print("Ошибка: Файл user_settings.json не найден.")
        logger.error("Файл user_settings.json не найден")
        return []
    except json.JSONDecodeError:
        # print("Ошибка: Невозможно прочитать JSON из файла user_settings.json.")
        logger.error("Невозможно прочитать JSON из файла user_settings.json")
        return []
    except requests.RequestException as e:
        # print(f"Ошибка: Не удалось получить данные от API. {e}")
        logger.error(f"Не удалось получить данные от API: {e}")
        return []


# Загрузка переменных окружения из файла .env
load_dotenv()

API_KEY_ALPHA = os.getenv('API_KEY_ALPHA')


def get_stock_prices() -> list[dict]:
    """Получение котировок акций из API."""
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_settings.json"), "r") as file:
            parsed_data = json.load(file)
        logger.info("Файл user_settings.json успешно загружен")

        stocks = parsed_data.get("user_stocks", [])

        if not stocks:
            # print("Нет акций для запроса.")
            logger.warning("Нет акций для запроса")
            return []

        stock_prices = []

        # api_key = 'VUEXCGD9IAALMKED'
        api_key = API_KEY_ALPHA
        base_url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={apikey}'

        for stock in stocks:
            url = base_url.format(symbol=stock, apikey=api_key)
            response = requests.get(url)
            data = response.json()

            if "Global Quote" in data:
                logger.debug(f"Котировка для {stock}: {data['Global Quote']}")
                # print(f"Котировка для {stock}: {data['Global Quote']}")
                stock_prices.append({
                    "stock": stock,
                    "price": data["Global Quote"].get("05. price", "Нет данных")
                })
            else:
                # print(f"Не удалось получить котировку для {stock}")
                logger.warning(f"Не удалось получить котировку для {stock}")
                stock_prices.append({
                    "stock": stock,
                    "price": "Нет данных"
                })

        logger.info("Котировки акций успешно получены")
        return stock_prices

    except FileNotFoundError:
        # print("Ошибка: Файл user_settings.json не найден.")
        logger.error("Файл user_settings.json не найден")
        return []
    except json.JSONDecodeError:
        # print("Ошибка: Невозможно прочитать JSON из файла user_settings.json.")
        logger.error("Невозможно прочитать JSON из файла user_settings.json")
        return []
    except requests.RequestException as e:
        # print(f"Ошибка: Не удалось получить данные от API. {e}")
        logger.error(f"Не удалось получить данные от API: {e}")
        return []


def get_data_file_path(filename: str) -> str:
    """Получение абсолютного пути к файлу данных."""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', filename)
    logger.info(f"Абсолютный путь к файлу данных: {path}")
    return path


if __name__ == "__main__":
    rates = get_currency_rates()
    print("Результат вызова функции get_currency_rates:", rates)
    prices = get_stock_prices()
    print("Результат вызова функции get_stock_prices:", prices)
