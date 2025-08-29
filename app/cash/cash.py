import json
import os
import logging

CACHE_FILE = "app/cash/cache.json"
messages_meta: dict = {}  # глобальный словарь для всего проекта

def load_cache():
    """
    Загружает кеш из JSON в существующий словарь messages_meta.
    Важно: обновляем словарь через clear() и update(), чтобы ссылки в других модулях оставались корректными.
    """
    global messages_meta
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            messages_meta.clear()
            messages_meta.update(data)
        logging.info("Кеш загружен из cache.json")
    else:
        messages_meta.clear()
        logging.warning("Файл кеша cache.json не найден, словарь пустой")

def save_cache():
    """
    Сохраняет текущий словарь messages_meta в JSON.
    """
    global messages_meta
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(messages_meta, f, ensure_ascii=False, indent=2)
        logging.info("Кеш сохранен в cache.json")
