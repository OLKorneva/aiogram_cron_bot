import asyncio
import logging
from typing import Callable, Any, Optional, Coroutine, Tuple, Dict, Type

async def retry_async(
    func: Callable[..., Coroutine[Any, Any, Any]],
    *args,
    retries: int = 5,
    base_delay: float = 0.5,
    factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    **kwargs
) -> Any:
    """
    Универсальный ретрай для любой асинхронной функции.

    Параметры:
        func: Асинхронная функция, которую нужно выполнить
        args, kwargs: Аргументы для функции
        retries: Количество попыток
        base_delay: Начальная задержка перед повтором
        factor: Множитель задержки (экспоненциальная задержка)
        exceptions: Кортеж исключений, при которых делаем повтор
    """
    delay = base_delay
    for attempt in range(1, retries + 1):
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            logging.warning(f"[Retry] Ошибка при попытке {attempt}: {e}")
            if attempt == retries:
                logging.error(f"[Retry] Все {retries} попыток исчерпаны, ошибка не устранена.")
                raise
            logging.info(f"[Retry] Ждём {delay:.2f} сек перед повторной попыткой...")
            await asyncio.sleep(delay)
            delay *= factor

import asyncio
import logging
from functools import wraps
from aiogram.exceptions import TelegramNetworkError
from aiogram.client.errors import RetryAfter
from aiohttp import ClientConnectorError

def retry_for_telegram(max_attempts: int = 5, initial_delay: float = 0.5, backoff: float = 2.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except RetryAfter as e:
                    wait = getattr(e, "timeout", None) or delay
                    logging.warning(f"{func.__name__}: Получен RetryAfter, ждем {wait:.1f} сек")
                    await asyncio.sleep(wait)
                except (TelegramNetworkError, ClientConnectorError, asyncio.TimeoutError) as e:
                    logging.warning(f"{func.__name__}: Попытка {attempt}/{max_attempts} не удалась: {e}")
                    if attempt == max_attempts:
                        logging.error(f"{func.__name__}: Все попытки исчерпаны")
                        raise
                    await asyncio.sleep(delay)
                    delay *= backoff
        return wrapper
    return decorator
