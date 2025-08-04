from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


class TimeFilter(BaseFilter):
    def __init__(self, times: list[str]):
        self.times = times

    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data in self.times