import os
from aiogram import executor, Dispatcher, types
from aiogram.types import Message, CallbackQuery
from db.db import engine, session
from handlers.handlers import add_description_handler, get_by_id_handler, move_object_handler, \
    show_object_moving_handler, add_id_handler, add_geolocation_handler, search_1c
from keyboards.keyboards import add_technic_keyboard, status_keyboard
from models.models import User, Base, LogItem
from static_data import main_folder, bot
from utils.set_bot_commands import check_if_admin

# диспетчер для обработки команд боту
dispatcher = Dispatcher(bot)

# создание бд если ее нет
Base.metadata.create_all(engine)

print("Бот запущен")

# сохраняем значения введенные пользователем в бота
state = {}

# действие при команде старт - проверка пользователя - приветственное сообщение
@dispatcher.message_handler(commands=['start'])
async def command_start(message: Message):
    if check_if_admin(message.chat.id):
        user = session.query(User).filter(User.chat_id == message.chat.id).all()
        if len(user) == 0:
            user = User(chat_id=message.chat.id)
            session.add(user)
            session.commit()
        state[message.chat.id] = {'state': 'start'}
        await message.answer(f'Привет {message.from_user.full_name}! Твой айди: {message.from_user.id}\n'
                             f'Это бот для учета активов на складе RC MAIN office \n')
    else:
        await message.answer("Тебя нет в списке пользователей ботом, либо ты еще не ввел команду: /start")


# диспетчер который ловит команду - add_technics
@dispatcher.message_handler(commands=['add_technics'])
async def add_technics(message: Message):
    await bot.send_message(message.chat.id, "Выбери категорию", reply_markup=add_technic_keyboard())


# диспетчер который ловит команду - add_laptop
@dispatcher.callback_query_handler(text='add_laptop')
async def add_laptop(call_back: CallbackQuery):
    state[call_back.message.chat.id] = {'state': 'send_id', "category": 'ноутбук'}
    await bot.send_message(call_back.message.chat.id, "Введи ID")


# диспетчер который ловит команду - add_pc
@dispatcher.callback_query_handler(text='add_pc')
async def add_pc(call_back: CallbackQuery):
    state[call_back.message.chat.id] = {'state': 'send_id', "category": 'компьютер'}
    await bot.send_message(call_back.message.chat.id, "Наведи камеру на QR, получи ID актива и впиши его сюда")


@dispatcher.callback_query_handler(text='add_server')
async def add_server(call_back: CallbackQuery):
    state[call_back.message.chat.id] = {'state': 'send_id', "category": 'сервер'}
    await bot.send_message(call_back.message.chat.id, "Введи ID")


@dispatcher.callback_query_handler(text='given')
async def given(call_back: CallbackQuery):
    state[call_back.message.chat.id]['state'] = 'add_contact_mail'
    await bot.send_message(call_back.message.chat.id, "Введите почту ответственного")


# диспетчер который ловит команду - нет. после вопроса о желании добавить местоположение
# если пользователь нажал нет - то, ему просто выдастся информация о заведенном актива
@dispatcher.callback_query_handler(text='hold')
async def hold(call_back: CallbackQuery):
    await add_geolocation_handler(bot, state, call_back=call_back)


@dispatcher.callback_query_handler(text='add_other')
async def add_other(call_back: CallbackQuery):
    state[call_back.message.chat.id] = {'state': 'send_id', "category": 'другое'}
    await bot.send_message(call_back.message.chat.id, "Введи ID")


