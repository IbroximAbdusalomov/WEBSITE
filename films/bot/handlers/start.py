from aiogram import types
from aiogram.dispatcher.filters import Text
from asgiref.sync import sync_to_async

from accounts.models import Message
from accounts.utils import false_account_status, true_account_status
from films.bot.loader import dp
from films.models import Products


@dp.callback_query_handler(Text(startswith='button1_'))
async def process_start_command(call: types.CallbackQuery):
    message = await activate(call.data.replace("button1_", ""))
    await call.message.reply(message)


@dp.callback_query_handler(Text(startswith='button2_'))
async def process_start_command(call: types.CallbackQuery):
    message = await dis_activate(call.data.replace("button2_", ""))
    await call.message.reply(message)


@dp.callback_query_handler(Text(startswith='activate_company_'))
async def process_start_command(call: types.CallbackQuery):
    message = await activate_company(call.data.replace("activate_company_", ""))
    await call.message.reply(message)


@dp.callback_query_handler(Text(startswith='dis_activate_company_'))
async def process_start_command(call: types.CallbackQuery):
    message = await dis_activate_company(call.data.replace("dis_activate_company_", ""))
    await call.message.reply(message)


@sync_to_async
def activate(id):
    text = Products.objects.get(pk=id)
    text.is_active = True
    text.save()
    return f'Success {id}'


@sync_to_async
def dis_activate(id):
    product = Products.objects.get(pk=id)
    user = Message.objects.create(sender_id=1, message=f"Ваш продукт не прошёл модерацию.  пост -> {product.title}")
    user.recipients.add(product.author_id)
    user.save()

    return f'Deleted {id}'


@sync_to_async
def activate_company(pk):
    return true_account_status(pk)


@sync_to_async
def dis_activate_company(pk):
    return false_account_status(pk)
