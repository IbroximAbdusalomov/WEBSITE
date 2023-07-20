from aiogram import types
from aiogram.dispatcher.filters import Text
from asgiref.sync import sync_to_async

from films.bot.loader import bot, dp
from films.models import Films


@dp.callback_query_handler(Text(startswith='button1_'))
async def process_start_command(call: types.CallbackQuery):
    message = await activate(call.data[8:])
    await call.message.reply(message)


@dp.callback_query_handler(Text(startswith='button2_'))
async def process_start_command(call: types.CallbackQuery):
    message = await dis_activate(call.data[8:])
    await call.message.reply(message)


@sync_to_async
def activate(id):
    text = Films.objects.get(pk=id)
    text.is_active = True
    text.save()
    return f'Success {id}'


@sync_to_async
def dis_activate(id):
    print(id)
    # text = Films.objects.get(pk=id)
    # text.is_active = True
    # text.save()
    # text.delete()
    return f'Deleted {id}'
