import logging
from aiogram import Bot, types
from Technoprom.settings import TOKEN
from aiogram.dispatcher import Dispatcher

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
