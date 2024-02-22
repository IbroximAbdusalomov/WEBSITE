import logging
import environ
from aiogram import Bot, Dispatcher, types

logging.basicConfig(level=logging.INFO)

env = environ.Env()
environ.Env.read_env()

TOKEN = env("TOKEN")
CHAT_ID = env("CHAT_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


async def send_message_to_channel(message, image=None):
    tags = message.get('tags', [])
    subcategories = message.get('subcategory', [])
    film_id = message['film_id']
    # Extract tag names as strings
    subcategory_names = [str(subcategory) for subcategory in subcategories]
    tag_names = [str(tag) for tag in tags]

    # Initialize the message text with common fields
    formatted_message = (
        f"*Новый запрос*\n"
        f"📌 *Заголовок*: {message['title']}\n"
        f"📝 *Описание*: {message['description']}\n"
        f"📅 *Категория*: {message['category']}\n"
        f"🏷️ *Субкатегория*: {', '.join(subcategory_names)}\n"
        f"🏷️ *Теги*: {', '.join(tag_names)}\n"
        f"🌐 *Страна*: {message['country']}\n"
        f"🌆 *Город*: {message['city']}\n"
        f"📞 *Телефон*: {message['telephone']}\n"
        f"📞 *Телеграм*: {message['telegram']}\n"
        f"📋 *Тип*: {message['тип']}\n"
    )

    # Check if there is a price, if not, include "Договорная"
    if message['is_price_negotiable']:
        formatted_message += "💰 *Цена*: Договорная\n"
    else:
        formatted_message += f"💰 *Цена*: {message['price']}\n"

    inline_btn_1 = types.InlineKeyboardButton('👍', callback_data=f'button1_{film_id}')
    inline_btn_2 = types.InlineKeyboardButton('👎', callback_data=f'button2_{film_id}')
    inline_kb = types.InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)

    if image:
        with open(image, "rb") as image_file:
            await bot.send_photo(CHAT_ID, image_file, caption=formatted_message, reply_markup=inline_kb,
                                 parse_mode="markdown")
    else:
        await bot.send_message(CHAT_ID, formatted_message, reply_markup=inline_kb, parse_mode="markdown")
