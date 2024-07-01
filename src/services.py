import datetime
import json
import logging
import os

from config import LOGS_DIR

# logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("services")
logger.setLevel(logging.INFO)


log_file = os.path.join(LOGS_DIR, "services.log")
print(log_file)


file_handler = logging.FileHandler(log_file)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def analyze_cashback_categories(transactions: list[dict], year: int, month: int) -> str:
    """Анализ категорий кэшбэка."""
    logger.info("Начало анализа кэшбэка для года %d и месяца %d", year, month)
    cashback_summary = {}
    for transaction in transactions:
        date = datetime.datetime.strptime(transaction["Дата операции"], '%Y-%m-%d %H:%M:%S')
        if date.year == year and date.month == month:
            category = transaction["Категория"]
            cashback = transaction["Кешбэк"]
            if category not in cashback_summary:
                cashback_summary[category] = 0
            cashback_summary[category] += cashback
            logger.debug("Обновление категории %s: %f", category, cashback_summary[category])

    return json.dumps(cashback_summary, ensure_ascii=False, indent=4)
