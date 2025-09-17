import asyncio
import logging
import random
from typing import Callable, Any, Optional, Coroutine, Tuple, Dict, Type
from aiogram.exceptions import TelegramRetryAfter

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
        except TelegramRetryAfter as e:
            wait = e.retry_after + random.uniform(0.2, 0.5)
            logging.warning(f"Flood control: ждём {wait} сек")
            await asyncio.sleep(wait)
        except exceptions as e:
            logging.warning(f"[Retry] Ошибка при попытке {attempt}: {e}")
            if attempt == retries:
                logging.error(f"[Retry] Все {retries} попыток исчерпаны, ошибка не устранена.")
                raise
            logging.info(f"[Retry] Ждём {delay:.2f} сек перед повторной попыткой...")
            await asyncio.sleep(delay)
            delay *= factor
