import logging

from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.forms import model_to_dict

from root.settings import TOKEN, chat_id

logging.basicConfig(level=logging.INFO)

bot_token = TOKEN
chat_id = chat_id
bot = Bot(token=bot_token)
dp = Dispatcher(bot)


async def send_message_to_channel(message, image=None):
    tags = message.get('tags', [])

    # Extract tag names as strings
    tag_names = [str(tag) for tag in tags]
    formatted_message = (
        f"*Новый запрос*\n"
        f"📌 *Заголовок*: {message['title']}\n"
        f"📝 *Описание*: {message['description']}\n"
        f"📅 *Категория*: {message['category']}\n"
        f"🏷️ *Субкатегория*: {message['sub_category']}\n"
        f"🌐 *Страна*: {message['country']}\n"
        f"🌆 *Город*: {message['city']}\n"
        f"🏷️ *Теги*: {', '.join(tag_names)}\n"
        f"📞 *Телефон*: {message['telephone']}\n"
        f"📋 *Тип*: {message['тип']}\n"  # Include the type field
    )
    # inline_btn_1 = InlineKeyboardButton('👍', callback_data=f'button1_{film_id}')
    # inline_btn_2 = InlineKeyboardButton('👎', callback_data=f'button2_{film_id}')
    # inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
    # await bot.send_message(chat_id=chat_id, text=message, reply_markup=inline_kb1)
    if image:
        await bot.send_photo(chat_id=chat_id, photo=image, caption=formatted_message, parse_mode="markdown")
    else:
        await bot.send_message(chat_id=chat_id, text=formatted_message, parse_mode="markdown")