# диспетчер который добавляет фото
@dispatcher.message_handler(content_types=types.ContentType.PHOTO)
async def picture_download(message: Message):
    if state[message.chat.id]["state"] in ['send_first_photo', 'send_second_photo']:
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        photo = await bot.download_file(file_path)
        dir_list = os.listdir(main_folder)
        if "photos" not in dir_list:
            os.mkdir(os.path.join(main_folder, "photos"))
        photos_dir_list = os.listdir(os.path.join(main_folder, "photos"))
        if f'{state[message.chat.id]["technic_id"]}' not in photos_dir_list:
            os.mkdir(os.path.join(main_folder, "photos", state[message.chat.id]["technic_id"]))
        if "photo.jpg" not in os.listdir(os.path.join(main_folder, "photos", state[message.chat.id]["technic_id"])) and \
                state[message.chat.id]['category'] != 'другое':
            with open(os.path.join(main_folder, "photos", state[message.chat.id]["technic_id"], "photo.jpg"),
                      'wb') as f:
                f.write(photo.read())
            state[message.chat.id]['state'] = 'send_second_photo'
            await bot.send_message(message.chat.id, 'пришлите фото техники целиком')
        else:
            with open(os.path.join(main_folder, "photos", state[message.chat.id]["technic_id"], "photo_1.jpg"), 'wb') as f:
                f.write(photo.read())
            state[message.chat.id]['state'] = 'add_model'
            await bot.send_message(message.chat.id, 'пришли номер техники')
            await bot.send_message(message.chat.id, 'пример: pc10001')
    else:
        await bot.send_message(message.chat.id, "Вы прислали фото, но не выбрали что с ним сделать")


@dispatcher.message_handler(commands=['get_by_id'])
async def get_by_id(message: Message):
    if message.chat.id not in state.keys():
        state[message.chat.id] = {'state': 'get_by_id'}
    else:
        state[message.chat.id]['state'] = 'get_by_id'
    await bot.send_message(message.chat.id, "Введите ID техники")


@dispatcher.message_handler(commands=['get_from_1c'])
async def get_from_1c(message: Message):
    if message.chat.id not in state.keys():
        state[message.chat.id] = {'state': 'get_from_1c'}
    else:
        state[message.chat.id]['state'] = 'get_from_1c'
    await bot.send_message(message.chat.id, "Введите ID техники")


@dispatcher.message_handler(commands=['move_object'])
async def move_object(message: Message):
    if message.chat.id not in state.keys():
        state[message.chat.id] = {'state': 'move_object'}
    else:
        state[message.chat.id]['state'] = 'move_object'
    await bot.send_message(message.chat.id,
                           'введите через запятую: ID актива, почта ответственного, место куда отправляется актив')
    await bot.send_message(message.chat.id,
                           'пример: 0101010101, nikolay.melnik@rencons.com, Санкт-Петербург')


@dispatcher.message_handler(commands=['show_object_moving'])
async def show_object_moving(message: Message):
    if message.chat.id not in state.keys():
        state[message.chat.id] = {'state': 'show_object_moving'}
    else:
        state[message.chat.id]['state'] = 'show_object_moving'
    await bot.send_message(message.chat.id, "введите ID актива")


@dispatcher.message_handler()
async def handlers(message: Message):
    if message.chat.id in state.keys():
        if state[message.chat.id]['state'] == 'add_geolocation':
            state[message.chat.id]['place'] = message.text
            await bot.send_message(message.chat.id, "выберите статус", reply_markup=status_keyboard())
        if state[message.chat.id]['state'] == 'send_id':
            await add_id_handler(bot, message, state)
        if state[message.chat.id]['state'] == 'add_description':
            await add_description_handler(bot, message, state)
        if state[message.chat.id]['state'] == 'add_model':
            state[message.chat.id]['state'] = 'add_description'
            state[message.chat.id]['model'] = message.text
            await bot.send_message(message.chat.id, "Введите базовые характеристики (марка, CPU, RAM, HDD(SSD))")
        if state[message.chat.id]['state'] == 'get_by_id':
            await get_by_id_handler(bot, message)
        if state[message.chat.id]['state'] == 'get_from_1c':
            await search_1c(bot, message)
        if state[message.chat.id]['state'] == 'move_object':
            await move_object_handler(bot, message)
        if state[message.chat.id]['state'] == 'show_object_moving':
            await show_object_moving_handler(bot, message)
        if state[message.chat.id]['state'] == 'add_contact_mail':
            await add_geolocation_handler(bot, state, message=message)
    else:
        await bot.send_message(message.chat.id, "я не понимаю")


executor.start_polling(dispatcher, skip_updates=True)
