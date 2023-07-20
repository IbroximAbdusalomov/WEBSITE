import logging

from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.forms import model_to_dict

from Technoprom.settings import TOKEN, chat_id

logging.basicConfig(level=logging.INFO)

bot_token = TOKEN
chat_id = chat_id
bot = Bot(token=bot_token)
dp = Dispatcher(bot)


async def send_message_to_bot(msg, cat1, cat2):
    msg = model_to_dict(msg)
    message = f"*TYPE: {msg.get('type')}\n*" \
              f"title:          {msg.get('title')}\ndescription:    {msg.get('description')}\n" \
              f"telephone:      {msg.get('telephone')}\nemail:          {msg.get('email')}\n" \
              f"category:       {cat1}\nsub_category:   {cat2}\n"
    film_id = msg.get('id')
    inline_btn_1 = InlineKeyboardButton('👍', callback_data=f'button1_{film_id}')
    inline_btn_2 = InlineKeyboardButton('👎', callback_data=f'button2_{film_id}')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
    await bot.send_message(chat_id, message, reply_markup=inline_kb1)


async def send_message_to_channel(message):
    await bot.send_message(chat_id=chat_id, text=message)
