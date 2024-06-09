import asyncio
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.types import Message,CallbackQuery
from aiogram.filters import CommandStart,Command
from aiogram import F

from decouple import config

from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton,ReplyKeyboardMarkup,KeyboardButton

from aiogram.types import CallbackQuery, InputFile,FSInputFile
from kbds import *
from dishes import *
import io


TOKEN = '6987837708:AAE9HL1ny0VLSFj2E6LvaCyyM23bh4F9oVI'

bot = Bot(TOKEN)


dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message,state:FSMContext):
    await message.answer("Выберите язык", reply_markup=set_language.as_markup())

@dp.callback_query(lambda query: query.data.startswith('lang_'))
async def set_lang(callback:CallbackQuery,state:FSMContext):
    await state.update_data(language=callback.data[-2:])
    data = await state.get_data()
    if data['language'] == 'RU':
        await callback.message.answer(text = 'Вы сменили язык на Русский',reply_markup = default_kb_ru)
    else:
        await callback.message.answer(text = 'You changed the language to English',reply_markup = default_kb_en)

@dp.message(F.text.in_({'Сменить язык','Switch language'}))
async def swaitch_lang(message:Message,state:FSMContext):
    await start(message,state)

@dp.message(F.text.in_({'🔎Блюда','🔎Dishes'}))
async def g_dish(message,state):
    data  = await state.get_data()
    lang = data.get('language')

    if lang == 'RU':
        await message.answer(text = 'Выберите блюдо',reply_markup = dishes_kb_ru.as_markup())
    else:
        await message.answer(text = 'Choose dish',reply_markup = dishes_kb_en.as_markup())


@dp.callback_query(lambda query: query.data.startswith('send_'))
async def send_dish(callback,state):
    data = await state.get_data()
    lang = data.get('language')
    if lang == 'RU':
        if callback.data[5:] == 'soup':
            img,data = pretty_dish(d2_ru,'ru')
        if callback.data[5:] == 'kasha':
            img,data = pretty_dish(d1_ru,'ru')
        if callback.data[5:] == 'pancakes':
            img,data = pretty_dish(d3_ru,'ru')
    else:
        if callback.data[5:] == 'soup':
            img,data = pretty_dish(d2_en,'en')
        if callback.data[5:] == 'kasha':
            img,data = pretty_dish(d1_en,'en')
        if callback.data[5:] == 'pancakes':
            img,data = pretty_dish(d3_en,'en')
    
    # Создание объекта InputFile из байтов данных
    photo = FSInputFile(img)
    await bot.send_photo(callback.message.chat.id,photo=photo)
    # print(photo.read())
    # await callback.message.text(img)


@dp.message(F.text.in_({'Помощь','Help'}))
async def help_func(message:Message,state:FSMContext):
    data = await state.get_data()
    lang = data.get('language')
    if lang == 'RU':
        await message.answer(text = 'Для помощи обратитесь по номеру: 996500448877')
    else:
        await message.answer(text = 'For assistance, please call: 996500448877')




async def main():
    await dp.start_polling(bot)

asyncio.run(main())