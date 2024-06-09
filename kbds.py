from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton,ReplyKeyboardMarkup,KeyboardButton


set_language = InlineKeyboardBuilder(
    markup=[
        [InlineKeyboardButton(text = '🇷🇺',callback_data='lang_RU'),
        InlineKeyboardButton(text = '🇺🇸',callback_data='lang_EN')]
])

def get_lang_kb(current_lang):
    if current_lang == 'RU':
        flag = '🇺🇸'
        new_lang = '🇺🇸'
    else:
        flag = '🇷🇺'
        new_lang = 'RU'
    kb = InlineKeyboardButton(text = f'Переключить язык на {flag}',callback_data = f'switch_language_{new_lang}')
    return kb


default_kb_ru = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = '🔎Блюда'),
            KeyboardButton(text = 'Сменить язык'),
            
        ],
        [
            KeyboardButton(text = 'Помощь'),
        ]
    ],
    resize_keyboard=True
)
default_kb_en = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = '🔎Dishes'),
            KeyboardButton(text = 'Switch language'),
            
        ],
        [
            KeyboardButton(text = 'Help'),
        ]
    ],
    resize_keyboard=True
)

dishes_kb_ru = InlineKeyboardBuilder(
    markup = [
        [InlineKeyboardButton(text = 'Каша',callback_data = 'send_kasha'),
        InlineKeyboardButton(text = 'Суп',callback_data = 'send_soup'),
        InlineKeyboardButton(text = 'Блины',callback_data = 'send_pancakes'),]
    ]
)
dishes_kb_en = InlineKeyboardBuilder(
    markup = [
        [InlineKeyboardButton(text = 'Porridge',callback_data = 'send_kasha'),
        InlineKeyboardButton(text = 'Soup',callback_data = 'send_soup'),
        InlineKeyboardButton(text = 'Pancakes',callback_data = 'send_pancakes'),]
    ]
)

