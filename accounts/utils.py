import logging

from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from django.contrib.auth import get_user_model

from root.settings import TOKEN, chat_id
from .models import Message

logging.basicConfig(level=logging.INFO)
bot_token = TOKEN
chat_id = chat_id
bot = Bot(token=bot_token)
dp = Dispatcher(bot)
User = get_user_model()


async def send_message(user_id, amount, photo):
    inline_kb = [
        InlineKeyboardButton(text="Добавить", callback_data=f"+"),
        InlineKeyboardButton(text="Перейти", callback_data="-"),
        # InlineKeyboardButton(text="Перейти", url="http://localhost:8000/"),
    ]

    message = f"""
    User id: {user_id}

    Amount: {amount}


    """

    inline_query = InlineKeyboardMarkup(row_width=1).row(*inline_kb)
    # with open(photo, "rb"):
    await bot.send_photo(
        chat_id=chat_id,
        photo=InputFile(photo.file),
        reply_markup=inline_query,
        caption=amount,
    )


async def send_message_to_channel(message_data, pk):
    message = f"Новая компания зарегистрирована:\n{pk}\n\n"
    for key, value in message_data.items():
        if key == "Website" or key == "URL Maps":
            if value:
                message += f"*{key}:* [{key}]({value})\n"
        else:
            if value:
                message += f"*{key}:* {value}\n"

    # buttons = [
    inline_kb1 = InlineKeyboardButton(
        text="Активировать", callback_data=f"activate_company_{pk}"
    )
    inline_kb2 = InlineKeyboardButton(
        text="Деактивировать", callback_data=f"dis_activate_company_{pk}"
    )
    # ]
    inline_kb = InlineKeyboardMarkup().add(inline_kb1, inline_kb2)

    await bot.send_message(
        chat_id=chat_id, text=message, parse_mode="markdown", reply_markup=inline_kb
    )


def false_account_status(pk: int):
    account = User.objects.get(pk=pk)
    account.is_business_account = False
    account.save()
    user = Message.objects.create(
        sender_id=1, message=f"Ваш запрос на бизнес аккаунт был принят"
    )
    user.recipients.add(pk)
    user.save()
    return "status false"


def true_account_status(pk: int):
    account = User.objects.get(pk=pk)
    account.is_business_account = True
    account.save()
    user = Message.objects.create(
        sender_id=1, message=f"Ваш запрос на бизнес аккаунт был отклонен"
    )
    user.recipients.add(pk)
    user.save()
    return "status true"
