from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def add_technic_keyboard():
    button1 = InlineKeyboardButton(text='Ноутбук', callback_data='add_laptop')
    button2 = InlineKeyboardButton(text='Компьютер', callback_data='add_pc')
    button3 = InlineKeyboardButton(text='Сервер', callback_data='add_server')
    button4 = InlineKeyboardButton(text='Другое', callback_data='add_other')
    keyboard = InlineKeyboardMarkup()
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    keyboard.add(button4)
    return keyboard


def status_keyboard():
    button1 = InlineKeyboardButton(text='хранение', callback_data='hold')
    button2 = InlineKeyboardButton(text='выдан', callback_data='given')
    keyboard = InlineKeyboardMarkup()
    keyboard.add(button1)
    keyboard.add(button2)
    return keyboard


