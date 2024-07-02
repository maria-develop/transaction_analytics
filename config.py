import os

# Корневая директория проекта
ROOT_DIR = os.path.dirname(__file__)

# Директория для логов
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')

# Создание каталога для логов, если он не существует
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
