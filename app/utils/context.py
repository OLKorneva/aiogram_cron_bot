from contextvars import ContextVar
from aiogram import Bot, Dispatcher

bot_var: ContextVar[Bot] = ContextVar("bot")
dp_var: ContextVar[Dispatcher] = ContextVar("dp")
