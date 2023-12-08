import logging

from aiogram import Bot
from aiogram.dispatcher import Dispatcher

from root.settings import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
